# 2026-08-25 — Project kickoff

Project started today. Target game: **DOOM** (2016, id Software, published
by Bethesda Softworks), built on the **id Tech 6** engine. The Steam copy was
mid-download on the dev PC at the time these repos were seeded — this is the
last new game being added to the active project roster for now.

This is the "first look" phase: the six-repo standard was seeded (`-mod`,
`-dev-archive`, `-modding-notes`, `-staging`, `-engine-research`,
`-external-research`) before any reverse-engineering has started. No binary
analysis, debugging, or code has happened yet — that begins in a later
session, once the install finishes.

Next: begin engine identification per the `PLAYBOOK.md` in
`doom-2016-vr-engine-research` — confirm renderer API (id Tech 6 shipped with
both OpenGL and a later Vulkan path; which one this build defaults to needs
verifying), threading model, and where the camera/projection data lives.
