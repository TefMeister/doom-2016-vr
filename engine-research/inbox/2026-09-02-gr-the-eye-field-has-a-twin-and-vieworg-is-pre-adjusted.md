# The eye field's neighbour is a float separation, and BFG's view origin is already stereo-adjusted

Filed by: `/gr`, 2026-09-02
Topic: `external-research/topics/2026-09-02-the-eye-field-has-a-twin-and-the-view-origin-is-pre-adjusted.md`
Dossier sections: §6d/§6a (the eye-field search), §6h (the static origin+basis global), §13 (next steps)

`[reported 2026-09-02, from id's published Doom 3 BFG source]`. BFG is id Tech 4's descendant, not id Tech 6 — names transfer across id generations, layouts do not. Treat as a prediction.

- **`viewEyeBuffer` and `stereoScreenSeparation` are adjacent and are the last two members of `renderView_t`** — an `int` eye selector (−1/+1/0) immediately followed by a `float` *"projection matrix horizontal offset, positive or negative based on camera eye"*. **Search for the pair**: it is far more distinctive than an integer named "eye", and either one locates the other.
- **Anchor sequence for matching field order**, in declaration order: `viewID`, `fov_x`, `fov_y`, `vieworg`, `vieworg_weapon`, `viewaxis`, `cramZNear`, `flipProjection`, `forceUpdate`, `time[2]`, `shaderParms[]`, `globalMaterial`, `viewEyeBuffer`, `stereoScreenSeparation`. The `fov_x`/`fov_y` pair and `time[2]` are the recognisable landmarks.
- **⭐ The eye offset is applied in two places, and one is upstream of the renderer.** id's own comment on **both** `vieworg` and `vieworg_weapon` is *"has already been adjusted for stereo world seperation"*. So the world separation is baked into the **view origin** before the render view exists, and `stereoScreenSeparation` handles only the projection-side shift. If id Tech 6 kept the pattern, **the origin+basis global in §6h is a candidate injection point for the per-eye translation** — a different route from driving the camera buffer, and worth weighing before more effort goes into the buffer. `[hypothesis]` for id Tech 6.
- `viewaxis` looks down the **positive X axis** — the basis convention to expect.

Suggested dossier change: record the pair and the anchor sequence in §6d as the search target, and add the two-place eye-offset pattern to §6h as an alternative injection point with its confidence tag.
