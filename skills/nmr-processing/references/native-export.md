# Unchanged whole-page MNOVA export

Use this route for already selected manual results, regardless of whether their scientific processing history has been independently reviewed. Exporting them does not certify that history. No automatic rephasing, baseline correction, referencing, peak picking, integration, zoom restoration or structure insertion belongs here.

## Prepare

Find the actual executable and the scripts directory recognized by the target Mnova installation. Prefer user-provided paths or installed application information; do not assume a username, drive, version or universal scripting directory. Record version, license status and scripting capability from actual evidence. A discovered executable alone means only `FOUND`, not `READY`.

If the installed scripts directory is not writable, discover the application's user scripts folder instead of changing installation permissions. On Windows a candidate is the current user's `%APPDATA%/Mestrelab Research S.L/MestReNova/scripts`; confirm that this installation loads scripts there before using it. Other systems use the folder exposed by their installed application. Keep this machine-specific choice in the job report.

```text
python3 -B /path/to/skill/scripts/prepare_export.py --input selected.mnova --output new-export-job --software /path/to/native/executable
```

The command creates a byte-identical working copy, manifest, unique QS function and UTF-8 job file. It does not launch software or test the native file. Leave the prepared job in its original location during execution; paths are generated for that target machine. Regenerate after moving it.

## Execute on Windows

First run `scripts/probe_environment.ps1 -Software <actual executable> -ScriptsDirectory <actual scripts directory>`. It reads file version and command availability without launching software. It does not establish a license or QS API readiness. Hashing in the runner uses .NET SHA-256 rather than `Get-FileHash`, so it does not depend on that cmdlet's module import. If other required commands are unavailable, report the host/PowerShell versions; diagnose within the task process, without changing global module paths.

```powershell
& '/path/to/skill/scripts/run_export.ps1' -JobDirectory 'new-export-job' -Software 'actual/MestReNova.exe' -ScriptsDirectory 'actual/Mnova/scripts'
```

The runner temporarily places one unique QS file in the supplied Mnova scripts directory, invokes `--sf <function> -w`, and removes only that file after process exit. It does not alter configuration or replace existing scripts. If the application is open it stops without terminating it. When normal closing cannot finish, it leaves its process and script intact for inspection. Do not start another attempt until the previous application session is resolved. Jobs with an existing attempt or output report cannot be rerun; prepare a new job.

The candidate QS uses `serialization.open`, `DocumentWindow`, page activation, `Page.toPixmap(300)` and native NMR metadata reads. Test these on a representative real file in the target version. A missing API or ignored command-line argument is a failed native probe, not justification for falling back to spectrum-only screenshots. No macOS/Linux launcher is bundled.

## Verify

```text
python3 -B /path/to/skill/scripts/verify_export.py new-export-job --record
```

This checks both input hashes, job/source linkage, non-saving report, log, success marker, page sequence and PNG structure/CRC. It returns `NEEDS_VISUAL_REVIEW`, even when technical evidence passes. It does not decode every image pixel or establish scientific correctness.

The runner records `BLOCKED`, `RUNNING`, `EXITED_UNVERIFIED`, `FAILED` or `CLEANUP_PENDING` in the job manifest and exit evidence in `attempt.json`. `--record` updates that job to `TECHNICAL_PASS` only after successful runner exit and technical checks. Without the switch, verification is read-only. Older jobs without runner exit evidence may have valid export files but retain `process_exit: UNVERIFIED`; never infer completed execution from preparation alone. Technical success does not mark visual or scientific review complete.

For each page, inspect the four edges, tallest peaks, peak/solvent labels, axes, parameter table, structures and actual nucleus/sample mapping. If a thumbnail suggests clipping, inspect the original-resolution region and compare with the source page before declaring an export defect. A peak touching the page boundary may be inherited source layout. Distinguish faithful export from optional layout improvements; unchanged-export mode must not silently repair the source.

Open every exported page to check complete spectrum, structures, parameter text, readability, crop, direction and page mapping. Page and nucleus counts come from native content, not filenames. `Molecule` count zero may mean an embedded structure rather than no structure. Preserve the original page orientation unless the requested deliverable needs a separate transformed copy.

Report `Page.toPixmap(300)` as the requested render call, not as measured 300 dpi. Record the actual PNG pixel dimensions; read its pHYs density or image metadata separately when reporting stored dpi. Metadata density and effective dpi at a chosen placement size are different quantities. If no density is stored, report it as unspecified rather than copying the request argument. Do not resample an unchanged export just to make its metadata match the request.

Accept unchanged export only after process exit, technical checks and visual inspection. Keep source-to-page mapping and native logs. Do not require a signal ledger, reinterpret peaks, or claim native editing/save-reopen validation from a zero-save export.


## Runner completion and startup preflight

The Windows runner uses a Python 3 interpreter (`-Python <executable>`, default `py -3`). Before launching it writes `startup_check.json` using `inspect_script_startup.py`. This checks common top-level side effects in the chosen scripts folder, including named functions called from a top-level try block. It is a limited preflight, not a sandbox. If startup scripts can open/save unrelated files, report BLOCKED and do not launch through a different route to bypass the check. Leave user scripts and configuration unchanged; use a supported isolated software environment only when it is available and verified.

The runner observes the native success report, log, page mapping and PNG checks independently of process exit. After verified export it requests normal closing of only its independently started process. It never force-terminates it. `CLEANUP_PENDING` preserves the export evidence but is not completed native execution; finish that session before preparing another job. `verify_export.py` reports image evidence even if cleanup remains incomplete, while `--record` still requires clean exit. The template requests `Application.quit()` after reporting export; target-version support remains part of the native probe.
