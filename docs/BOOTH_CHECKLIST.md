# Ruwi Booth Smoke-Test Checklist

Run this checklist on the presentation computer, connected to the intended display and network.

## Start-up

- [ ] Copy `.env.example` to `.env` and add only the services intended for the demo.
- [ ] Start the backend from `backend/` with `uvicorn main:app --host 0.0.0.0 --port 8000`.
- [ ] Open `http://localhost:8000/health/config` and confirm collection/experiences are `true`.
- [ ] Confirm narrator, vision, and TTS readiness matches the services configured for the demo.
- [ ] Start the frontend from `frontend/` with `npm run dev -- --host=0.0.0.0`.
- [ ] Open the frontend in the booth browser and enter full-screen mode.

## Gallery and navigation

- [ ] The gallery loads all 102 artifacts without a blank state.
- [ ] Featured Experiences shows exactly artifacts 6, 14, 18, 43, 46, and 79.
- [ ] Featured cards have visible Ruwi Experience badges.
- [ ] Scan / Upload Artifact is visible without scrolling on the opening screen.
- [ ] Back to gallery returns reliably from an artifact and from the scan page.

## Featured experiences

Open each featured artifact and confirm the image, story, quiz, source, and Ask Ruwi area render:

- [ ] 6 — Meteorite Fragment: select all three timeline events.
- [ ] 14 — Sandstone Altar: select all three hotspots.
- [ ] 18 — Silver Khanjar: select handle, sheath, and curved tip.
- [ ] 43 — Wall Painting: select figure, grapevine, and attendant.
- [ ] 46 — Gold Mask: select holes, facial features, and gold sheet.
- [ ] 79 — Hanging Mabkhara: select dome, chains, and lower bowl.
- [ ] Answer both quiz questions on each artifact; confirm scoring, explanations, and Try again.
- [ ] Open each source link once before the presentation.

## Scan and upload

- [ ] Select a JPEG, PNG, and WebP image within the 8 MB limit.
- [ ] On a mobile device, confirm Take photo opens the rear-camera flow.
- [ ] A confident match navigates to the existing artifact page.
- [ ] A partial match waits for visitor confirmation.
- [ ] An unsupported result offers retry and collection navigation.
- [ ] Repeated taps while analyzing do not create duplicate requests.

## Ask Ruwi and narration

- [ ] Ask one English question and receive a textual answer.
- [ ] Ask one Arabic question and receive a textual answer.
- [ ] If frontend narration is merged, play, pause, and replay both languages.
- [ ] If TTS is unavailable, textual answers still remain usable.

## Fallbacks

- [ ] Start without external credentials: gallery and all six curated experiences still work.
- [ ] `/chat` returns a clear unavailable message when narrator configuration is absent.
- [ ] `/identify` returns a clear configuration message when vision is absent.
- [ ] Disable network access and confirm curated experiences still render.
- [ ] Confirm an ordinary non-showcase artifact still shows its normal detail page.
- [ ] On a machine without WebGL, confirm the static artifact image appears.

## Display check

- [ ] Test at the actual screen resolution and browser zoom.
- [ ] Text is readable from the expected viewing distance.
- [ ] Hotspots align with their intended visual details.
- [ ] Buttons are comfortably usable by touch.
- [ ] No browser toolbars, debug consoles, secrets, or terminal windows are visible.
- [ ] Refresh the page once on `/artifacts/46` to verify direct-route hosting fallback.
