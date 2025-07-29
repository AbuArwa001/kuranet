# 🚀 Contributing to the Online Poll System

Thank you for considering contributing to this project! To ensure a smooth development workflow, we follow the **GitFlow branching strategy** and collaborative coding practices.

---

## 📌 Important: Use Pull Requests Instead of `git flow feature finish`

To ensure compatibility with **protected branches** like `develop`, **do NOT use** `git flow feature finish`. Instead:

✅ **Use a Pull Request (PR)** to merge your feature branch into `develop`.

This prevents merge conflicts and access issues, especially when:

- Branch protections prevent direct pushes to `develop`
- You forget to push your `feature/*` branch before finishing
- You need team reviews or CI approvals

---

### 🔁 Standard Workflow with Pull Requests

1. **Start your feature**  

   ```bash
   git flow feature start my-feature
   ```

2. **Commit your changes**

    ```bash
    git add .
    git commit -m "✨ Add my feature"
    ```

3. **Push your branch to GitHub**

    ```bash
    git push -u origin feature/my-feature
    ```

4. **Open a Pull Request on GitHub**

   - Base: develop

   - Compare: feature/my-feature

5. **Wait for review & CI checks, then merge the PR**

   ```bash

   ```

6. **Delete the local and remote feature branch**

   ```bash
    git branch -d feature/my-feature
    git push origin --delete feature/my-feature
   ```

## 🔀 GitFlow Workflow

### Main Branches

- `main` → **Production-ready code**
- `develop` → **Latest integration of features**

### Supporting Branches

| Type        | Naming Convention | Based On | Merges Into    | Purpose                        |
|-------------|-------------------|----------|----------------|--------------------------------|
| Feature     | `feature/<name>`  | `develop`| `develop`       | New features                   |
| Bugfix      | `bugfix/<name>`   | `develop`| `develop`       | Fix bugs before release        |
| Release     | `release/<x.x.x>` | `develop`| `main`, `develop` | Prepare for release            |
| Hotfix      | `hotfix/<name>`   | `main`   | `main`, `develop` | Critical fix in production     |

---

## 🚨 Branch Rules

✅ DO:

- Branch from `develop` for features/bugfixes
- Create pull requests (PRs) for review before merging
- Ensure your branch is up-to-date before PR
- Follow naming conventions strictly

🚫 DO NOT:

- Push directly to `main` or `develop`
- Use non-standard branch names

---

## ✅ Pull Request Checklist

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] Lint checks pass
- [ ] Branch naming is correct
- [ ] PR is rebased with `develop` (if feature)

---

## 🧪 Running Tests Locally

```bash
# Run all tests before committing
python manage.py test
```

## Run linter

flake8
