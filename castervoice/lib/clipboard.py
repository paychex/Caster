import re

from dragonfly import Clipboard as DragonflyClipboard
from castervoice.lib import printer, settings

def _is_aenea_available():
    try:
        import aenea
        return True
    except ImportError:
        print("Unable to import aenea, castervoice.lib.clipboard.ExtendedClipboard will be used instead.")
        return False

"""
Extended clipboard that allows using multiple indexes
"""
class ExtendedClipboard(DragonflyClipboard):
    SAVED_CLIPBOARD_PATH = settings.settings([u'paths', u'SAVED_CLIPBOARD_PATH'])

    # TODO fix circular import
    #from castervoice.lib import utilities
    #utilities.load_json_file(settings.settings(["paths", "SAVED_CLIPBOARD_PATH"]))
    _clip = {}

    def __init__(self, contents=None, text=None, from_system=False):
        super(ExtendedClipboard, self).__init__(contents=contents, text=text, from_system=from_system)

    # This will allow commands like 'stoosh' to work properly server-side if the RPC functions are availablefrom 
    if settings.settings(["miscellaneous", "use_aenea"]) and _is_aenea_available():
        # pylint: disable=import-error
        import aenea
        from jsonrpclib import ProtocolError

        @classmethod
        def get_system_text(cls):
            # Get the server's clipboard content if possible and update this
            # system's clipboard.
            try:
                server_text = aenea.communications.server.paste()
                DragonflyClipboard.set_system_text(server_text)
                return server_text
            except ProtocolError as e:
                print("ProtocolError caught when calling server.paste(): %s" % e)
                print("Only getting local clipboard content.")
                return DragonflyClipboard.get_system_text()

        @classmethod
        def set_system_text(cls, content):
            # Set the server's clipboard content if possible.
            try:
                aenea.communications.server.copy(content)
            except ProtocolError as e:
                print("ProtocolError caught when calling server.copy(): %s" % e)
                print("Only setting local clipboard content.")

            # Set this system's clipboard content.
            DragonflyClipboard.set_system_text(content)

    @classmethod
    def save_clipboard(cls): 
        # TODO fix circular import
        #from castervoice.lib import utilities
        #utilities.save_json_file(_CLIP, settings.settings([u'paths', u'SAVED_CLIPBOARD_PATH']))
        print("SAVE CLIP")
        print(clip)
        pass

    def copy_from_system(self, clear=False, index=1):
        key = self._key(index)
        if key == "1":
            super(ExtendedClipboard, self).copy_from_system(clear)
        else:
            self.set_text(self.get_system_text(), index)

            if clear:
                # Clears the system clipboard
                self.clear_clipboard()

    def copy_to_system(self, index=1):
        key = self._key(index)
        if key == "1":
            super(ExtendedClipboard, self).copy_to_system()
        else:
            content = self.get_text(key)
            self.set_system_text(content)

    def has_text(self, index=1):
        key = self._key(index)
        if key == "1":
            return super(ExtendedClipboard, self).has_text()
        else:
            return key in _clip and _clip[key] is not None

    def get_text(self, index=1):
        key = self._key(index)
        if key == "1":
            return super(ExtendedClipboard, self).get_text()
        else:
            return _clip.get(key)

    def set_text(self, content, index=1):
        key = self._key(index)
        if key == "1":
            super(ExtendedClipboard, self).set_text(content)
        else:
            if key is None:
                _clip.pop(key, None)
            else:
                _clip[key] = content
            self.save_clipboard()

    def clear_text(self, index=1):
        self.set_text(None, index)

    def clear_all_text(self):
        self.clear_text(1)

        _clip = {}
        self.save_clipboard()

    def _key(self, obj):
        key = str(obj)

        if obj is None or not re.match('^\\w+$', key):
            raise ValueError("Clipboard key must be alphanumeric")

        return key

    
Clipboard = ExtendedClipboard