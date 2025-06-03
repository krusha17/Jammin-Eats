# Jammin' Eats Development Roadmap

## Current Status

**Current milestone:** Title → Gameplay Transition (as of 2025-06-03)

- Tutorial system, DAL, and state machine are validated and working.
- Blockers for this milestone:
  - Map is not loading (fallback/default map shown)
  - Customer food bubbles, food sprites, and HUD info not displayed
  - Food throwing mechanic not functioning (no sprites thrown, food selection not working)
  - Shop overlay opens/closes but is blank
- See `CORE_SYSTEM_VALIDATION_CHECKLIST.md` section 3A for the detailed implementation plan.

## Next Development Phases

### Current Phase: Title → Gameplay Transition

- Follow the step-by-step implementation plan in `CORE_SYSTEM_VALIDATION_CHECKLIST.md` section 3A to resolve all blockers above.
- Do not proceed to asset polish, economy, or scoring until all Title → Gameplay transition checklist items are validated.

> **Note:** Asset integration and polish are deferred until all items in `CORE_SYSTEM_VALIDATION_CHECKLIST.md` are complete.

---

### Implementation Plan Summary (2025-06-03)
| Step | Task |
|------|------|
| 1 | Audit asset paths and existence |
| 2 | Centralize asset management |
| 3 | Remove placeholders |
| 4 | Refactor map loading & rendering |
| 5 | Fix sprite assignment & food throwing |
| 6 | Implement/restore HUD |
| 7 | Populate shop overlay |
| 8 | Add robust error handling/logging |
| 9 | Validate security & efficiency |
| 10 | Update documentation/checklists |

See checklist for full details and rationale for each step.

- [ ] **Unit Tests**
  - [ ] Test tutorial completion detection logic
  - [ ] Test DAL persistence of tutorial completion flag
  - [ ] Test state transitions (tutorial → tutorial complete → title screen)

- [ ] **Integration Tests**
  - [ ] Verify persistence of tutorial completion across game restarts
  - [ ] Test UI updates and menu option enable/disable behavior
  - [ ] Verify tutorial state is properly skipped for returning players

- [ ] **User Experience Testing**
  - [ ] Gather feedback on tutorial clarity and difficulty
  - [ ] Ensure tutorial goals are achievable but educational
  - [ ] Verify all UI elements are clear and responsive

### Phase 2: Finalize Core Systems on First Frame/Map

- [ ] **Upgrade System Completion**
  - [ ] Implement all planned food truck upgrades
  - [ ] Balance upgrade costs and effects
  - [ ] Create upgrade UI with visual feedback

- [ ] **Economy Balancing**
  - [ ] Fine-tune customer spawn rates and patience
  - [ ] Balance food costs, selling prices, and profit margins
  - [ ] Implement difficulty scaling over time

- [ ] **Visual Polish**
  - [ ] Add particle effects for successful/failed deliveries
  - [ ] Improve UI animations and transitions
  - [ ] Add environmental animations (weather, time of day)

### Phase 3: Multi-Frame/Map Support

- [ ] **Map System Enhancement**
  - [ ] Create framework for multiple maps/levels
  - [ ] Implement map transition system
  - [ ] Design progression system between maps

- [ ] **Map-Specific Features**
  - [ ] Create unique customer types per map
  - [ ] Design map-specific challenges and objectives
  - [ ] Implement varying difficulty levels per map

- [ ] **Save/Load System Enhancement**
  - [ ] Implement save slots for multiple game saves
  - [ ] Create load submenu with save previews
  - [ ] Add auto-save functionality at key points

### Phase 4: Performance & Scalability

- [ ] **Code Optimization**
  - [ ] Profile and optimize rendering pipeline
  - [ ] Improve asset loading and caching
  - [ ] Implement object pooling for frequently created entities

- [ ] **Database Optimization**
  - [ ] Optimize database queries and connections
  - [ ] Implement proper indexing for frequently accessed data
  - [ ] Add database migration versioning system

- [ ] **Memory Management**
  - [ ] Implement asset unloading for unused resources
  - [ ] Optimize sprite and animation memory usage
  - [ ] Add memory usage monitoring in debug mode

### Phase 5: Distribution & Deployment

- [ ] **Packaging**
  - [ ] Create installer with all dependencies
  - [ ] Optimize executable size and startup time
  - [ ] Add version checking and update notification

- [ ] **Documentation**
  - [ ] Complete user manual and controls reference
  - [ ] Create developer documentation for future contributors
  - [ ] Document database schema and migration process

- [ ] **Community Features**
  - [ ] Implement high score submission
  - [ ] Add achievement system
  - [ ] Create framework for community-created maps/mods

## Development Principles

- **Data-Driven Development**: All game features should be configurable through data files
- **Test-Gated Progress**: New features require passing tests before merging
- **Modular Architecture**: Maintain clean separation between game systems
- **Error Resilience**: Graceful fallbacks for all potential failure points
- **User-Centered Design**: Regular playtesting and feedback incorporation

## Technical Debt & Refactoring Priorities

- [ ] Consolidate duplicate code in rendering systems
- [ ] Improve error handling and logging consistency
- [ ] Standardize naming conventions across codebase
- [ ] Extract hard-coded values to configuration files
- [ ] Implement proper dependency injection for testability

---

*This roadmap is a living document and will be updated as development progresses.*
