import os
import unittest
from unittest.mock import patch

import config


class ProviderPreflightTests(unittest.TestCase):
    def test_all_optional_services_can_be_unconfigured(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(config, "NARRATOR_PROVIDER", None),
            patch.object(config, "NARRATOR_MODEL", None),
            patch.object(config, "VISION_PROVIDER", None),
            patch.object(config, "VISION_MODEL", None),
        ):
            status = config.provider_preflight()
        self.assertTrue(status["core"]["collection"])
        self.assertTrue(status["core"]["curated_experiences"])
        self.assertFalse(status["narrator"]["configured"])
        self.assertFalse(status["vision"]["configured"])
        self.assertFalse(status["tts"]["configured"])

    def test_preflight_reports_readiness_without_secret_values(self):
        environment = {
            "DEMO_BASE_URL": "https://provider.invalid/v1",
            "DEMO_API_KEY": "secret-value",
            "VISION_BASE_URL": "https://vision.invalid/v1",
            "VISION_API_KEY": "another-secret",
            "ELEVENLABS_API_KEY": "tts-secret",
            "ELEVENLABS_VOICE_ID_EN": "voice-en",
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(config, "NARRATOR_PROVIDER", "demo"),
            patch.object(config, "NARRATOR_MODEL", "demo-model"),
            patch.object(config, "VISION_MODEL", "vision-model"),
        ):
            status = config.provider_preflight()
        self.assertTrue(status["narrator"]["configured"])
        self.assertTrue(status["vision"]["configured"])
        self.assertTrue(status["tts"]["configured"])
        self.assertTrue(status["tts"]["english_voice"])
        self.assertFalse(status["tts"]["arabic_voice"])
        self.assertNotIn("secret", repr(status))


if __name__ == "__main__":
    unittest.main()
