import unittest
from unittest.mock import MagicMock, patch

from tts.speak_text import _detect_language, speak_text


class TTSUnitTests(unittest.TestCase):

    def test_detects_english(self):
        self.assertEqual(_detect_language("Hello, welcome to Ruwi."), "en")

    def test_detects_arabic(self):
        self.assertEqual(_detect_language("مرحباً بكم في روي"), "ar")

    @patch("tts.speak_text.config.get_tts_credentials")
    def test_missing_english_voice_fails(self, mock_credentials):
        mock_credentials.return_value = ("key", "", "arabic-voice")

        with self.assertRaises(RuntimeError):
            speak_text("Hello Ruwi")

    @patch("tts.speak_text.config.get_tts_credentials")
    def test_missing_arabic_voice_fails(self, mock_credentials):
        mock_credentials.return_value = ("key", "english-voice", "")

        with self.assertRaises(RuntimeError):
            speak_text("مرحباً بكم")

    @patch("tts.speak_text.requests.post")
    @patch("tts.speak_text.config.get_tts_credentials")
    def test_english_uses_english_voice(self, mock_credentials, mock_post):
        mock_credentials.return_value = (
            "api-key",
            "english-voice",
            "arabic-voice",
        )

        response = MagicMock()
        response.status_code = 200
        response.content = b"fake-mp3"
        mock_post.return_value = response

        result = speak_text("Hello Ruwi")

        self.assertEqual(result, b"fake-mp3")
        self.assertIn("english-voice", mock_post.call_args.args[0])

    @patch("tts.speak_text.requests.post")
    @patch("tts.speak_text.config.get_tts_credentials")
    def test_arabic_uses_arabic_voice(self, mock_credentials, mock_post):
        mock_credentials.return_value = (
            "api-key",
            "english-voice",
            "arabic-voice",
        )

        response = MagicMock()
        response.status_code = 200
        response.content = b"fake-arabic-mp3"
        mock_post.return_value = response

        result = speak_text("مرحباً بكم")

        self.assertEqual(result, b"fake-arabic-mp3")
        self.assertIn("arabic-voice", mock_post.call_args.args[0])

    @patch("tts.speak_text.requests.post")
    @patch("tts.speak_text.config.get_tts_credentials")
    def test_provider_failure_is_controlled(self, mock_credentials, mock_post):
        mock_credentials.return_value = (
            "api-key",
            "english-voice",
            "arabic-voice",
        )

        response = MagicMock()
        response.status_code = 500
        response.text = "provider error"
        mock_post.return_value = response

        with self.assertRaises(RuntimeError):
            speak_text("Hello Ruwi")


if __name__ == "__main__":
    unittest.main()