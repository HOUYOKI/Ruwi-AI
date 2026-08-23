# Final Ruwi Booth Checklist

Run on the presentation computer, intended browser, display, and network. Record pass/fail and retest failures after any change.

## 1. Start and modes

- [ ] Start backend and frontend using the README; open full screen at the intended resolution and zoom.
- [ ] `/health/config` reports collection and curated experiences ready; provider states match the configured booth services.
- [ ] Check each mode: English Light, English Dark, Arabic Light, Arabic Dark.
- [ ] Arabic uses RTL and English uses LTR; theme/language choices survive refresh.
- [ ] Gallery contains Featured Experiences plus the full 102-artifact collection; active artifact name, age, and location are readable.

## 2. Featured matrix

For every row, check image, localized details, experience cue/scroll, indicated template, quiz/reset, source link, Ask Ruwi, TTS play-pause-resume-replay, and back navigation.

| ID | Artifact | Template | EN | AR |
|---:|---|---|:---:|:---:|
| 6 | Meteorite Fragment | Timeline | [ ] | [ ] |
| 14 | Sandstone Cube Altar | Hotspots | [ ] | [ ] |
| 18 | Silver Khanjar | Anatomy | [ ] | [ ] |
| 43 | Qaryat al-Faw Wall Painting | Hotspots | [ ] | [ ] |
| 46 | Small Gold Mask | Hotspots | [ ] | [ ] |
| 79 | Hanging Copper Mabkhara | Anatomy | [ ] | [ ] |

- [ ] Experience cue appears only on those six pages and reaches the experience section.
- [ ] Ordinary artifact page works without a cue or structured experience.

## 3. Upload and camera

- [ ] Desktop drag/drop and file picker work for valid JPEG, PNG, and WebP images up to 8 MB.
- [ ] Mobile Take Photo opens the rear camera and shows a correct preview.
- [ ] Empty, wrong-type, spoofed, and oversized files show localized controlled errors.
- [ ] Confident match opens the existing artifact page.
- [ ] Partial match waits for candidate confirmation; unsupported offers retry.
- [ ] Analyze cannot be submitted repeatedly; retry and return-to-collection work.

## 4. Provider and failure behavior

- [ ] English and Arabic Ask Ruwi return text; TTS uses the intended voice.
- [ ] Narrator unavailable: clear text error; artifact and curated experience remain usable.
- [ ] Vision unavailable: localized controlled failure; browsing remains usable.
- [ ] TTS unavailable: narrator text remains readable.
- [ ] Live experience generation unavailable: validated curated fallback renders.
- [ ] Backend unavailable: frontend shows a readable error rather than a blank page.
- [ ] Network unavailable: local gallery/images and curated experiences continue to work as expected for the deployment setup.

## 5. Booth mechanics

- [ ] Carousel arrows, swipe, wheel, hotspots, quiz choices, upload controls, and audio controls are accurate by touch.
- [ ] Refresh `/artifacts/46` and `/identify` directly to verify hosting fallback.
- [ ] Open every showcase source link once on the booth network.
- [ ] Leave the app idle, replay several answers, and navigate repeatedly; no stale audio or blocked controls remain.
- [ ] No browser chrome, console, terminal, credentials, debug output, or personal data is visible.
- [ ] Complete one final cold start and the two full visitor journeys: browse → experience → Ask Ruwi, and upload → match → experience → Ask Ruwi.
