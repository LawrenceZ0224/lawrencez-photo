# LawrenceZ photography website

Maintain the website in this repository. The user prefers direct local changes and Git synchronization, instead of zip download/upload steps.

- Public deployment target: GitHub Pages, repository `LawrenceZ0224/lawrencez-photo`, branch `main`.
- Navigation: Top, Work, Wandering on Earth, Portrait, Profile, Journal. Top returns to the white entry page and must honor the repository base path.
- Use the user's photographs only. Empty categories remain empty until content is supplied.
- Public website content lives under `content/`; originals and credentials stay outside the repository.
- `scripts/build.py` creates static output in `dist/`. Do not edit generated output as source.
- Run the relevant checks before publishing. Preserve remote history; do not force push or overwrite unrelated local edits.
- `scripts/preview.py` previews local changes. `scripts/publish.py` checks and synchronizes explicitly requested updates.
- Keep source and operating instructions current when workflows change.

- Local photo sources are sibling folders Work, Wandering on Earth, Portrait. import_photos.py prepares managed public copies; never alter original sources.
- Preview and publish prepare photos automatically; Actions builds already committed content only.
- Wandering navigation opens a location menu, then location pages show square thumbnails and a full-ratio white viewer with side arrows and an upper-right close icon.
