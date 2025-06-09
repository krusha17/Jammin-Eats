# Jammin’ Eats Naming Convention Guide

## 1. General Principles
- **Be Consistent:** Always use the same naming style for similar things.
- **Be Descriptive:** Names should clearly indicate what the item is or does.
- **Avoid Abbreviations:** Only abbreviate if it’s a well-known term (e.g., `UI`, `DB`). Otherwise, spell it out.
- **No “Hungarian Notation”:** Don’t prefix variables with type info (e.g., `strName`). Let the type system and context do the work.

---

## 2. File & Directory Names
- **Modules/Files:**  
  Use all lowercase, words separated by underscores (`snake_case`).  
  Example:  
  - `player_profile.py`
  - `black_screen_gameplay_state.py`
  - `data_access_layer.py`
- **Directories:**  
  Use all lowercase, no spaces, underscores allowed if needed.  
  Example:  
  - `src/`
  - `sprites/`
  - `core/`
  - `game_states/`

---

## 3. Class Names
- **PascalCase (a.k.a. UpperCamelCase):**  
  Each word capitalized, no underscores.  
  Example:  
  - `PlayerProfile`
  - `BlackScreenGameplayState`
  - `DataAccessLayer`
  - `GameState`

---

## 4. Function & Method Names
- **snake_case:**  
  All lowercase, words separated by underscores.  
  Example:  
  - `reset_player_progress()`
  - `draw_current_state()`
  - `handle_event()`
  - `is_tutorial_complete()`

---

## 5. Variable & Attribute Names
- **snake_case:**  
  Example:  
  - `current_option`
  - `menu_items`
  - `selected_index`
  - `player_id`

---

## 6. Constants
- **ALL_CAPS_WITH_UNDERSCORES:**  
  Example:  
  - `SCREEN_WIDTH`
  - `PLAYER_SPEED`
  - `WHITE`
  - `BLACK`

---

## 7. Asset Names (Images, Sounds, etc.)
- **snake_case, lowercase, descriptive:**  
  Example:  
  - `player_idle.png`
  - `background_music.ogg`
  - `main_menu_bg.jpg`

---

## 8. State & Event Naming
- **State Classes:**  
  - Always end with `State` (e.g., `TitleState`, `GameplayState`, `PauseState`).
- **Event Handlers:**  
  - Use `on_` prefix for event methods (e.g., `on_player_death`, `on_menu_select`).

---

## 9. Database Tables & Columns
- **snake_case, all lowercase:**  
  Example:  
  - Table: `player_profile`
  - Column: `tutorial_completed`

---

## 10. Test Names
- **Test files:**  
  - `test_<feature>.py` (e.g., `test_new_game_transition.py`)
- **Test classes:**  
  - `Test<Feature>` (e.g., `TestNewGameTransition`)
- **Test methods:**  
  - `test_<behavior>()` (e.g., `test_new_game_resets_database()`)

---

## How Do Studios Enforce This?
- **Written Style Guides:**  
  Shared docs like this, often in the project root or a `docs/` folder.
- **Code Reviews:**  
  PRs/MRs must follow the style guide before merging.
- **Automated Tools:**  
  Linters (e.g., flake8, pylint), pre-commit hooks, and CI checks.
- **Refactoring:**  
  Regularly refactor legacy code to align with conventions.

---

## What To Do If You’re Unsure?
- Check this guide first.
- Look at similar files/classes in the project.
- Ask your team or reviewer.
- When in doubt, favor clarity and consistency.
