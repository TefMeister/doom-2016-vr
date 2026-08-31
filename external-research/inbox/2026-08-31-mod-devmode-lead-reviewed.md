# Status flip: the `devMode_enable` lead is 👀 reviewed (not yet tested)

**From:** modding session, 2026-08-31 (dev PC)
**For:** `/gr doom-2016-vr` — please flip the `INDEX.md` row for
`topics/2026-08-27-devmode-enable-public-precedent-and-the-fatal-error-tension.md`
from 🆕 **new** to 👀 **reviewed**. (Modding never edits `INDEX.md` itself.)

## What the modding side did with it

Read in full and **drained from `engine-research/inbox/` into the dossier** on 2026-08-31. It now
sits in `ENGINE-DOSSIER.md` §11, directly under the existing "⚠️ `devMode_enable` is a trap as
shipped" dead end, with both readings kept side by side and each tagged:

- our own live reading of `devMode_fatalErrorOnEnter` = `1` → `[verified-live 2026-08-26, n=1]`
- the public precedent that `devMode_enable 1` is routinely non-fatal → `[reported, /gr 2026-08-27]`

It is also listed in §13's "still open" set, with the safe test order your write-up recommended
(launch-option route, throwaway save, back up the save folder first, then check `listCvars stereo`
and `com_production` visibility immediately).

## Why it is "reviewed" and not "incorporated" or "dead end"

**Nothing has been tested.** The test needs the game launched, and only the user launches. So the
lead has genuinely changed our documentation and our next-step ordering, but it has not yet
produced a result either way.

Deliberately **not** resolved by argument: neither reading disproves the other. The public sources
predate our build (`20240321-104810-ginger-fuchsia`) by years, so either a tripwire was added
later or `devMode_fatalErrorOnEnter` gates something narrower than its name suggests. Recording it
as settled in either direction would be exactly the claim-hygiene failure the confidence tags
exist to prevent.

When it is finally tested, expect a second inbox drop flipping this to ✅ incorporated or
❌ dead end, with the live result.

## Unrelated, for your awareness

This session built DOOM's external command channel and a four-backend input layer
(`staging/doom-2016-vr/proxy-vulkan/`, commit `0d314b1`). If any public research turns up how
id Tech 6 reads input — specifically whether DOOM 2016 uses `GetRawInputData` or
`GetRawInputBuffer` — that would directly settle the one open risk in it. Not a request, just the
question that is live on this side right now.
