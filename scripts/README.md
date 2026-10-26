# scripts

Everything visual on the profile is generated here. Edit the content at the top of a script,
push, and the `Build profile graphics` workflow rebuilds and commits the SVGs.

| script | builds | edit this to change |
|---|---|---|
| `update_card.py` | `dark_mode.svg`, `light_mode.svg` (terminal card, live stats) | `INFO`, `CONTACT`, `SCENES` |
| `build_ascii.py` | `ascii_*.txt` used by the card | drop a photo at `assets/me.jpg` for a portrait |
| `build_buttons.py` | `assets/buttons/` | `LINKS` |
| `build_talks.py` | `assets/talks/` | `TALKS` |
| `build_sphere.py` | `assets/stack-sphere-*.svg`, `docs/index.html` | `STACK` (icons in `icons/`) |
| `build_activity.py` | `assets/activity-*.svg`, `assets/stats-*.svg` | needs `GITHUB_TOKEN`, or `--preview DIR` |

Local run: `pip install fonttools brotli pillow`, then any script with `python3 scripts/<name>.py`.
Fonts: JetBrains Mono and Inter (SIL OFL), subset into each SVG. Icon sources: `icons/SOURCES.md`.
