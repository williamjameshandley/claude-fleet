import tempfile
import unittest

from alan_composer.archive import Archive
from alan_composer.model import Composition, Mode, classify


class VoiceModelTests(unittest.TestCase):
    def test_local_controls_are_exact(self):
        self.assertEqual(classify("Alan, send."), ("control", "send"))
        self.assertEqual(classify("Alan, make this shorter"),
                         ("instruction", "make this shorter"))
        self.assertEqual(classify("A long rambling sentence"),
                         ("dictation", "A long rambling sentence"))

    def test_draft_and_pause(self):
        composition = Composition().append("first").append("second")
        self.assertEqual(composition.draft, "first second")
        self.assertEqual(composition.pause().mode, Mode.PAUSED)
        self.assertEqual(composition.pause().resume().mode, Mode.RECORDING)

    def test_archive_is_append_only_jsonl(self):
        with tempfile.TemporaryDirectory() as root:
            archive = Archive(root)
            composition = Composition()
            archive.record(composition, "opened")
            archive.record(composition, "cancelled", draft="recover me")
            self.assertEqual(len(archive.events.read_text().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
