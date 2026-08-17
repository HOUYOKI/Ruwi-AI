# Ruwi v11 QA / Asset Audit

## Changes
- Removed artifact IDs 21–25 from the exhibition build because their previous images/models were placeholder geometry and were not suitable as museum artifacts.
- Kept the 20 existing reference artifacts and their transparent PNG/GLB assets.
- Improved direct-manipulation worlds so repeated categories use artifact-specific scenes (vessel residue lab, medical instrument inspection, blade sharpening, etc.).
- Removed passive scene rotation from the interactive worlds; interaction is now driven by direct touch/drag.
- Added higher-quality lighting/material treatment, particles, pointer capture, and smoother direct manipulation.
- Improved artifact viewer lighting and model-load reporting.
- Added an explicit asset-policy document to prevent unverified assets from being presented as official museum scans.

## Important authenticity note
The Saudi National Museum's official website documents a public collection of 4,000+ objects and lists specific collection/gallery items. It also states that photography/publication of museum materials is subject to museum permissions. The current 20 PNG/GLB files in this project are retained as project reference assets; this build does **not** claim they are official museum scans or museum-approved 3D files.

For a production exhibition, replace each reference image/model with museum-approved high-resolution photography and approved photogrammetry/3D assets where available.

## v12 experience architecture
- Rebuilt the interactive world as 20 artifact-specific 3D scenes rather than a shared generic interaction.
- Each scene now has multiple physical objects, direct manipulation, state-dependent visual response, and a distinct interaction mechanic.
- The artifact GLB is loaded into the scene as a contextual museum reference, while the activity remains an independent 3D world.
- Added touch pointer capture and automatic scene response without stage-selection buttons.
- Portrait kiosk layout tuned for tall touch displays.
- Artifact viewer no longer auto-rotates by default; rotation is optional rather than the core interaction.
- Added transparent PNG fallback for artifact viewing when a GLB fails to load.
