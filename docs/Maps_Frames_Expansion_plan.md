Below is a production-oriented Phase “Maps & Frames Expansion” plan.
It adds completely new maps/frames while keeping every mechanic—inventory, upgrades, DB persistence—intact, and prepares the codebase for rapid future content drops.

Executive Summary
You’ll create a data-driven level catalogue stored in SQLite, feed it TMX files exported from Tiled, and switch the runtime to a state-machine loader so each frame/map is just another row in the database. This isolates gameplay code from content, keeps frame-to-frame performance high, and lets designers add new levels without touching Python. Key practices—PyTMX for maps, object-pooled sprites, and a DB-backed level registry—mirror common indie pipelines and scale cleanly to dozens of maps. 
Pygame
Auth0
Reddit
Reddit

1 Design & Scoping
1.1 Draft the Level Catalogue
Column	Example	Notes
level_id (PK)	1-01	world-frame pattern (world-level).
tmx_path	assets/maps/world1/frame01.tmx	Relative path.
bgm	lofi_beach.ogg	Music cue.
par_time	90	Seconds target for medals.
unlock_req	NULL	Level gating logic.

Store this schema in your new levels table. SQLite fits because reads are single-player, local, and low-latency 
Reddit
SQLite
.

1.2 Map-building checklist
Tile layers: sky, ground, decor, collision.

Object layers: CustomerSpawns, UpgradeTokens, Teleports.

Re-use the PyTMX loader to extract objects so code changes are minimal 
Pygame
.

2 Content Pipeline
2.1 Tiled → Git workflow
Designer exports .tmx into assets/maps/<world>/.

A pre-commit hook validates the file and runs tmxlint to catch missing tiles.

Large image layers (static backgrounds) get pre-baked to PNG once, then blitted as a single surface for FPS gains 
Reddit
.

2.2 Sprite/Animation frames
Adopt a batch-sheet tool (e.g., SpriterNator) so every food/customer animation is exported as one atlas with JSON frame-timings; prevents duplication and accelerates loading 
DEV Community
GameMaker Forum
.

3 Runtime Architecture
3.1 State-machine level loader
Implement a LevelState class that plugs into your existing game state machine 
Auth0
Welcome to python-forum.io
.

python
Copy
Edit
class LevelState(GameState):
    def __init__(self, level_meta):
        self.tmx = pytmx.load_pygame(level_meta['tmx_path'])
        self.build_scene()
    def on_event(self, ev): ...
    def update(self, dt): ...
    def draw(self, surf): ...
The main state manager pops the old LevelState and pushes a new one when the player completes a frame. This pattern is simpler than nested if/elif chains and scales to any number of maps 
Stack Overflow
.

3.2 Data-driven spawning
Customer spawn points come from the CustomerSpawns object layer; food request logic stays unchanged, so all maps instantly inherit inventory and penalty rules 
Stack Overflow
Reddit
.

4 Database Integration
Migration 013_add_levels.sql – creates the levels table and seeds the first map.

A DAL helper:

python
Copy
Edit
def get_level_meta(level_id: str) -> dict:
    with dal.get_conn() as c:
        return dict(c.execute(
            "SELECT * FROM levels WHERE level_id=?", (level_id,)
        ).fetchone())
Game.reset_state() now accepts level_id, fetches metadata, and instantiates LevelState.

All other Phase 4 persistence code (save profiles, run history) continues to work unchanged.

5 Performance & Memory
Object pools for food projectiles per level to dodge Python GC churn 
Reddit
.

Surface caching – prerender static tile layers to an off-screen surface at load; draw once per frame.

Lazy asset loading – keep only current level’s textures/animations in RAM; evict on state pop.

6 Testing & CI
Test type	Tooling	Example
Level smoke	pytest + headless SDL	Load every TMX via PyTMX, assert no missing tiles.
Progression path	Parametrised test cycling through level IDs	Ensure unlock requirements resolve.
DB migration	pytest with :memory:	Upgrade → insert level row → query back.

Automate these in GitHub Actions so a bad TMX or migration blocks merge 
Reddit
.

7 Security & Future-proofing
TMX whitelisting – load maps only from assets/maps/ to avoid arbitrary-file reads.

Input sanitisation – validate level IDs against regex [0-9]{1,2}-[0-9]{2} before querying DB.

Schema versioning – continue using Alembic/numeric migration folders; rollback tested in CI.

Content hot-patching path – keep TMX and PNGs external so you can ship content updates without touching the binary.

8 Roadmap Gate-Checks
Gate	Proof
G1 – Catalogue ready	All level rows present; TMXs load via smoke test.
G2 – State machine live	Player can finish map 1-01 and auto-loads 1-02.
G3 – Performance	≥60 FPS on mid-tier machine after 20 min of map-switching.
G4 – CI green	All headless tests & migrations pass.
G5 – Design review	Designers add a new TMX + DB row without code edits.

After G5, you rinse-and-repeat: designers keep adding frames, coders focus on mechanics.

9 Team Workflow Tips
Branch naming – content/level-1-03 for pure TMX/asset commits; no Python changes allowed.

Code review template – includes “FPS after 1 min” column to catch heavy maps early.

Weekly content freeze – merge all map work Thursday, dedicate Friday to regression QA.

Ready to build out the world 🌍
By shifting to a data-driven catalogue, leveraging PyTMX, pooling sprites, and guarding every new piece of content with automated tests, you’ll be able to add dozens of frames/maps without destabilising the core loop—and every map immediately benefits from the inventory, penalties and progression systems you’ve already solidified. Happy world-building!