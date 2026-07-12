# Contributing

## Development Setup
1. Fork this repository and create a feature branch.
2. Copy `.env.example` to `.env`.
3. Start services with `docker compose up --build`.
4. Validate your changes by calling `/fetch` and checking service logs.

## Pull Request Guidelines
- Keep pull requests focused and small.
- Update `README.md` when behavior, API parameters, or environment variables change.
- Include clear reproduction steps in the PR description.

## Commit Messages
- Use short, imperative commit messages.
- Prefer prefixes like `feat:`, `fix:`, `docs:`, `refactor:`.

## Reporting Issues
When reporting bugs, include:
- Request payload used for `/fetch`
- Expected behavior and actual behavior
- Relevant container logs (`podman compose logs`)
