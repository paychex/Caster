import unittest

from castervoice.lib.clipboard import Clipboard
from dragonfly import Clipboard as DragonflyClipboard

class TestExtendedClipboard(unittest.TestCase):
    def setUp(self):
        self.clipboard = Clipboard(file=None)
    
    def test_copy_to_from_system(self):
        pass

    def test_get_set_has_clear_text(self):
        self.clipboard.set_text('text1')
        self.assertEqual(self.clipboard.get_text(), 'text1')

        self.clipboard.set_text('text2', 1)
        self.assertEqual(self.clipboard.get_text(1), 'text2')
        self.assertEqual(self.clipboard.get_text("1"), 'text2')
        self.assertEqual(self.clipboard.text, 'text2')
        self.assertEqual(self.clipboard.has_text(1), True)
        self.assertEqual(self.clipboard.has_text("1"), True)

        self.clipboard.set_text('text3', "1")
        self.assertEqual(self.clipboard.get_text(1), 'text3')
        self.assertEqual(self.clipboard.get_text("1"), 'text3')
        self.assertEqual(self.clipboard.text, 'text3')

        self.clipboard.text = 'text4'
        self.assertEqual(self.clipboard.get_text(1), 'text4')
        self.assertEqual(self.clipboard.get_text("1"), 'text4')
        self.assertEqual(self.clipboard.text, 'text4')

        self.clipboard.set_text('text5', 2)
        self.assertEqual(self.clipboard.get_text(2), 'text5')
        self.assertEqual(self.clipboard.has_text(2), True)

        self.clipboard.set_text('text6', "my_key")
        self.assertEqual(self.clipboard.get_text("my_key"), 'text6')
        self.assertEqual(self.clipboard.has_text("my_key"), True)

        self.assertEqual(self.clipboard.has_text("dne"), False)

        self.clipboard.clear_text()
        self.clipboard.clear_text(2)
        self.clipboard.clear_text("my_key")

        # TODO fix bug in dragonfly
        # self.assertEqual(self.clipboard.has_text(), False)
        self.assertEqual(self.clipboard.has_text(2), False)
        self.assertEqual(self.clipboard.has_text("my_key"), False)


