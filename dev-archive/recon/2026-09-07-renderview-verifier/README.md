# 2026-09-07 — the renderView_t verifier, and §6c is now addressable

`/pd`, dev PC. **The game was not launched; nothing here was run.**

`rvtest-output.txt` — the shipped shape test on the host: **22 checks, 0 failures**, and
**0 of 20,000 random-memory windows** passed the filter.

## What the number means, and what it does not

0/20000 bounds the false-positive rate; it does not make it zero. Random bytes must
produce two 0/1 bool bytes (≈1/128 each) *and* two individually plausible, mutually
consistent field-of-view floats, so the expected count over 20,000 trials was already
well under one. **Read it as "the filter filters", not as "a pass is a proof".**

The positive control is test 1: a well-formed struct built from the real `getviewpos`
reading in dossier §6e is accepted. Without it, a filter that rejected everything would
also have scored 0/20000.
