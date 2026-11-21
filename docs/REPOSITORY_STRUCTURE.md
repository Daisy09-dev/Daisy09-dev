# Repository structure

This repository powers the [Daisy09-dev GitHub profile](../README.md). Keep workflow inputs and generated assets in their documented locations so automation continues to work.

| Location | Purpose |
| --- | --- |
| `.github/workflows/` | GitHub Actions: animated portrait, contribution snake, 3D skyline, metrics and activity |
| `assets/` | Images, SVGs and GIFs used by the profile |
| `scripts/` | Build scripts for animated assets |
| `docs/` | GitHub Pages interactive portrait and repository documentation |
| `terminal/` | Standalone terminal animation project |
| `profile-3d-contrib/` | Generated 3D contribution visuals |
| `portrait.txt` | ASCII portrait source used by generators |
| `profile.json`, `render.py` | Legacy terminal-card rendering inputs and script |
| `neofetch-dark.svg`, `neofetch-light.svg` | Generated terminal-card SVGs |
| `publish.sh` | Legacy whole-repository replacement script; **do not run** casually: it deletes tracked files before copying |
| `README.md` | Public profile shown on GitHub |

## Maintenance rules

1. Keep all workflow YAML files under `.github/workflows/`. Some workflows reference paths at the repository root.
2. Do not relocate `portrait.txt`, `profile.json`, `render.py`, or generated assets without updating their consumers.
3. `docs/index.html` is the interactive GitHub Pages site; GitHub profile README itself cannot execute cursor-reactive JavaScript.
4. Keep the `output` branch for contribution snake assets separate from the main source tree.
5. Before removing old-looking files, inspect workflow references and GitHub Pages settings.

## Follow-up cleanup candidates

- Consolidate unused ASCII portrait SVG versions after checking which are referenced.
- Review the two oddly named workflow files ending in `.yml.` before renaming or deleting.
- Retire the legacy `publish.sh` after confirming it is no longer needed.

No files are deleted or moved by this document.
