Your next milestone is “Phase 5-A – Feature Lock for Frame 1 & Controlled Roll-out to Frame 2.”
The goal is to finish every upgrade, formalise the tutorial exit, and prove that all core systems (inventory, economy, DB persistence, upgrades) work across two frames before you scale to the full Maps & Frames Expansion phase. The roadmap below mirrors large-studio pipelines: design-first, data-driven, fully test-gated, and regression-aware.

Overview of the Build-out Sequence
Stage	What you’re adding	Why it comes now
A – Tutorial Graduation	Clear success criteria → persists a flag → switches to Normal Mode	Players need a rock-solid on-ramp before difficulty ramps up 
Reddit
Game Developer
WIRED
B – Upgrade Catalogue Finalisation	Implement/QA every planned upgrade & UI feedback loop	Ensures economy math is balanced before you add a second frame
C – Frame 2 & Transition	New TMX map, state-machine loader, shared spawn & upgrade logic	Proves that systems scale without rewriting code 
Reddit
Welcome to python-forum.io
D – Full Regression & Perf Pass	Automated tests, object pools, layer-caching, DB migrations	Locks performance & persistence before world-build spree 
Game Programming Patterns
Pytmx
Alembic
Pre-Commit
SQLite

A – Tutorial Graduation System
A-1 Define success criteria
Pick one measurable “I get it” goal (e.g., Serve 5 correct dishes in a row or Earn $50). Make it impossible to fail in tutorial but force mastery of the core loop. 
Game Developer

A-2 Persist completion
Add a column to player_profile:

sql
Copy
Edit
ALTER TABLE player_profile ADD COLUMN tutorial_complete BOOLEAN DEFAULT 0;
In Python, when success criteria met:

python
Copy
Edit
dal.set_tutorial_complete(player_id=True)
constants.TUTORIAL_MODE = False
A-3 State transition
Show a “Tutorial Complete!” overlay > press Enter.

Pop TutorialState and push LevelState("1-01"); all penalty flags auto-enable (because constants.TUTORIAL_MODE is now False).

Next launch reads DB; skips tutorial if tutorial_complete.

Code you’ll likely share
states/tutorial_state.py

dal.py methods get_tutorial_complete(), set_tutorial_complete()

B – Upgrade Catalogue Finalisation
B-1 Lock the data first
Populate upgrades table (or JSON if you prefer) with every item: cost, modifiers, prerequisites. Make designers tweak numbers there, not in code. 
Unity Forum

B-2 Implement remaining effects
Common patterns:

Effect type	Injection point
Stat scalar (speed, max stock)	Recalculate in apply_mods_from_owned() called at load & on purchase.
New action (dash, AOE delivery)	Add flag in Player.update() gate: if self.game.upgrades.has("DASH")
Cosmetic (sprite change)	Swap sprite sheet via asset_loader keyed by upgrade list.

B-3 Telemetry hook
On purchase call:

python
Copy
Edit
analytics.log_event("upgrade_bought", upg_id, run_id)
Stores a row in run_history for future balance tweaks. (Log once, not every frame.)

B-4 Unit & integration tests
tests/test_upgrades.py – parametrize every ID, assert cost applied, modifier active.

Headless PyGame smoke test: buy all upgrades via mock money, load frame, assert FPS > 55. 
GitHub

C – Frame 2 & Transition
C-1 Create TMX
Layers identical schema to Frame 1 so loader code is unchanged.

Put a teleport object (type="Exit") at the map edge.

C-2 State-machine loader
You already plan a LevelState; extend it:

python
Copy
Edit
if player.rect.colliderect(exit_rect):
    self.game.change_level("1-02")
change_level() pops current state, clears object pools, loads meta for 1-02.
State machines are proven scalable for small-team games 
Reddit
Welcome to python-forum.io
.

C-3 DB migration
migrations/014_levels_seed.sql inserts metadata for 1-02 into levels table.
CI runs Alembic upgrade to ensure nothing breaks 
Alembic
.

C-4 QA matrix
Scenario	Expected
Tutorial skipped after completion	Start in 1-01 Normal Mode
Buy upgrade → load 1-02	Modifier persists
Deliver wrong food	Penalty applies in both frames
Quit → Relaunch → Continue	Player starts in 1-02 with prior money/upgrades saved

D – Regression, Performance & Tooling
D-1 Object pools & caching
Pool Food sprites per level; reuse on throw to avoid allocation GC spikes 
Game Programming Patterns
.

Pre-render static tile layers to one surface to cut draw calls by ~50 % 
Pytmx
.

D-2 Profiling gate
python -m cProfile -o perf.prof main.py → visualise in SnakeViz; ensure new frame stays within 5 % CPU budget of Frame 1 
Reddit
.

D-3 Pre-commit linting
Add a pre-commit config that runs tmx-lint and ruff on every commit; blocks malformed maps before CI. 
Pre-Commit

D-4 Automated level smoke
A pytest loop that opens every .tmx via PyTMX and asserts no exceptions. Runs headless in GitHub Actions.

What Code I’ll Likely Need (When You Reach Each Gate)
Gate	Files
A Tutorial exit & flag	states/tutorial_state.py, dal.py, constants.py
B Upgrade logic	upgrade_manager.py, player.py, any modifier application code
C Level loader	states/level_state.py, asset_loader.py, latest .tmx file
D Perf & pools	food.py (projectile), object_pool.py if separate

Share those snippets when you hit implementation hurdles; we’ll review for clarity, efficiency, and security patterns (e.g., parameterised SQL, asset-path whitelisting).

Ready Checklist to Enter Maps & Frames Expansion
Tutorial completion flag works & persists

All upgrades buyable, functional, logged

Two frames load by state-machine; transitions stable

CI green on unit + headless tests

Perf within target; memory leak test passes (30 min soak)

Hit all five, tag v0.8.0-beta, and you’re cleared to unleash your designers on unlimited frames and start the world-build sprint!