# Copyright (C) 2018, Vladimir Shapranov 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


import logging

class BaseDecoderPlugin:
    def load_config(self, fn):
        pass

    def check_message(self, msg):
        raise NotImplementedError()

    def decode_message(self, msg):
        raise NotImplementedError()

class ReprDecoderPlugin(BaseDecoderPlugin):
    def __init__(self):
        self.cache = {}

    def check_message(self, msg):
        print("Checking message %r" % msg)
        return True
    
    def decode_message(self, msg):
        print("Decoding message...")
        logging.warning("pl: %s")
        return True, repr(msg)

class DecoderMaster(BaseDecoderPlugin):
    def __init__(self):
        self.children = []

    def check_message(self, msg):
        for i in self.children:
            if i.check_message(msg):
                return True
        return False

    def decode_message(self, msg):
        for i in self.children:
            if i.check_message(msg):
                return i.decode_message(msg)
        return False, ''
decoder = DecoderMaster()
decoder.children.append(ReprDecoderPlugin())