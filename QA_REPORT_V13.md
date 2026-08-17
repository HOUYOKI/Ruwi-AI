# v13 QA Notes

Implemented:
- 20 independent 3D scene branches.
- Separate artifact GLB viewer and experience world.
- Cinematic camera entrance.
- PBR materials + RoomEnvironment + ACES tone mapping.
- Direct pointer/touch manipulation.
- Arabic hints and experience scripts for all 20 records.
- Larger portrait-kiosk scene stage.

Build note: dependency installation/build could not be executed in the packaging environment because npm package download was unavailable/time-limited. The source is prepared for `npm install` + `npm run build` on the target Windows machine.
