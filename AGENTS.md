# Vibes Supplier — Project Instructions

## Product direction

- Build a maintainable SaaS platform of focused audio tools for producers, DJs,
  and artists.
- Treat the name "Vibes Supplier" as provisional.
- Do not use "Auto-Tune" or "AutoTune" as product branding because it is a
  third-party trademark.
- Each tool must have its own page and search-focused purpose. Do not combine
  every feature into one large page.

## Working style

- The product owner is new to programming. Explain important decisions in plain
  language without hiding relevant technical tradeoffs.
- Work in small, verifiable increments: objective, small change, test, commit,
  push.
- Finish and verify one feature before starting another.
- Prefer a durable design over a quick workaround.
- Challenge product or technical ideas that would create security,
  maintainability, UX, or scaling problems.
- Do not perform broad refactors unless they are required for the current
  increment and explained first.

## Architecture

- Keep Streamlit pages focused on presentation and user interaction.
- Keep audio analysis, transformations, and infrastructure outside the UI.
- Use `audio_engine.py` as the low-level FFmpeg execution layer.
- Use `audio_effects.py` for product-level transformations such as Nightcore.
- UI code must call product-level functions; it must not construct raw FFmpeg
  commands or filters.
- Use FFmpeg as the shared processing engine for pitch, tempo, format conversion,
  export, and related effects.
- Never invoke FFmpeg through `shell=True`. Pass command arguments as a list.
- Validate user-controlled values before passing them to the processing layer.
- Use temporary storage for uploaded and generated audio. Do not retain user
  audio after processing unless persistent storage is intentionally designed.

## Current application structure

- `app.py`: current key and BPM analysis page.
- `audio_analysis.py`: key, BPM, and Camelot analysis logic.
- `audio_engine.py`: reusable FFmpeg runner and processing errors.
- `audio_effects.py`: reusable product-level audio transformations.
- `ui.py`: shared Streamlit presentation helpers.
- `pages/`: independent Streamlit tool pages.
- `tests/`: automated tests.
- `requirements.txt`: Python dependencies for local and cloud environments.
- `packages.txt`: system packages required by Streamlit Community Cloud.

## Quality rules

- Preserve existing working behavior unless the current task explicitly changes
  it.
- Add or update tests for processing behavior and regressions.
- Run the relevant automated tests before committing.
- Run Python syntax checks and `git diff --check` before committing.
- Keep commits small and focused on one working increment.
- Do not commit generated audio, temporary files, secrets, credentials, virtual
  environments, or Python cache files.
- Do not add a production dependency without explaining why it is needed.

## Deployment

- The application deploys from the `main` branch to Streamlit Community Cloud.
- Remember that local Homebrew packages are not available in the cloud;
  required Debian packages belong in `packages.txt`.
- A successful local test does not replace checking the Streamlit deployment
  logs and the published user flow after pushing.

## Near-term direction

- Complete and validate Nightcore before starting another generator.
- Keep pitch-only and tempo-only processing separate from Nightcore so the same
  primitives can support future Pitch Changer and Tempo Changer pages.
- Defer accounts, billing, persistent user files, background jobs, and stem
  splitting until their product and infrastructure requirements are designed.
