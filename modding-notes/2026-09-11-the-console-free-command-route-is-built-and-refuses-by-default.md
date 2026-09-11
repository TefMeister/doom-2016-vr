# The console-free command route is built — and it refuses by default (2026-09-11, dev PC, `/pd`)

**One sentence:** the code that would let us tell DOOM what to do *without* the console — no tilde
key, no typing, no log file to parse — now exists, compiles, and is wired into the proxy; it has
never run against DOOM, so it is written to **decline** rather than guess.

## What was built

Two new files in the Vulkan proxy (`staging/doom-2016-vr/proxy-vulkan/src/cmdroute.{h,c}`) and three
new operator commands in `autocmd`:

| command | what it does |
| --- | --- |
| `cmdroute` | reports whether the engine's command system was found, and which of two possible memory layouts it matched — or why it refused |
| `cmd <text>` | runs any console command with no console open |
| `viewpos` | asks for `getviewpos` and reads the six floats it caches, straight out of memory |

This is dossier §6o turned into code. §6o's claim is that `idCmdSystem` sits at RVA `0x2F451C0`,
that vtable slot `+0x50` is `BufferCommandText(this, const char *)`, and that `getviewpos` caches
its answer at `0x5B5CB90` (x, y, z) and `0x5B5CBA0` (pitch, yaw). **All of that is
`[inferred-static 2026-09-10]` — read out of the binary, never run.**

## The two things that shaped how it is written

**1. It is one-shot by construction.** §6o names thread safety as the real hazard, so there is
deliberately **no polling variant**. `viewpos` issues the command once, from an explicit operator
line. Nothing in the present hook's hot path calls it, and there is no code path that could.

**2. It refuses rather than hopes.** Every pointer is checked before it is dereferenced: inside the
module's own address range, in committed and readable memory, and — for the function pointer we
would actually *call* — inside an **executable** page. A stale RVA on a different game build is
indistinguishable from a correct one until you dereference it, and the failure is an instant crash
in someone's running game. So the failure mode is a log line, not a crash.

## ⚠️ The ambiguity §6o does not settle, and what was done about it

§6o says *"idCmdSystem sits at RVA `0x2F451C0`"*. That is consistent with **two different layouts**,
and they are dereferenced differently:

- **POINTER** — the global holds a *pointer to* the object. This is the idTech idiom
  (`cmdSystem->BufferCommandText(...)`).
- **OBJECT** — the global *is* the object.

Guessing here is exactly what this file exists not to do. **Both readings are validated, and the one
that passes is used and named in the log.** If **both** validate and disagree, the call is
**REFUSED** — two readings that both look valid means the evidence does not identify the layout, and
a coin-flip call into the engine is the one outcome worth avoiding outright. If both validate and
*agree* on the same target, that is agreement, not ambiguity, and it proceeds.

`cmdroute` prints which layout it found, so the first live run **settles §6o's ambiguity as a side
effect of the first command anyone types**, with nothing dereferenced if it is wrong.

## What is proved, and what is not

A new host test suite (`test/cmdroutetest.c`, **30 checks**, runs on every build) includes the
shipped `cmdroute.c` directly and proves the guards actually **discriminate**, using pointers whose
nature is certain in the test's own process `[compile-verified 2026-09-11]`:

- the module's first byte is inside, its one-past-the-end byte is **outside**; heap, stack and NULL
  are outside;
- committed heap is readable; NULL, a low bogus address, **reserved-but-uncommitted** memory and a
  `PAGE_NOACCESS` page are all rejected (the first of those is the case a plain null check misses);
- a real function is executable; heap, stack, NULL and **the module's own PE-header page** are not
  (that last one is the point: a pointer can be in the module and readable and still not be code);
- and the headline: **`resolve()` refuses cleanly when run against a binary that is not DOOM**, and
  hands back no function pointer when it does.

**What that does NOT prove:** that the RVAs are right. They cannot be tested without DOOM. The test
proves that being wrong about them produces a refusal instead of a crash.

## What a live run would settle, in one command each

| type this | what each outcome means |
| --- | --- |
| `cmdroute` | names the layout (**POINTER** or **OBJECT**) ⇒ §6o's ambiguity is settled and `[inferred-static]` becomes `[verified-live]`. "unresolved" ⇒ the RVA is wrong on this build, or the object is not constructed yet — nothing was dereferenced either way. "AMBIGUOUS" ⇒ both readings validate and disagree; the census needs redoing before anything is called. |
| `cmd reload` (or any harmless command) | the command visibly takes effect ⇒ **the whole typing dance is retired** — no tilde, no dead key, no `conDump`, no text parsing, ever again |
| `viewpos` | six plausible floats ⇒ the camera is readable from static memory every frame for free. ⚠️ The values are from the **previous** `getviewpos`, because the engine drains its buffer next frame — run it twice. "not plausible" ⇒ the cache RVA is wrong, or `getviewpos` has never run. |

⚠️ **`cmd` will run anything the console would**, so the first live test should be a harmless
command, not `quit`.

## Gate

`GATE: FLAT — NOTHING FURTHER WITHOUT THE GAME RUNNING` on this row. The code is built, tested as far
as it can be tested without DOOM, and deployed-ready; every remaining question about it needs the
game up.
