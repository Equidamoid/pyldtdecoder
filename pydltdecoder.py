# Copyright (C) 2018-2019, Vladimir Shapranov 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


import logging
import dltpy.dltfile
import debus.marshalling



class BaseDecoderPlugin:
    def load_config(self, fn):
        pass

    def check_message(self, msg):
        """ 
        Check whether this plugin should be used to decode the message"
        """
        raise NotImplementedError()

    def decode_message(self, msg):
        """
        Decode the message, return a tuple: `(bool, str)`
        the bool determines if the message should be displayed
        the str is the message to be displayed
        """
        raise NotImplementedError()

class ReprDecoderPlugin(BaseDecoderPlugin):
    def __init__(self):
        self.cache = {}

    def check_message(self, msg):
        logging.info("Checking message %r", msg)
        return True
    
    def decode_message(self, msg):
        logging.warning("app: %r, ctx: %r, ts: %d, payload: %r", msg['app'], msg['ctx'], msg['ts'], msg['pl'])
        pl = dltpy.dltfile.parse_payload(msg['pl'])
        return True, repr(pl)

class DBusDecoderPlugin(BaseDecoderPlugin):

    formats = {
        debus.MessageType.METHOD_CALL: '[0x{msg.serial:x}] M {msg.path} {msg.interface}.{msg.member} {msg.payload}',
        debus.MessageType.METHOD_RETURN: '[0x{msg.serial:x}] R (0x{msg.reply_serial:x}) {msg.payload}',
        debus.MessageType.ERROR: '[0x{msg.serial:x}] E (0x{msg.reply_serial:x}) {msg.payload}',
        debus.MessageType.SIGNAL: '[0x{msg.serial:x}] M {msg.path} {msg.interface}.{msg.member} {msg.payload}',
        debus.MessageType.METHOD_CALL: '[0x{msg.serial:x}] M {msg.path} {msg.interface} {msg.member} {msg.payload}',
        debus.MessageType.INVALID: '[INVALID]',
    }
    def __init__(self):
        self.cache = {}
        self.segmented = {}
        self.segmented_cache = {}

    def check_message(self, msg):
        return msg['app'] in ('DBSE', 'DBSY') and msg['ctx'] in ('DIN', 'DOUT')
    
    def decode_message(self, msg):
        pl = dltpy.dltfile.parse_payload(msg['pl'])
        if pl[0] == b'NWST':
            return False, ''
        if pl[0] == b'NWCH':
            s_id = pl[1]
            if not s_id in self.segmented_cache:
                self.segmented.setdefault(s_id, b'')
                self.segmented[s_id] += pl[3]
            return True, '[segmented] %d bytes' % len(pl[3])
        elif pl[0] == b'NWEN':
            s_id = pl[1]
            if s_id in self.segmented_cache:
                dbus_pl = self.segmented_cache[s_id]
            else:
                dbus_pl = self.segmented[s_id]
                self.segmented_cache[s_id] = dbus_pl
                del self.segmented[pl[1]]
            
        else:
            dbus_pl = pl[1]
        
        try:
            msg = debus.marshalling.read_message(dbus_pl)
        except Exception as ex:
            logging.exception('')
            return True, '%s %r' % (ex, pl)
        assert(len(msg) == 1)
        msg = msg[0]
        
        ret = '[%5d:%5s] %s %s %s.%s %r' % (
            msg.serial,
            msg.reply_serial if msg.message_type in (debus.MessageType.METHOD_RETURN, debus.MessageType.ERROR) else 'N/A',
            msg.message_type.name,
            msg.path,
            msg.interface,
            msg.member,
            msg.payload,
        )
        ret = self.formats.get(msg.message_type, '{msg}').format(msg=msg)
        return True, ret

class DecoderMaster(BaseDecoderPlugin):
    def __init__(self):
        self.children = []

    def check_message(self, msg):
        try:
            for i in self.children:
                if i.check_message(msg):
                    return True
        except:
            logging.exception('')
        return True

    def decode_message(self, msg):
        try:
            for i in self.children:
                if i.check_message(msg):
                    return i.decode_message(msg)
        except Exception as ex:
            logging.exception('')
            return True, str(ex)
        return False, ''

# Create an instance of your decoder and put it to a global variable named "decoder"

decoder = DecoderMaster()
decoder.children.append(DBusDecoderPlugin())
decoder.children.append(ReprDecoderPlugin())

