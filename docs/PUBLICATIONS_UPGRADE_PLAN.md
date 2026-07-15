# NasCOHST Publications Upgrade

## Goal

Transform the current News module into a modern institutional publishing platform capable of supporting:

- College News
- Academic Articles
- Research Publications
- Health Education
- Press Releases
- Announcements

Development will be done incrementally with backward compatibility.

## Phase 1: Editorial authorship

This phase adds multi-author support without removing the existing `News.author`
field.

### New relationship model

- `News` remains the publication record.
- `PublicationAuthor` now represents one author row per publication.
- `PublicationAuthor.publication` links back to `News`.
- `PublicationAuthor.staff` optionally links to an internal `Staff` record.
- `PublicationAuthor.external_name`, `affiliation`, `email`, and `orcid`
  support external researchers.

### Backward compatibility

The legacy `News.author` field is preserved because:

- existing templates and queries still depend on it
- production data already uses it
- it provides a safe fallback while the editorial workflow is expanded

On save, a publication with only a legacy `News.author` value will receive a
matching `PublicationAuthor` row so new templates can render authors through the
new model.

### Migration strategy

- only forward migrations are added
- existing migrations are not modified
- a data migration backfills `PublicationAuthor` rows from legacy `News.author`
- the migration is safe for both PostgreSQL and SQLite

### Future expansion

This structure leaves room for later additions such as:

- peer review assignments
- reviewer reports
- editorial decisions
- submission / revision status tracking
- author contribution metadata

### Citation helper intent

Helper methods on `News` now centralize author rendering:

- `primary_author()`
- `corresponding_author()`
- `author_list()`
- `citation_authors()`
- `has_external_authors()`

These keep templates simple and avoid repeating author-selection logic in
multiple places.
