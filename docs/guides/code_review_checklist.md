# ud83dudd0d Jammin' Eats Code Review Checklist

This checklist helps ensure consistent code reviews and maintain code quality across the project. Use it when reviewing Pull Requests.

## ud83dudce6 General

- [ ] Does the code follow our modular structure (core, sprites, utils, etc.)?
- [ ] Does the PR have a clear title and description?
- [ ] Are the commits atomic with descriptive messages following our format?
- [ ] Is the PR of reasonable size? (Small PRs are easier to review)

## ud83dudc1b Functionality

- [ ] Does the code perform as described in the PR description?
- [ ] Are edge cases handled properly?
- [ ] Does the code handle errors gracefully?
- [ ] If this adds a new feature, is it complete (or clearly marked as WIP)?
- [ ] Does the feature integrate well with existing code?

## ud83dudd8cufe0f Code Quality

- [ ] Does the code follow our style guidelines (PEP 8 for Python)?
- [ ] Is the code DRY (Don't Repeat Yourself)?
- [ ] Are variable and function names clear and descriptive?
- [ ] Are complex sections well-commented?
- [ ] Are there appropriate docstrings for functions and classes?
- [ ] Has unnecessary commented-out code been removed?

## ud83dudca1 Game Design Considerations

- [ ] Does this change maintain or improve player experience?
- [ ] Is performance considered, especially for rendering and physics?
- [ ] For visual changes, are the aesthetics consistent with our game style?
- [ ] For gameplay changes, is the difficulty appropriate?

## ud83cudfa8 Assets

- [ ] Are new assets placed in the correct directories?
- [ ] Are assets properly optimized?
- [ ] Do assets follow our naming conventions?
- [ ] Are fallbacks implemented for missing assets?

## ud83euddea Testing

- [ ] Has the code been manually tested?
- [ ] Has it been tested on different screen sizes (if UI-related)?
- [ ] Are there automated tests for new functionality (if applicable)?
- [ ] Do existing tests still pass?

## ud83dudcdd Documentation

- [ ] Is the code self-documenting where possible?
- [ ] Are complex algorithms explained in comments?
- [ ] Has the README been updated (if applicable)?
- [ ] Is the CHANGELOG updated?

## ud83dudd12 Security and Error Handling

- [ ] Is user input validated appropriately?
- [ ] Are potential exceptions caught and handled?
- [ ] Does the error handling provide useful feedback?
- [ ] Are debug logs appropriate (not too verbose, not too sparse)?

## ud83dudd27 Maintenance

- [ ] Is the code maintainable by other team members?
- [ ] Would a new contributor understand what this code does?
- [ ] Are magic numbers and strings avoided in favor of constants?
- [ ] Are dependencies managed properly?

---

### After Merging:

- [ ] Have you tested the feature on the target branch?
- [ ] Is documentation updated?
- [ ] If applicable, has the VERSION file been updated?
- [ ] Should this change be highlighted in release notes?
