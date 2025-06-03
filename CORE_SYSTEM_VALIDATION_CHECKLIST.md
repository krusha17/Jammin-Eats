# Jammin' Eats – Core System Validation Checklist

**Status:** Tutorial system, DAL, and state machine are validated and working. Project is in the graybox validation phase. Use this checklist to validate all systems before asset integration and polish.


> Purpose: Provide a *mechanics-first* test plan that professional game studios use to validate core gameplay loops **before** art / audio polish.  
> Scope: Tutorial graduation, title → gameplay transition, persistence, economy, input, and error handling on Windows (primary) & cross-platform readiness.

---

## 0. Environment / Build-Pipeline
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| ENV-01 | Clean install | Clone repo → `python -m venv venv` → `pip install -r requirements.txt` → `python initialize_database.py` | No errors; `data/jammin.db` created. |
| ENV-02 | Missing DB graceful fallback | Rename `data/jammin.db` → launch game | Warning log + in-memory DB used; game still boots. |
| ENV-03 | Pygame init | Run `python - <<<'import pygame, sys; pygame.init(); print(pygame.get_sdl_version())'` | Non-zero SDL version printed; no exceptions. |

---

## 1. Database & Persistence
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| DB-01 | Player profile default | Delete/rename DB → run initializer → inspect `player_profile` | Row exists with `player_id=1`, `tutorial_complete=0`. |
| DB-02 | Tutorial completion flag | Play tutorial → complete → exit game → inspect DB | `tutorial_complete=1` for `player_id=1`. |
| DB-03 | High-score update | Manually call `update_high_score(1, 999)` → query DB | `high_score` becomes `999`. |

---

## 2. Tutorial Graduation Flow
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| TG-01 | Initial launch shows tutorial | Fresh DB → launch → observe | Tutorial instructions visible; money & deliveries 0/targets. |
| TG-02 | SPACE increments money | Press SPACE 3× | `$30` displayed; deliveries updated if scripted. |
| TG-03 | Goal reached triggers overlay | Reach $50 OR 5 deliveries | *Tutorial Complete* overlay fades in. |
| TG-04 | ENTER persists completion | On overlay press ENTER → title screen | `tutorial_complete` in DB set to `1`. |
| TG-05 | Skip tutorial on relaunch | Relaunch game | Title screen shown immediately, *Continue* enabled. |

---

---

**Project Status (as of 2025-06-02):**
- Environment, Database, and Tutorial Graduation Flow: **COMPLETE & VALIDATED**
- Title → Gameplay Transition: **BLOCKED** (missing modules: game_map, player, asset loading)
- Next: Implement map, player, and asset modules to enable gameplay and menu transitions.

---

## 3. Title → Gameplay Transition
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| TP-00 | Title screen | Fresh DB → launch → observe | Title screen shown immediately, *Continue* enabled. |
| TP-01 | Start new game | At title press New Game | Game loop begins; player/objects spawn if assets exist. |
| TP-02 | Load saved game | At title press Load Game | Game loop begins; player/objects spawn if assets exist. |  
| TP-03 | Exit button | Click EXIT | Window closes; process ends with exit code 0. |

---

## 4. Economy & Scoring
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| EC-01 | Delivery payment | During gameplay deliver food | `economy.add_money()` called; money increases correctly. |
| EC-02 | High-score save | Finish run with score > DB high score | `high_score` updates. |

---

## 5. Input Handling & Security
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| IN-01 | Key debounce | Hold SPACE 2 sec | Money increments only at expected rate (no rapid-fire exploit). |
| IN-02 | Invalid key safety | Mash random keys | No crashes, unhandled exceptions, or unexpected state changes. |
| IN-03 | SQL injection guard | Attempt to call DAL with malicious string via debug console | DAL sanitizes input / uses parameterized queries → DB intact. |

---

## 6. Error Handling & Logging
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| ER-01 | Asset missing | Temporarily rename an asset → launch game | Error log shows missing asset but game continues / uses placeholder. |
| ER-02 | DB locked | Open DB in external editor → play game | DAL retries or logs error gracefully; no crash. |

---

## 7. Performance (Baseline)
| ID | Test | Steps | Expected Result |
|----|------|-------|-----------------|
| PF-01 | FPS stability | Launch minimal tutorial → observe `clock.get_fps()` for 30 sec | Avg FPS ≥ target (e.g., 60). |
| PF-02 | Memory leak smoke | Play for 10 min on low-spec machine | Memory stays within 10% of baseline. |

---

## 8. Regression Suite Automation (Pytest)
- **`tests/test_tutorial_system.py`** already covers DAL and tutorial logic.
- Add tests for:
  1. `GamePersistence` loading / saving.
  2. Economy calculations.
  3. Input debounce edge cases.

```bash
pytest -q tests
```
Should print all **PASSED**.

---

## 9. Continuous Integration (CI) Suggestions
1. **Linting:** `ruff` / `flake8` gate.
2. **Unit tests:** Run PyTest on each PR.
3. **Package audit:** `pip-audit` for dependency CVEs.
4. **Artifact build:** Optional – bundle with PyInstaller for nightly builds.

---

## 10. Future Asset-Integration Checklist (Post-Mechanics)
1. Map tileset loads → draw order correct.
2. Player sprite animations → frame-timing validated.
3. Customer sprites & paths.
4. Sound effect volume obeys `player_settings`.
5. Loading screen while heavy assets decode.

---

### Usage
1. Place this file at repo root (`CORE_SYSTEM_VALIDATION_CHECKLIST.md`).
2. Check off each **ID** before moving to the next development milestone.
3. Update checklist as new systems are added.

Happy testing — *keep it gray, keep it fast!*
