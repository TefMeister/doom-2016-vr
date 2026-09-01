# Dossier line 68 cites `-staging/proxy-vulkan/`, a pre-consolidation path

Filed by: `/pd`, 2026-09-01

`engine-research/ENGINE-DOSSIER.md:68` refers to the proxy as living in:

```
-staging/proxy-vulkan/
```

The leading bare `-staging/` is a leftover from the `<prefix>-staging` repo naming retired on
2026-08-30. The live path is **`staging/doom-2016-vr/proxy-vulkan/`** in the private staging
monorepo — confirmed present in the staging clone. `[inferred-static 2026-09-01]`

**Why this is an inbox drop and not a fix.** This is the same class of drift that `/gs` filed against
`far-cry-2-vr` and `mad-max-vr` the same day; a `/pd` session found five more instances and repaired
them directly, because `/pd` *is* the modding lane and owns `engine-research/`. **DOOM was
deliberately left alone: it is the game the live modding session has open**, so editing its dossier
would put two writers on one file. Hence a create-only drop.

Also worth knowing: the bare `-staging/` form is the one an estate-wide grep for stale repo names
**misses**, because it carries no game prefix to match on. `far-cry-2-vr` had the identical form.

## Suggested fix

`-staging/proxy-vulkan/` → `staging/doom-2016-vr/proxy-vulkan/`.

Low stakes on its own, but line 68 is the dossier's record of where the live proxy source lives, and
DOOM is the active front — it is exactly the line the next session follows to rebuild.
