# Contributing to idea2ui

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/anomalyco/idea2ui.git
cd idea2ui
npm install
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
npm run dev
```

## Project Structure

See [README.md](README.md#project-structure) for the directory layout.

## Coding Guidelines

- **No comments in code** — let the code speak for itself
- **Use `.value` access** for reactive wrappers (e.g., `phase.value === 'idle'`, never `phase === 'idle'`)
- **TypeScript** for all frontend code; **Python type hints** for backend
- **ant-design-vue** components for UI consistency
- **Pure HTML+CSS+JS** output — no framework in generated pages

## Pull Request Process

1. Fork the repo and create a feature branch from `master`
2. Make your changes
3. Run `npm run build` to verify no type or build errors
4. Update any affected documentation
5. Open a PR with a clear description of the changes

## Code of Conduct

Be respectful, constructive, and inclusive. We're all here to learn and build something useful.
