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
    def __init__(self):
        self.cache = {}

    def check_message(self, msg):
        return msg['app'] in ('DBSE', 'DBSY') and msg['ctx'] in ('DIN', 'DOUT')
    
    def decode_message(self, msg):
        #logging.warning("app: %r, ctx: %r, ts: %d, payload: %r", msg['app'], msg['ctx'], msg['ts'], msg['pl'])
        pl = dltpy.dltfile.parse_payload(msg['pl'])
        dbus_pl = pl[1]
        
        msg = debus.marshalling.read_message(dbus_pl)
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
        return False

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

