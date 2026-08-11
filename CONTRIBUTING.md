# Contributing

Thank you for improving `shuyixiao-agent`. Keep changes focused, testable, and honest about what the code supports.

## Development setup

```bash
git clone https://github.com/shuyixiao-better/shuyixiao-agent.git
cd shuyixiao-agent
python -m venv .venv
# Activate .venv for your platform
python -m pip install -e ".[dev]"
Copy-Item .env.example .env  # PowerShell; use cp on macOS/Linux
```

An API key is optional for offline work. To run model-backed examples, set `GITEE_AI_API_KEY` in the untracked `.env` file.

```bash
python -m pytest
python -m ruff check .
python examples/00_offline_quickstart.py
python run_web.py
```

## Contribution workflow

1. Fork the repository and create a focused branch.
2. Make the smallest change that solves the problem.
3. Add or update tests and documentation when behavior changes.
4. Run the CI-equivalent commands above.
5. Open a pull request using the template.

Use Conventional Commits where practical: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, or `chore:`.

## Pull request requirements

Explain what changed, why it changed, how it was tested, and whether it breaks compatibility. Include screenshots for visible UI changes. Tests must not require paid APIs or real credentials in CI; use a fake provider or mark explicitly online-only tooling outside the default suite.

## Good first contributions

- Correct stale documentation links or unclear examples.
- Add deterministic tests for tools, routing, parsers, memory, or RAG components.
- Improve error messages and type hints in a focused module.
- Add a small tool integration with clear safety boundaries.
- Add an agent-pattern example backed by tests.

For vulnerabilities, do not open a public issue; follow [SECURITY.md](SECURITY.md).
