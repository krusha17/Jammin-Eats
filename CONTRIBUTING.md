# 🎮 Contributing to Jammin' Eats

First off, thanks for taking the time to contribute! 🎵 🌴

The following is a set of guidelines for contributing to Jammin' Eats. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 🔄 Git Workflow

We follow a branching model inspired by GitFlow to maintain our code quality and enable parallel development:

### Branch Structure

- `main`: Production-ready code only. Protected branch that only accepts merges from `develop` after thorough testing.
- `develop`: Integration branch where features are combined. This is where most PRs will target.
- `test`: QA branch for testing before promoting to `main`.
- `feature/<name>`: Created from `develop`, used for developing new features (e.g., `feature/new-enemy-type`).
- `bugfix/<name>`: Created from `develop`, used for fixing bugs.
- `hotfix/<name>`: Created from `main`, used for critical fixes that need to be applied directly to production.

### Workflow Steps

1. **Start with an Issue**: All changes should start with an issue describing what needs to be done.
2. **Create a Branch**:
   ```bash
   # For a new feature
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**: Implement your changes with descriptive commits following our commit message format.
4. **Keep Updated**: Regularly sync with the parent branch:
   ```bash
   git fetch origin develop
   git rebase origin/develop
   ```
5. **Open a Pull Request**: When your changes are ready, open a PR to the `develop` branch.
6. **Code Review**: Address any feedback from reviewers.
7. **Merge**: Once approved, your PR will be merged.

## 💾 Commit Message Format

We follow a structured commit message format to make our history readable and to automate versioning:

```
<type>(<scope>): <subject>
```

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or improving tests
- `chore`: Changes to the build process, tools, etc.

**Example**:
```
feat(customer): add new customer animation system
```

## 🖌️ Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Comment complex logic and include docstrings for functions and classes
- Organize code in a modular fashion as per our project structure

## 🧪 Testing

- Write tests for new features when possible
- Manually test your changes thoroughly
- Ensure existing tests pass before submitting a PR

## 🎨 Asset Contribution

For sprites, sounds, and other assets:

- Place them in the appropriate subdirectory within `assets/`
- Provide source files when possible (e.g., .psd files for sprites)
- Follow the existing naming conventions
- Consider performance implications (optimize file sizes)

## 🚀 Release Process

1. Features are merged into `develop`
2. When ready for a release, `develop` is merged to `test` for QA
3. After testing, `test` is merged to `main`
4. The release is tagged with a version number (e.g., v0.1.0)
5. GitHub Actions builds release artifacts automatically

## ❓ Questions?

Feel free to ask for help in the issues or discussions section!

Stay Jammin'! 🌴🎵🍍🚚
