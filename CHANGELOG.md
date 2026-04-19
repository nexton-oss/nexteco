# Changelog

## 0.3.0

- added `nexteco measure -- <command>` functionality to natively benchmark empirical OS power and energy
- implemented background metrology pipelines abstracting `powermetrics` (macOS), `turbostat` (Linux), and `typeperf` (Windows) 
- rewired `core.md`, `advanced.md`, and `SKILL.md` logic to instruct AI agents to leverage the `measure` pipeline organically
- added strict PEP8 code formatting and continuous linting enforcement via Ruff
- resolved manual `sudo` inconsistencies natively across examples and documentation routines

## 0.2.0

- repositioned NextEco as a two-form product: OSS repository + embedded skill
- added `skill/nexteco/` as the agent-native execution layer
- upgraded repository structure for public GitHub publication
- improved `core.md` and `advanced.md`
- added project documentation under `docs/`
- added GitHub workflows and issue templates
- kept the Python CLI as the reference implementation
- preserved the core doctrine: small, explicit, auditable, honest

## 0.1.0

- initial CLI and YAML/report workflow
- starter templates
- validation and rendering
- tests and examples
