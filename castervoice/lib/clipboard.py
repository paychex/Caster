import re

from dragonfly import Clipboard as DragonflyClipboard
from castervoice.lib import printer, utilities, settings

def _is_aenea_available():
    try:
        import aenea
        return True
    except ImportError:
        print("Unable to import aenea, castervoice.lib.clipboard.ExtendedClipboard will be used instead.")
        return False

"""
Virtual in-memory clipboard that supports more than 1 slot.

Text from the system must be explicitly read and written from and to the system clipboard. Data can be synchzronized 
between this virtual clipboard and the system clipboard using copy_from_system and copy_to_system.

Persisting and loading the virtual clipboards contents can be achieved using the save() and load() methods
"""
class ExtendedClipboard(DragonflyClipboard):
    def __init__(self, contents=None, text=None, from_system=False):
        super(ExtendedClipboard, self).__init__(contents=contents, text=text, from_system=from_system)

        self._clip = { }

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

    def copy_from_system(self, clear=False, slot=1):
        """
        Reads the system clipboard contents into the specified slot of this virtual clipboard instance.

        Contents of the system clipboard are read into slot 1.
        Contents on disk are read into other slots.
        """
        key = self._key(slot)
        if key == "1":
            super(ExtendedClipboard, self).copy_from_system(clear)
        else:
            self.set_text(self.get_system_text(), slot)

            if clear:
                # Clears the system clipboard
                self.clear_clipboard()

    def copy_to_system(self, slot=1):
        """
        Writes the contents in the specified slot of this virtual clipboard instance to the system clipboard
        """
        key = self._key(slot)
        if key == "1":
            super(ExtendedClipboard, self).copy_to_system()
        else:
            content = self.get_text(key)
            self.set_system_text(content)

    def has_text(self, slot=1):
        """
        Returns if this virtual clipboard has contents loaded at the specifed slot.
        """
        key = self._key(slot)
        if key == "1":
            return super(ExtendedClipboard, self).has_text()
        else:
            return key in self._clip and self._clip[key] is not None

    def get_text(self, slot=1):
        """
        Returns the contents of the specified slot of this virtual clipboard instance.
        """
        key = self._key(slot)
        if key == "1":
            return super(ExtendedClipboard, self).get_text()
        else:
            return self._clip.get(key)

    def set_text(self, content, slot=1):
        """
        Sets the contents of the specified slot on this virtual clipboard instance.
        """
        key = self._key(slot)
        if key == "1":
            super(ExtendedClipboard, self).set_text(content)
        else:
            if key is None:
                self._clip.pop(key, None)
            else:
                self._clip[key] = content

    def clear_text(self, slot=1):
        """
        Clears the contents of the specified slot on this virtual clipboard instance.
        """
        self.set_text(None, slot)

    def clear_all_text(self):
        """
        Clears the contents of all slots on this virtual clipboard instance.
        """
        self.clear_text(1)

        self._clip = {}

    def load(self, file):
        """
        Loads the contents of the specified file into this virtual clipboard
        """
        tmp = utilities.load_json_file(file)

        # The first slot is special and handled by parent classes
        if "1" in tmp:
            slot1 = tmp["1"]
            tmp.pop("1")
            self._clip = tmp
            self.set_text(slot1, "1")
        else:
            self._clip = tmp
            self.set_text(None, "1")

    def save(self, file):
        """
        Saves the contents of this virtual clipboard to the specified file
        """
        temp_clip = self._clip.clone()
        if self.has_text("1"):
            temp_clip["1"] = self.get_text("1")
        
        utilities.save_json_file(temp_clip, file)

    def _key(self, obj):
        # Convert key to string so 1 and "1" resolve the same
        key = str(obj)

        if obj is None or not re.match('^\\w+$', key):
            raise ValueError("Clipboard key must be alphanumeric")

        return key

    
Clipboard = ExtendedClipboard