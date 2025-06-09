# Jammin' Eats – Core System Validation Checklist

**Status:** Tutorial system, DAL, and state machine are validated and working. Project is following professional game development practices with a "vertical slice" approach. Core mechanics are prioritized before asset integration.


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

**Project Status (as of 2025-06-03):**
- Environment, Database, and Tutorial Graduation Flow: **COMPLETE & VALIDATED**
- Title → Gameplay Transition: **IN PROGRESS** (blockers: map not loading, missing HUD, food/customer sprites, and shop content)
- Next: Complete asset loading, map rendering, sprite/HUD functionality, and shop overlay population as detailed below.

---

## 3A. Professional Game Development: State Transition Implementation Plan

### Current Achievements and Next Steps
- ✅ Tutorial state transitions fixed (Tutorial → TutorialComplete → Title)
- ✅ State transition framework in Game.run() implemented
- ✅ Tutorial conditions properly evaluated
- ✅ Detailed logging for state transitions added
- 🔄 Title → New Game/Continue transition implementation in progress

### Comprehensive State Machine Implementation Plan

#### Phase 1: Core State Machine Framework (COMPLETED)
| Step | Task | Automated Test | Status |
|------|------|---------------|--------|
| 1.1 | Fix next_state transition handling in Game.run | test_state_transitions.py | ✅ DONE |
| 1.2 | Add proper error handling and recovery | test_error_recovery.py | ✅ DONE |
| 1.3 | Implement state transition logging | test_transition_logging.py | ✅ DONE |

#### Phase 2: Title Menu Options Implementation
| Step | Task | Automated Test | Status |
|------|------|---------------|--------|
| 2.1 | Title → New Game transition | test_new_game_transition.py | 🔄 IN PROGRESS |
| 2.2 | Title → Continue transition | test_continue_transition.py | 🔄 IN PROGRESS |
| 2.3 | Title → Load Game menu screen | test_load_game_menu.py | 📝 PLANNED |
| 2.4 | Load Game → Selected Save | test_load_save_transition.py | 📝 PLANNED |
| 2.5 | Title → Options menu screen | test_options_menu.py | 📝 PLANNED |
| 2.6 | Apply Options Settings | test_apply_settings.py | 📝 PLANNED |
| 2.7 | Exit Button Functionality | test_exit_function.py | 📝 PLANNED |

#### Phase 3: Save/Load Implementation
| Step | Task | Automated Test | Status |
|------|------|---------------|--------|
| 3.1 | Create SaveGameState | test_save_game_state.py | 📝 PLANNED |
| 3.2 | Implement save slot selection | test_save_slot_selection.py | 📝 PLANNED |
| 3.3 | Create SaveManager interface | test_save_manager.py | 📝 PLANNED |
| 3.4 | Implement save file serialization | test_serialization.py | 📝 PLANNED |
| 3.5 | Add save preview thumbnails | test_save_previews.py | 📝 PLANNED |

#### Phase 4: Options Menu Implementation
| Step | Task | Automated Test | Status |
|------|------|---------------|--------|
| 4.1 | Create OptionsState | test_options_state.py | 📝 PLANNED |
| 4.2 | Implement audio settings | test_audio_settings.py | 📝 PLANNED |
| 4.3 | Implement display settings | test_display_settings.py | 📝 PLANNED |
| 4.4 | Implement gameplay settings | test_gameplay_settings.py | 📝 PLANNED |
| 4.5 | Create SettingsManager | test_settings_manager.py | 📝 PLANNED |

#### Phase 5: Asset Management System
| Step | Task | Automated Test | Status |
|------|------|---------------|--------|
| 5.1 | Create AssetManager class | test_asset_manager.py | 📝 PLANNED |
| 5.2 | Implement asset caching | test_asset_caching.py | 📝 PLANNED |
| 5.3 | Add fallback system for missing assets | test_asset_fallbacks.py | 📝 PLANNED |
| 5.4 | Create placeholder generator | test_placeholder_generation.py | 📝 PLANNED |

#### Phase 6: Testing Framework
| Step | Task | Automated Test | Status |
|------|------|---------------|--------|
| 6.1 | Create regression test suite | N/A | 📝 PLANNED |
| 6.2 | Set up GitHub Actions CI pipeline | N/A | 📝 PLANNED |
| 6.3 | Implement automated test reporting | N/A | 📝 PLANNED |
| 6.4 | Create integration test suite | N/A | 📝 PLANNED |

Follow professional game development best practices throughout implementation:
- ✓ Start with core state machine logic
- ✓ Add placeholder visuals before asset integration
- ✓ Implement comprehensive logging and diagnostics
- ✓ Test each module independently before integration
- ✓ Create automated tests for each feature

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
