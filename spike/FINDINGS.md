# WP01 findings — does GitHub Pages serve raw `.md` as readable text?

**Mission**: `guide-site-build-01KXP76R` · **Work package**: WP01 (spike) · **Settles**: contract
condition **C1** in `contracts/url-map.md`, spec risk **R-001**, research **§ R3**

## Answer

**Yes. C1 holds.** GitHub Pages serves `.md` from the project-site subpath as
**`content-type: text/markdown; charset=utf-8`**, with **no `Content-Disposition`**, and the body is the
markdown **source**. A model doing a plain GET on `{base}AGENTS.md` receives readable text. The machine
surface (FR-007, FR-008) can be built as the URL map specifies. **No fallback is needed and the URL map
does not change.**

## How the evidence was produced

- Deployment: `.github/workflows/spike-content-type.yml` published **only** `spike/` to Pages via
  `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`. Run
  [29532549096](https://github.com/Conspiracy-LARP/dungeon-masters-guide/actions/runs/29532549096),
  conclusion `success`, deployed 2026-07-16T20:33:35Z.
- Shape: the **real** thing — the live project site at
  `https://conspiracy-larp.github.io/dungeon-masters-guide/`, a **subpath**, not a domain root (C-003).
- Method: `curl -isS` — a plain GET with no browser headers, no `Accept` negotiation, i.e. what a model
  actually does. The judgement below is on the **headers and body**, not on any browser rendering.
- `probe.md`, `probe.txt` and `probe` were **byte-identical** (sha256
  `a6f6593df40d9d94684bd86529deb02aa193c35e8d84eb62a1b3d5eb991d99ba`, 614 bytes each), so the only
  variable between them is the file extension. All three returned `content-length: 614`.

## Summary of recorded responses

| URL | Status | `Content-Type` | `Content-Disposition` | Body |
|---|---|---|---|---|
| `{base}probe.md` | 200 | `text/markdown; charset=utf-8` | **none** | markdown **source** |
| `{base}probe.txt` | 200 | `text/plain; charset=utf-8` | **none** | markdown **source** |
| `{base}probe` (no extension) | 200 | `application/octet-stream` | **none** | markdown **source** |
| `{base}.nojekyll` | 200 | `application/octet-stream` | none | empty (`content-length: 0`) |

## Raw responses (verbatim)

### `GET https://conspiracy-larp.github.io/dungeon-masters-guide/probe.md`

```http
HTTP/2 200
server: GitHub.com
content-type: text/markdown; charset=utf-8
last-modified: Thu, 16 Jul 2026 20:33:35 GMT
access-control-allow-origin: *
strict-transport-security: max-age=31556952
etag: "6a59401f-266"
expires: Thu, 16 Jul 2026 20:43:49 GMT
cache-control: max-age=600
x-proxy-cache: MISS
x-github-request-id: 20B2:20ABF:2E9673:3093DB:6A59402C
accept-ranges: bytes
age: 0
date: Thu, 16 Jul 2026 20:33:49 GMT
via: 1.1 varnish
x-served-by: cache-lon4255-LON
x-cache: MISS
x-cache-hits: 0
x-timer: S1784234029.040745,VS0,VE100
vary: Accept-Encoding
x-fastly-request-id: 169d605e620050377d527cd7253dfdcaec1a6a08
content-length: 614

# Probe heading

This file is a WP01 spike probe for mission `guide-site-build-01KXP76R`. It exists to reveal how
GitHub Pages serves a raw `.md` file from a project-site subpath.

If you are reading this text as **markdown source** — heading marks, asterisks and all — then the
machine surface works: a model fetching this URL receives readable text.

If you are reading rendered HTML instead, condition C1 in `contracts/url-map.md` does not hold.

- A list item, to make source-vs-rendered obvious.
- A [link to the guide](https://conspiracy-larp.github.io/dungeon-masters-guide/).

SENTINEL-WP01-PROBE-BODY
```

The body arrives with `#`, `**`, `-` and `[]()` intact — it is the **source**, not rendered HTML. This is
the decisive observation.

### `GET https://conspiracy-larp.github.io/dungeon-masters-guide/probe.txt`

```http
HTTP/2 200
server: GitHub.com
content-type: text/plain; charset=utf-8
last-modified: Thu, 16 Jul 2026 20:33:35 GMT
access-control-allow-origin: *
strict-transport-security: max-age=31556952
etag: "6a59401f-266"
expires: Thu, 16 Jul 2026 20:43:49 GMT
cache-control: max-age=600
x-proxy-cache: MISS
x-github-request-id: 3E36:2ED96E:139ECFA:13D42AA:6A59402D
accept-ranges: bytes
age: 0
date: Thu, 16 Jul 2026 20:33:49 GMT
via: 1.1 varnish
x-served-by: cache-par-lfpg1960057-PAR
x-cache: MISS
x-cache-hits: 0
x-timer: S1784234029.196431,VS0,VE110
vary: Accept-Encoding
x-fastly-request-id: d0993a942132feda67c2fe6885e68676d61b3598
content-length: 614

(body identical to probe.md — markdown source)
```

### `GET https://conspiracy-larp.github.io/dungeon-masters-guide/probe` (no extension)

```http
HTTP/2 200
server: GitHub.com
content-type: application/octet-stream
last-modified: Thu, 16 Jul 2026 20:33:35 GMT
access-control-allow-origin: *
strict-transport-security: max-age=31556952
etag: "6a59401f-266"
expires: Thu, 16 Jul 2026 20:43:49 GMT
cache-control: max-age=600
x-proxy-cache: MISS
x-github-request-id: AF6C:454BD:2EE5D8:30E33A:6A59402C
accept-ranges: bytes
age: 0
date: Thu, 16 Jul 2026 20:33:49 GMT
via: 1.1 varnish
x-served-by: cache-lon4251-LON
x-cache: MISS
x-cache-hits: 0
x-timer: S1784234029.342247,VS0,VE91
vary: Accept-Encoding
x-fastly-request-id: dbd7484f9e6684fe7b68e305d1b95d00d603b45f
content-length: 614

(body identical to probe.md — markdown source)
```

### `GET https://conspiracy-larp.github.io/dungeon-masters-guide/.nojekyll`

```http
HTTP/2 200
server: GitHub.com
content-type: application/octet-stream
last-modified: Thu, 16 Jul 2026 20:33:35 GMT
access-control-allow-origin: *
strict-transport-security: max-age=31556952
etag: "6a59401f-0"
expires: Thu, 16 Jul 2026 20:43:49 GMT
cache-control: max-age=600
x-proxy-cache: MISS
x-github-request-id: 640C:314EE4:1396D8F:13CC2E9:6A59402D
accept-ranges: bytes
age: 0
date: Thu, 16 Jul 2026 20:33:49 GMT
via: 1.1 varnish
x-served-by: cache-par-lfpg1960085-PAR
x-cache: MISS
x-cache-hits: 0
x-timer: S1784234029.481102,VS0,VE112
vary: Accept-Encoding
x-fastly-request-id: dffd6948f38f9d8a4521142256794608d10d6b76
content-length: 0
```

### `Content-Disposition` scan

```
probe.md   -> (no Content-Disposition)
probe.txt  -> (no Content-Disposition)
probe      -> (no Content-Disposition)
```

### C2 spot-check — the subpath is real

```http
$ curl -isS "https://conspiracy-larp.github.io/probe.md"
HTTP/2 404
server: GitHub.com
content-type: text/html; charset=utf-8
```

```http
$ curl -isS "https://conspiracy-larp.github.io/dungeon-masters-guide/"
HTTP/2 200
server: GitHub.com
content-type: text/html; charset=utf-8
```

Root-relative addresses 404, as C2 predicts. Every generated link must be subpath-correct.

## Reading of the evidence

1. **`.md` is served, readably.** `text/markdown; charset=utf-8` is a `text/*` type with an explicit
   charset and no attachment disposition. It is fetched and read as text, not saved to disk. FR-007 and
   FR-008 are achievable exactly as the URL map specifies. **R-001 does not materialise.**
2. **`.nojekyll` is honoured** — the `.md` exists at its own address, unrenamed and unconverted. Note that
   with `upload-pages-artifact` + `deploy-pages` the artifact is served statically and Jekyll is not in
   the path at all, so `.nojekyll` is belt-and-braces here rather than load-bearing. It is retained: it
   costs one empty file, FR-012 requires it, and it protects against a future switch to branch-based
   publishing, where its absence *would* break the machine surface silently.
3. **The extensionless fallback would have been worse than the problem.** Research § R3 ranked
   *extensionless twins* above Fly as the second fallback. The evidence says extensionless serves as
   **`application/octet-stream`** — the least readable of the three, and the only genuinely download-ish
   type observed. Had C1 failed, the ranking should have been `.txt` twins (`text/plain`, clean) and then
   Fly; **extensionless should be struck as a fallback candidate.** Recording this so nobody re-derives
   it: it cost one extra file to learn, exactly as the WP intended. Moot in practice, since C1 holds.
4. **`.txt` twins remain a proven escape hatch** (`text/plain; charset=utf-8`) if GitHub ever changes the
   `.md` mapping. Not needed, not built.

## Decision (T003)

**Condition C1 is CONFIRMED.** `.md` is served as `text/markdown; charset=utf-8` — readable text, not a
download and not rendered HTML.

- The URL map in `contracts/url-map.md` **stands unchanged**.
- **No fallback is adopted.** No `.txt` twins, no extensionless twins, no Fly.
- The Amendment rule is **not** triggered: the guide's published text (`src/pack/start.md`,
  `README.md`, `technical-suggestions.md`) keeps quoting the addresses it already promises. Nothing in
  `src/pack/` is touched, and content stays out of scope (C-006). **Nothing to escalate.**
- Downstream WPs may rely on `{base}<doc>.md` and `{base}AGENTS.md` being machine-readable.

### Standing risk, for whoever owns the site later

The content-type is GitHub's choice, not ours, and it is **not** pinned by anything in this repo. If
GitHub ever remaps `.md`, the machine surface fails **silently** while the site still looks perfect — the
exact invisibility that justified this spike. This evidence is a snapshot of 2026-07-16, not a guarantee.
Cheap insurance, if wanted later: a post-deploy check asserting `curl -sSI {base}AGENTS.md` still returns
a `text/*` content-type. Out of scope for this WP; noted for whoever owns FR-007/FR-008 in service.

## Cleanup (T004)

The spike deployment is **removed**, per T004 — no mystery workflow, no stray Pages deploy:

- `.github/workflows/spike-content-type.yml` is deleted in the same commit that records this finding.
- The probe files (`probe.md`, `probe.txt`, `probe`, `index.html`, `.nojekyll`) are deleted. This file is
  the deliberate exception: it **is** the deliverable.
- The temporary `github-pages` deployment-branch policy for the spike branch (id `54841701`) is revoked;
  the environment is returned to `main`-only, as found.
- The spike content remains live at the Pages URL only until WP03's real deployment overwrites it. Pages
  serves the most recent deployment; there is no way to un-deploy without deploying something else, and
  publishing the real site is WP03's job, not this spike's. The `index.html` says plainly that it is a
  throwaway spike. **This is the one residue of WP01 and it is self-describing.**
