"""
Ruwi TTS Core — speak_text()

This is the automatic, non-model-invoked step from the Stage 3 spec:
called ONCE after run_narrator_turn() returns a final answer, never
inside the reasoning loop, never a decision the model makes. The
Narrator decides WHAT to say; this decides how it sounds.

TTS-only, per current scope. Visitor still types questions (STS is a
separate, deliberately deferred design decision, not part of this).
"""

import requests

import config


def _detect_language(text: str) -> str:
    """
    Crude but sufficient: if the text contains Arabic script characters,
    treat it as Arabic. This mirrors rule 8's language-matching logic —
    the Narrator already responds in the visitor's language, this just
    needs to pick a matching VOICE for whatever text it's handed.
    """
    arabic_range = range(0x0600, 0x06FF)
    has_arabic = any(ord(ch) in arabic_range for ch in text)
    return "ar" if has_arabic else "en"


def speak_text(text: str, posture: str = "interpreter", model_id: str = "eleven_multilingual_v2") -> bytes:
    """
    Converts final Narrator text to audio. Returns raw MP3 bytes.

    Args:
        text: the Narrator's final answer, already decided, never
            intermediate/reasoning text.
        posture: "storyteller" or "interpreter" — reserved for future
            voice-settings tuning (e.g. slower pacing, more stability
            for storyteller mode). Not yet used to change the request,
            flagged here so it's not silently dropped.
        model_id: ElevenLabs model. eleven_flash_v2_5 = low latency,
            32 languages including Arabic (Saudi Arabia, UAE).
            eleven_multilingual_v2 = higher expressiveness, more
            languages, higher latency — worth A/B testing both for
            the Storyteller posture specifically once that exists.

    Raises:
        RuntimeError if no voice ID is configured for the detected
        language, or if the API call fails — fails loudly, matching
        the Narrator's own fail-closed discipline, never a silent
        empty audio return.
    """
    api_key, voice_id_en, voice_id_ar = config.get_tts_credentials()
    language = _detect_language(text)
    voice_id = voice_id_ar if language == "ar" else voice_id_en

    if not voice_id:
        raise RuntimeError(
            f"No voice ID configured for detected language '{language}'. "
            f"Set ELEVENLABS_VOICE_ID_{'AR' if language == 'ar' else 'EN'} "
            f"to a real voice ID from your ElevenLabs dashboard."
        )

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": config.TTS_STABILITY,
                "similarity_boost": config.TTS_SIMILARITY_BOOST,
                "style": config.TTS_STYLE,
                "use_speaker_boost": True,
            },
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs TTS call failed: {response.status_code} — {response.text}"
        )

    return response.content