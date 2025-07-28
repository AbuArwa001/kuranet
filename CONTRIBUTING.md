# 🚀 Contributing to the Online Poll System

Thank you for considering contributing to this project! To ensure a smooth development workflow, we follow the **GitFlow branching strategy** and collaborative coding practices.

---

## 🔀 GitFlow Workflow

### Main Branches:
- `main` → **Production-ready code**
- `develop` → **Latest integration of features**

### Supporting Branches:
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

# Run linter
flake8
