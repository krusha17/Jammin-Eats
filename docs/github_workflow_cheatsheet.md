# 🚦 GitHub Workflow Cheat Sheet

## 🏁 Branching Model

- **main** – Stable, production-ready code (releases only)
- **develop** – Latest development version (features merged here)
- **test** – QA/integration testing before release
- **feature/xyz** – New features (branched from develop)
- **bugfix/xyz** – Bug fixes (branched from develop)
- **hotfix/xyz** – Urgent production fixes (branched from main)

---

## 🛠️ Daily Workflow

### 1. Sync develop branch
```sh
git checkout develop
git pull origin develop
```

### 2. Create a feature branch
```sh
git checkout -b feature/your-feature-name
```

### 3. Work & Commit
- Make changes, test locally.
- Commit often with clear messages:
  ```sh
  git add .
  git commit -m "feat: add new food physics"
  ```

### 4. Push feature branch to GitHub
```sh
git push -u origin feature/your-feature-name
```

### 5. Create a Pull Request (PR)
- Go to GitHub, open a PR from your feature branch → `develop`
- Fill out the PR template, request review

### 6. Code Review & Merge
- Address feedback, push more commits if needed.
- Once approved, merge into `develop`.

---

## 🧪 Integration & Release

### 7. QA Testing
- When ready, merge `develop` → `test` for integration/QA.
- Playtest and bug hunt on `test`.

### 8. Release
- After QA, merge `test` → `main`.
- Tag a release on `main`.

---

## 🏷️ Release Tagging

```sh
git checkout main
git pull origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

---

## 🔄 Hotfixes

- For urgent fixes, branch from `main`:
  ```sh
  git checkout main
  git pull origin main
  git checkout -b hotfix/critical-fix
  # fix, commit, push, PR to main
  ```

---

## 🚨 Golden Rules

- **Never work directly on main or develop!**
- **Always branch from develop for features/bugfixes.**
- **Use PRs for all merges.**
- **Keep branches and PRs focused and small.**
- **Update your branch with latest develop before merging.**
- **Use the PR and issue templates for consistency.**

---

## 📋 Visual Diagram

```text
main  <---------  test  <---------  develop  <---------  feature/xyz
  ^         ^           ^                         ^
  |         |           |                         |
hotfix/xyz  |     bugfix/xyz, feature/xyz         |
            |                                     |
         (merge, PR, QA, release)             (branch, PR)
```
