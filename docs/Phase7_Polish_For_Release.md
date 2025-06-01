The finish-line is in sight! Phase 7 – Polish & Release Candidate transforms Jammin’ Eats from a solid alpha into a store-ready build. Below is a production-grade checklist that locks down performance, security and UX; adds accessibility, localization and analytics; and packages a signed installer. Follow the gates in order—each “✓ Done When…” acts as an objective milestone.

0 Project Kick-off
Branch & version – git checkout -b release/v1.0.0-rc and bump changelog.md to v1.0.0-rc.

Freeze features – only bug-fixes and polish enter this branch (feature flags for anything risky).

QA calendar – schedule daily smoke-test slots and a full regression pass before tagging GA.

1 Performance, Memory & Battery
1.1 Profile & optimise
Run python -m cProfile -o perf.prof main.py in three gameplay scenarios (title screen, mid-wave, end-wave).

Visualise hot-spots with SnakeViz or PyInstrument; focus on draw loops and collision checks.

Apply known Pygame optimisations:

Use spritecollideany for yes/no checks instead of full list collisions 
Reddit
.

Implement object pools for food projectiles and particle FX to avoid per-frame allocations 
Reddit
.

Enable double-buffering / HWSURFACE + pygame.display.set_mode(flags=pygame.DOUBLEBUF|pygame.HWSURFACE) to gain free FPS 
CodeProject
.
✓ Done When… FPS ≥ 60 on a mid-tier laptop and memory footprint stays flat after 30 min.

2 Quality-Assurance Pipeline
2.1 Automated tests & CI
Expand unit coverage to ≥ 80 %; add smoke tests that launch the main loop headless for 5 s.

GitHub Actions job caches pip deps and runs pytest on pushes 
GitHub Docs
.

Attach artefacts: perf profile, coverage HTML, signed build ZIP.

2.2 Manual test matrix
OS	GPU	Input	Status
Win 10	Intel UHD	Xbox pad	 
Win 11	GTX 1650	KB/M	 
Steam Deck (Windows)	RDNA2	Gamepad	 

✓ Done When… All platforms pass regression sheet with zero critical bugs.

3 Accessibility Pass
Audit against GameAccessibilityGuidelines.com – Basic & Intermediate checklists 
gameaccessibilityguidelines.com
.

Add: scalable font slider, colour-blind palette toggle, remappable controls and an optional No-Fail tutorial flag (indies like Tunic prove this can be elegant 
WIRED
).

Provide on-screen iconography (not just colour) for food types to aid colour-blind users 
WIRED
.

✓ Done When… Internal tester with colour-blindness completes a full round unaided.

4 Localization Readiness
Externalise all UI strings to locales/en_US.json.

Follow the 10 localisation best practices—avoid hard-coding flags and respect locale-specific formats 
Localization Services by BLEND
.

Pipe JSONs through Crowdin/Lokalise or a CSV sheet for translators.

✓ Done When… You can switch LANG=es_ES at launch and see Spanish UI placeholders.

5 Security & Compliance
Static analysis – run bandit & ruff with OWASP secure-coding rules 
OWASP Foundation
.

Input validation – sanitise player-name text fields to prevent malformed save files.

Code signing – sign the PyInstaller EXE with Windows SDK signtool or osslsigncode; see community guide 
Gist
Reddit
.

GDPR – analytics collect only anonymised session IDs; offer one-click opt-out 
Reddit
.

✓ Done When… Windows SmartScreen shows a verified publisher and Bandit returns 0 high-severity issues.

6 Build, Package & Installer
PyInstaller one-folder build → dist/JamminEats.

Run post-build script: compress textures, embed jammin.db seed file, copy licences.

Sign the EXE & installer as above; produce a ZIP and a Windows MSI via WiX.

Artifacts uploaded by CI for each push to release/*.

✓ Done When… Fresh VM downloads ZIP, double-clicks JamminEats.exe, game launches without warnings.

7 Store-front Preparation
7.1 Steam (or itch.io)
Follow Steamworks “Game Build Checklist” for release branch and depots 
Steamworks
.

Prepare capsule art, trailer and screenshot set at 1920×1080.

Fill in age-ratings and privacy policy on the store backend.

7.2 Press & Community
Draft press-kit (docs/press_kit/) with factsheet, GIFs and logo variants.

Schedule announcement tweets, Reddit posts and dev-log articles one week before launch.

✓ Done When… Store page passes Valve/itch review and “Coming Soon” page is live.

8 Telemetry & Crash Reporting
Integrate a lightweight module (e.g., Tinybird HTTP call) that posts anonymised run_history stats on session close (honouring opt-out).

Use Sentry’s free Python tier for uncaught exceptions in the release build.

✓ Done When… You can view a Sentry test error and one analytics ping in dashboards.

9 Release Candidate Sign-off
Tag v1.0.0-rc → CI builds → internal distribution.

48-hour “orange-box” period: only blocker fixes allowed.

If zero blockers arise, retag same commit as v1.0.0 and push to public branches/depot.

🔟 Post-Launch Support Plan
Hot-fix window – keep hotfix/* branch template ready; automate beta-branch pushes.

Roadmap – log future DLC ideas (extra foods, maps).

Community channels – set up Discord feedback bot to pipe bugs into issue tracker.

Deliverables Snapshot
Deliverable	Location	Gate
perf.prof & optimisation commits	perf/	Gate 1
Accessibility checklist & test video	docs/accessibility/	Gate 3
Localisation JSONs	locales/	Gate 4
Signed JamminEats.zip + MSI	releases/	Gate 6
Store assets & press-kit	docs/press_kit/	Gate 7
Sentry & analytics dashboards	URLs in README	Gate 8

By methodically knocking down each section—performance, QA, accessibility, security, packaging, store compliance—you’ll ship Jammin’ Eats as a lean, inclusive and maintainable 1.0 release that’s ready for long-term support and future content drops. Happy launch day! 🚀