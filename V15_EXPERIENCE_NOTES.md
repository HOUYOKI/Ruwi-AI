# Ruwi v15 — High Fidelity Touch Experiences

## What changed
- 20 artifact-specific experiences remain one-per-artifact, but the interaction logic is differentiated by the subject.
- The experience world is separate from the artifact viewer. The artifact itself is not duplicated as decorative geometry inside the scene.
- Direct touch is the primary interaction: drag, place, trace, inspect, assemble, feed, balance, and guide.
- Pottery now deforms the actual 3D clay mesh vertices instead of only scaling a primitive.
- Calligraphy/ink interactions leave continuous 3D stroke geometry instead of repeated rings.
- Meteor experience uses a textured Earth globe with atmosphere and a separate cloud shell. The Earth map is generated from Natural Earth country boundaries for geographic recognizability; it is not a satellite scan.
- Local Earth textures are bundled in `frontend/public/scenes/earth_map.png` and `earth_clouds.png` so the globe does not depend on a remote texture URL.
- Workshop, cave, laboratory, desert, road, and night environments use distinct staging and lighting.

## Important provenance note
The 20 artifact records and their existing artifact images/GLBs are still the project assets. They are described as interactive reconstructions in the existing project documentation. They should not be presented as official museum photogrammetry scans unless the museum supplies/approves those assets.

## Exhibition target
- Portrait touch displays, especially 1080x1920.
- Arabic-first UI.
- No required step buttons inside the experience.
- Hints describe what to touch rather than which stage to press.
