# Validation on a new project or computer

Run `python3 -B -m unittest discover -s /path/to/skill/scripts/tests -v` outside the originating project. Fixtures are synthetic bytes and metadata, not valid MNOVA containers or acquired spectra. They prove file-handling contracts only.

Use different project roots, including spaces and non-ASCII characters. Test missing software/input, incorrect hashes/nucleus, shared ZIP mappings, conflicting output locations, existing outputs and invalid archive paths. Confirm inputs unchanged. Same-computer directory tests do not prove another operating system, native software version or license works.

Before native production, use independently selected real material whose provenance and expected content are known:

| Case | Acceptance |
|---|---|
| Processed manual MNOVA with more than one page | Native page mapping; complete images; source/copy hashes unchanged; no save; visual review |
| A genuine raw 1D acquisition | Correct metadata/import and appropriate processing/reference; native save-close-reopen; scientifically reviewed spectrum |
| Missing/ambiguous identity or reference | Affected interpretation explicitly unresolved; no invented assignment or silent source substitution |
| Display edit | Only requested changes; protected scientific values compared before/after and after reopen |
| Unavailable software or unsupported API | Specific failure; no claim of completed native processing |

Record version, OS, actual command/API, input hashes, logs, native files and observed results in that project's run directory. New platform support requires its own evidence. Package tests and static checks never substitute for these native/scientific checks.

## Revision 0.2.0 focused checks

Runner state: prepare stays NOT_RUN; successful exit stays EXITED_UNVERIFIED until --record verifies evidence; timeout/failure cannot become technical/native success. Inspect original-resolution boundaries when thumbnails are ambiguous.

Treat scripts added in 0.2.0 as target-installation probes; consult their actual task logs. Package tests do not certify arbitrary native inputs or other computers.
