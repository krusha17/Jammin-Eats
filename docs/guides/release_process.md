# ud83dude80 Jammin' Eats Release Process

This document outlines our release process for Jammin' Eats, ensuring consistent and reliable game releases.

## ud83dudcc6 Release Schedule

We follow a versioned release cycle:

- **Major releases** (1.0.0): Significant game milestones with substantial new content.
- **Minor releases** (0.1.0): New features, levels, or gameplay elements.
- **Patch releases** (0.0.1): Bug fixes and small improvements.

## ud83dudcca Versioning

We follow [Semantic Versioning](https://semver.org/) with MAJOR.MINOR.PATCH format:

- **MAJOR**: Breaking changes or significant milestones
- **MINOR**: New features in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

## ud83dude9b Release Branch Workflow

1. When ready for a release, create a `release/vX.Y.Z` branch from `develop`
2. Make only bug fixes and release-specific changes on this branch
3. Merge to `test` for final QA
4. Once approved, merge to `main` and tag with version number
5. Merge back to `develop` to incorporate any release fixes

## ud83dudd16 Pre-Release Checklist

- [ ] All targeted features are complete and in `develop`
- [ ] VERSION file is updated
- [ ] CHANGELOG.md is updated with all changes
- [ ] All tests pass
- [ ] Game has been playtested on target platforms
- [ ] Release branch has been created
- [ ] Release notes are prepared

## ud83dudce6 Building a Release

1. Ensure you're on the `main` branch after the release PR has been merged
2. Tag the release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. Push the tag: `git push origin vX.Y.Z`
4. GitHub Actions will automatically build the release assets

## ud83dudd25 Post-Release

1. Create a GitHub Release with the release notes
2. Upload the built executable as an asset (if not done by GitHub Actions)
3. Announce the release to players
4. Monitor for critical issues

## ud83dudd04 Hotfix Process

For critical issues in production:

1. Create a `hotfix/vX.Y.Z+1` branch from `main`
2. Fix the issue
3. Update VERSION and CHANGELOG
4. Merge to `main` AND `develop` with a new version tag

## ud83dudcdd Release Notes Template

```markdown
# Jammin' Eats vX.Y.Z

## What's New
- Feature 1
- Feature 2

## Improvements
- Improvement 1
- Improvement 2

## Bug Fixes
- Fixed issue 1
- Fixed issue 2

## Known Issues
- Known issue 1
- Known issue 2
```

---

This process ensures our releases are consistent, well-tested, and properly documented.
