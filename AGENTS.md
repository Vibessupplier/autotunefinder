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

- Treat the user as the product owner and the agent as the technical lead. Discuss
  product and architecture decisions instead of imposing them.
- The product owner is an experienced music producer but is new to programming.
  Never assume knowledge of Python, terminals, virtual environments,
  dependencies, classes, or software architecture.
- Explain important decisions in plain language and connect technical concepts
  to a concrete product benefit. Avoid detached programming lessons.
- Give honest technical and product feedback. Do not agree with an idea when it
  would damage maintainability, UX, security, SEO, or future scalability.
- Work in small, verifiable increments: objective, small change, test, commit,
  push.
- Finish and verify one feature before starting another.
- Prefer sessions that end with a visible, working product improvement.
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
- Keep waveform selection in the UI, but perform sample extraction and export
  through reusable product-level functions backed by `audio_engine.py`.

## Current application structure

- `app.py`: application entry point and multipage navigation.
- `audio_analysis.py`: key, BPM, and Camelot analysis logic.
- `audio_engine.py`: reusable FFmpeg runner and processing errors.
- `audio_effects.py`: reusable product-level audio transformations.
- `stem_separation.py`: product-level local and cloud vocal separation.
- `cloud_stem_separation.py`: private Modal vocal separation client.
- `modal_vocal_split_server.py`: private zero-retention Modal GPU server.
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

- Nightcore-style and Slowed-style transformations are now modes of the shared
  Speed Changer rather than separate duplicated processing engines.
- The Speed Changer supports exact target BPM, pitch following speed, preserved
  original pitch, and independent pitch adjustment.
- Vocal Split supports a selectable local 20-second preview, and its private
  Modal GPU processing service is being connected to the application.
- Keep pitch and tempo processing reusable so future focused, SEO-friendly tool
  pages can share the same engine without duplicating logic.
- Plan Audio Chopper as a focused Pro tool with a waveform, user-selected start
  and end points, fragment preview, and sample export. Do not duplicate its
  trimming engine inside the page.
- Defer accounts, subscriptions, billing, and persistent user files until their
  product and infrastructure requirements are designed.
