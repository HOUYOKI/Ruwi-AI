# Ruwi Touch Exhibition — v13

Dark, Arabic-first, portrait-kiosk Ruwi exhibition prototype with a separate artifact viewer and a large 3D museum-world experience. Each of the 20 current artifact records has its own interaction pattern, scene script, hint, timeline, story, facts, and Ruwi Agent response.

## Important provenance boundary
The current artifact records and GLB files are inherited from the Ruwi-AI dataset and are marked as interactive reconstructions. They must be curator-verified against the official National Museum of Saudi Arabia catalog before an official exhibition deployment. See `MUSEUM_VERIFICATION.md`.

## Run
```powershell
cd frontend
npm install
npm run dev
```
Run the backend separately on port 8000 using the existing FastAPI project.

## v13 experience changes
- Large cinematic 3D scene stage rather than a small primitive widget.
- PBR materials, RoomEnvironment reflections, ACES tone mapping, shadows, fog and particles.
- Independent 3D world for each artifact; the artifact viewer remains separate.
- Direct touch manipulation with no mandatory stage buttons.
- Unique interaction patterns across all 20 current experiences.
- Arabic experience scripts returned by the Experience Agent.
- Portrait kiosk tuning for 1080x1920 displays.
