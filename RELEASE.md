# Release process

The project has no fabricated historical releases. When a maintainer is ready to publish one:

1. Ensure `main` is green and the worktree is clean.
2. Review `CHANGELOG.md`; move relevant Unreleased entries under a real version and date.
3. Update the version in `pyproject.toml` and `src/shuyixiao_agent/__init__.py` together.
4. Run `python -m ruff check .`, `python -m pytest`, `python -m compileall -q src examples evals`, and `python -m build`.
5. Install the generated wheel in a clean environment and run the offline quick start.
6. Create a signed or annotated tag such as `v0.1.0` and push it.
7. Create a GitHub Release from that tag using the changelog as release notes.

Do not publish until package ownership, credentials, artifact contents, and installation from the built wheel have been verified by a maintainer.
