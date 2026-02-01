# Releasing Postlette

Short checklist for the tag-driven release workflow.

## One-time setup

- Enable GitHub Actions for the repo.
- Configure PyPI Trusted Publishing (OIDC):
  - Repository: `owner/repo`
  - Workflow: `release.yml`
  - Optional: environment name if you use protected environments
- First-time publish requires creating the project on PyPI:
  - Option A: publish to TestPyPI first, then to PyPI.
  - Option B: publish directly to PyPI once from your machine to create the project.
  - After the project exists, enable Trusted Publishing for it (no GitHub secret needed).

## Each release

1. Update `pyproject.toml` version (SemVer).
2. Commit the version bump.
3. Create and push a tag that matches the version:
   - Example: `v0.2.0`
4. Wait for the `Release` workflow to finish.

## First-time publish (local)

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

## Optional: TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

## What the workflow does

- Builds Windows and macOS PyInstaller artifacts.
- Generates SHA-256 checksums.
- Creates a GitHub Release with auto-generated notes.
- Publishes sdist/wheel to PyPI.

Notes:
- Windows build uses `docs/images/logo-dark-navy.ico` as the app icon.
- macOS build uses `docs/images/logo-dark-navy.icns` as the app icon.
