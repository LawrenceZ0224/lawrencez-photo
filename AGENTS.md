# LawrenceZ photography website

Maintain the website in this repository. The user prefers direct local changes and Git synchronization, instead of zip download/upload steps.

- Public deployment target: GitHub Pages, repository `LawrenceZ0224/lawrencez-photo`, branch `main`.
- Navigation: Top, Portfolio, Wandering on Earth, Portrait, Profile, Journal. Top returns to the white entry page; ENTER SITE and the brand lead to Portfolio. All routes honor the repository base path. Work content stays available but is excluded from navigation.
- Use the user's photographs only. Empty categories remain empty until content is supplied.
- Public website content lives under `content/`; originals and credentials stay outside the repository.
- `scripts/build.py` creates static output in `dist/`. Do not edit generated output as source.
- Run the relevant checks before publishing. Preserve remote history; do not force push or overwrite unrelated local edits.
- `scripts/preview.py` previews local changes. `scripts/publish.py` checks and synchronizes explicitly requested updates.
- Keep source and operating instructions current when workflows change.

- Local photo sources are sibling folders Wandering on Earth and Portrait, with optional Work, Film, Vignettes and Profile. A missing optional source preserves its existing published content. import_photos.py prepares managed public copies; never alter original sources.
- Preview and publish prepare photos automatically; Actions builds already committed content only.
- Wandering navigation opens a location menu, then location pages show square thumbnails and a full-ratio white viewer with side arrows and an upper-right close icon.

- Portfolio links to Photoset, Portrait, Wandering on Earth (directly to wandering/singapore/) and Film; Vignettes replaces Landscape and opens its gallery directly at /vignettes/. Photoset is a three-column catalog of existing portrait series (catalogTitle or Series 01/02); Film has a three-column catalog and an original-ratio viewer with active square thumbnails. Cover selection uses portfolioCovers in content/site.json and original filenames recorded by the importer.
- Profile has an uncropped portrait on a light gray background and a blank white biography panel until text is supplied. Mobile stacks portrait before biography. profilePhotoSource selects a file from the sibling Profile folder, imported to content/profile/photo.jpg.

- Portrait public routes use ordered numbers (wsy → portrait/01/, anqi → portrait/02/); source folder names stay local identifiers. Preserve redirects from legacy folder-name URLs. Public page titles use catalogTitle or Series 01/02.

- Vignettes imports photos directly from the sibling Vignettes folder into content/vignettes/main. It uses the Film thumbnail viewer with a Portfolio return link. Into the Mist.jpg is the Portfolio cover and first image; never restructure or rename the user’s original folder.
