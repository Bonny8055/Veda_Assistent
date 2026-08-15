from django.test import SimpleTestCase

from .assistant import process_command


class VoiceCommandParsingTests(SimpleTestCase):
    def test_go_phrase_triggers_move_command(self):
        self.assertIn('go', process_command('go command').lower())

    def test_stop_phrase_triggers_stop_command(self):
        self.assertIn('stop', process_command('stop command').lower())

# Create your tests here.
