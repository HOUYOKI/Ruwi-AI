"""
Standalone test for speak_text() — proves TTS works end to end by
producing real, playable .mp3 files, no frontend needed.

    export ELEVENLABS_API_KEY=...
    export ELEVENLABS_VOICE_ID_EN=...   # from your dashboard's Voices tab
    export ELEVENLABS_VOICE_ID_AR=...   # ditto, an Arabic-capable voice
    python test_speak.py
"""

import os
import platform
from dotenv import load_dotenv

load_dotenv()

from speak_text import speak_text


def _play(filepath: str) -> None:
    """
    Zero-dependency playback via the OS default player. sounddevice was
    considered, but it plays raw audio arrays, not .mp3 directly — that
    needs pydub + a separate ffmpeg system install to decode first, an
    extra moving part for no real benefit here. This just opens the file
    the same way double-clicking it would.
    """
    if platform.system() == "Windows":
        os.startfile(filepath)
    else:
        print(f"Auto-play only wired for Windows right now — open {filepath} manually.")


TEST_TEXT_ENGLISH = (
    "This is a hanging copper incense burner, made in 1784, "
    "designed to be suspended in sacred or royal spaces."
)

TEST_TEXT_ARABIC = (
    "هذه مِبْخَرة نحاسية مُعَلّقة، صُنعت عام ألف وسبعمائة وأربعة وثمانين، "
    "لتُعْلّق في الأماكن المقدسة أو المَلَكّية."
)


def main() -> None:
    required = ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID_EN", "ELEVENLABS_VOICE_ID_AR"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        print("Get real voice IDs from your ElevenLabs dashboard's Voices tab first.")
        return

    print("--- Test 1: English text -> English voice ---")
    audio = speak_text(TEST_TEXT_ENGLISH, posture="interpreter")
    with open("test_output_en.mp3", "wb") as f:
        f.write(audio)
    print(f"Wrote test_output_en.mp3 ({len(audio)} bytes)\n")
    _play("test_output_en.mp3")

    print("--- Test 2: Arabic text -> Arabic voice ---")
    audio = speak_text(TEST_TEXT_ARABIC, posture="interpreter")
    with open("test_output_ar.mp3", "wb") as f:
        f.write(audio)
    print(f"Wrote test_output_ar.mp3 ({len(audio)} bytes)")
    _play("test_output_ar.mp3")

    print("\nPlay both files and listen — confirm the Arabic audio actually")
    print("sounds natural (Saudi dialect, not a flat robotic read), and that")
    print("neither file is silent or truncated.")


if __name__ == "__main__":
    main()