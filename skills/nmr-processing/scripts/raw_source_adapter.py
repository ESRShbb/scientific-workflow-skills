# -*- coding: utf-8 -*-
"""Inventory and materialize controlled NMR spectrum sources.

This module never processes spectra.  It normalizes file-backed MNOVA/1r
sources and Bruker ZIP/folder packages into explicit, hash-locked provenance
records.  ZIP/folder materialization is allowed only below a caller-provided
task work directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ALLOWED_SOURCE_KINDS = {
    "mnova_container",
    "bruker_zip",
    "bruker_folder",
    "bruker_1r",
    "independent_raw",
}
ALLOWED_NUCLEI = {"1H", "13C", "19F"}
ALLOWED_PROCESSING_PROFILES = {"curate_existing", "process_from_raw"}


class RawSourceError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _canonical_rows(rows: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    ordered = sorted(rows, key=lambda row: str(row["relative_path"]).casefold())
    text = "".join(
        f"{row['relative_path']}\t{row['size']}\t{row['sha256']}\n" for row in ordered
    )
    return ordered, hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def _is_reparse(path: Path) -> bool:
    info = path.lstat()
    attrs = getattr(info, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attrs & reparse)


def directory_manifest(root: Path) -> dict[str, Any]:
    _check_path(root)
    root = root.resolve()
    if not root.is_dir():
        raise RawSourceError(f"Bruker folder missing: {root}")
    rows: list[dict[str, Any]] = []
    seen = set()
    for path in sorted(root.rglob("*"), key=lambda item: str(item).casefold()):
        if _is_reparse(path):
            raise RawSourceError(f"Bruker folder contains reparse point: {path}")
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        _safe_member_name(rel)
        if rel.casefold() in seen:
            raise RawSourceError(f"case-colliding source files: {rel}")
        seen.add(rel.casefold())
        rows.append({"relative_path": rel, "size": path.stat().st_size, "sha256": sha256_file(path)})
    if not rows:
        raise RawSourceError(f"Bruker folder contains no files: {root}")
    ordered, tree_sha = _canonical_rows(rows)
    return {
        "schema_version": "nmr-directory-manifest.v1",
        "root": str(root),
        "file_count": len(ordered),
        "files": ordered,
        "tree_sha256": tree_sha,
    }


def _zip_member_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def _safe_member_name(name: str) -> str:
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in normalized.split('/')):
        raise RawSourceError(f"unsafe ZIP member path: {name}")
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{s}{i}' for s in ('COM', 'LPT') for i in range(1, 10)}
    for part in pure.parts:
        if any(c in part for c in ':<>"|?*') or any(ord(c) < 32 for c in part) or part.endswith((' ', '.')) or part.split('.')[0].upper() in reserved:
            raise RawSourceError(f"unsafe ZIP member path: {name}")
    return pure.as_posix()


def _check_path(path: Path) -> None:
    for item in (path.absolute(), *path.absolute().parents):
        if (item.exists() or item.is_symlink()) and _is_reparse(item):
            raise RawSourceError(f"linked/reparse path is not supported: {item}")


def validate_output(path: Path, sources: Iterable[Path]) -> None:
    _check_path(path)
    target = path.resolve()
    if target.exists():
        raise RawSourceError(f"output already exists: {target}")
    for source in sources:
        source = source.resolve()
        if target == source or source in target.parents or target in source.parents:
            raise RawSourceError(f"output overlaps input: {target}")


def zip_manifest(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise RawSourceError(f"invalid Bruker ZIP: {path}")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            safe = _safe_member_name(info.filename.rstrip("/")) if info.filename.rstrip("/") else ""
            if not safe or info.is_dir():
                continue
            folded = safe.casefold()
            if folded in seen:
                raise RawSourceError(f"duplicate normalized ZIP member: {safe}")
            seen.add(folded)
            if _zip_member_is_symlink(info):
                raise RawSourceError(f"ZIP member is a symbolic link: {safe}")
            digest = hashlib.sha256()
            with archive.open(info) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            rows.append(
                {
                    "relative_path": safe,
                    "size": info.file_size,
                    "sha256": digest.hexdigest().upper(),
                    "crc32": f"{info.CRC:08X}",
                }
            )
    ordered, member_sha = _canonical_rows(rows)
    return {
        "schema_version": "nmr-zip-member-manifest.v1",
        "path": str(path),
        "sha256": sha256_file(path),
        "file_count": len(ordered),
        "files": ordered,
        "member_manifest_sha256": member_sha,
    }


def _parse_jcamp_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        if not raw.startswith("##$") or "=" not in raw:
            continue
        key, value = raw[3:].split("=", 1)
        values[key.strip()] = value.strip().strip("<>")
    return values


def _parse_jcamp(path: Path) -> dict[str, str]:
    return _parse_jcamp_text(path.read_text(encoding="latin-1", errors="replace"))


def _normalise_nucleus(value: str) -> str:
    token = value.strip().replace("^", "")
    if token in ALLOWED_NUCLEI:
        return token
    raise RawSourceError(f"unsupported or missing Bruker NUC1: {value!r}")


def discover_experiments(root: Path, pdata_procno: str = "1") -> list[dict[str, Any]]:
    root = root.resolve()
    experiments: list[dict[str, Any]] = []
    for acqus in sorted(root.rglob("acqus"), key=lambda item: str(item).casefold()):
        exp_dir = acqus.parent
        fid = exp_dir / "fid"
        if not fid.is_file():
            continue
        params = _parse_jcamp(acqus)
        nucleus = _normalise_nucleus(params.get("NUC1", ""))
        proc_dir = exp_dir / "pdata" / str(pdata_procno)
        procs = proc_dir / "procs"
        one_r = proc_dir / "1r"
        experiments.append(
            {
                "experiment_id": exp_dir.name,
                "relative_root": exp_dir.relative_to(root).as_posix(),
                "nucleus": nucleus,
                "nuc2": params.get("NUC2", ""),
                "solvent": params.get("SOLVENT", ""),
                "sfo1_mhz": float(params["SFO1"]) if params.get("SFO1") else None,
                "number_of_scans": int(float(params["NS"])) if params.get("NS") else None,
                "pulse_program": params.get("PULPROG", ""),
                "fid": {"path": str(fid), "sha256": sha256_file(fid), "size": fid.stat().st_size},
                "acqus": {"path": str(acqus), "sha256": sha256_file(acqus), "size": acqus.stat().st_size},
                "pdata_procno": str(pdata_procno),
                "processed_1r": (
                    {"path": str(one_r), "sha256": sha256_file(one_r), "size": one_r.stat().st_size}
                    if one_r.is_file()
                    else None
                ),
                "procs": (
                    {"path": str(procs), "sha256": sha256_file(procs), "size": procs.stat().st_size}
                    if procs.is_file()
                    else None
                ),
            }
        )
    if not experiments:
        raise RawSourceError(f"no Bruker experiments containing acqus+fid under {root}")
    return experiments


def discover_zip_experiments(path: Path, pdata_procno: str = "1") -> list[dict[str, Any]]:
    experiments: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        names = {info.filename.rstrip("/").replace("\\", "/"): info for info in archive.infolist() if not info.is_dir()}
        for name in sorted((item for item in names if item.endswith("/acqus") or item == "acqus"), key=str.casefold):
            exp_root = name.rsplit("/", 1)[0] if "/" in name else ""
            fid_name = f"{exp_root}/fid" if exp_root else "fid"
            if fid_name not in names:
                continue
            params = _parse_jcamp_text(archive.read(names[name]).decode("latin-1", errors="replace"))
            nucleus = _normalise_nucleus(params.get("NUC1", ""))
            proc_root = f"{exp_root}/pdata/{pdata_procno}" if exp_root else f"pdata/{pdata_procno}"
            one_r_name = f"{proc_root}/1r"
            procs_name = f"{proc_root}/procs"

            def member_record(member_name: str) -> dict[str, Any] | None:
                info = names.get(member_name)
                if info is None:
                    return None
                data = archive.read(info)
                return {"member_path": member_name, "sha256": hashlib.sha256(data).hexdigest().upper(), "size": len(data)}

            experiments.append(
                {
                    "experiment_id": PurePosixPath(exp_root).name,
                    "relative_root": exp_root,
                    "nucleus": nucleus,
                    "nuc2": params.get("NUC2", ""),
                    "solvent": params.get("SOLVENT", ""),
                    "sfo1_mhz": float(params["SFO1"]) if params.get("SFO1") else None,
                    "number_of_scans": int(float(params["NS"])) if params.get("NS") else None,
                    "pulse_program": params.get("PULPROG", ""),
                    "fid": member_record(fid_name),
                    "acqus": member_record(name),
                    "pdata_procno": str(pdata_procno),
                    "processed_1r": member_record(one_r_name),
                    "procs": member_record(procs_name),
                }
            )
    if not experiments:
        raise RawSourceError(f"no Bruker experiments containing acqus+fid in {path}")
    return experiments


def _choose_experiment(experiments: list[dict[str, Any]], experiment_id: str, nucleus: str) -> dict[str, Any]:
    matches = [item for item in experiments if item["experiment_id"] == str(experiment_id)]
    if len(matches) != 1:
        raise RawSourceError(f"experiment_id={experiment_id!r} matches={len(matches)}")
    selected = matches[0]
    if selected["nucleus"] != nucleus:
        raise RawSourceError(
            f"Bruker nucleus mismatch experiment={experiment_id} expected={nucleus} actual={selected['nucleus']}"
        )
    return selected


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _copy_folder(source: Path, destination: Path) -> None:
    if destination.exists():
        raise RawSourceError(f"raw work destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, copy_function=shutil.copy2)


def _extract_zip(source: Path, destination: Path) -> None:
    if destination.exists():
        raise RawSourceError(f"raw work destination already exists: {destination}")
    destination.mkdir(parents=True)
    target_root = destination.resolve()
    with zipfile.ZipFile(source) as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            raw_name = info.filename.rstrip("/")
            if not raw_name:
                continue
            safe = _safe_member_name(raw_name)
            folded = safe.casefold()
            if folded in seen:
                raise RawSourceError(f"duplicate normalized ZIP member: {safe}")
            seen.add(folded)
            if _zip_member_is_symlink(info):
                raise RawSourceError(f"ZIP member is a symbolic link: {safe}")
            target = (target_root / Path(*PurePosixPath(safe).parts)).resolve()
            if os.path.commonpath([str(target), str(target_root)]) != str(target_root):
                raise RawSourceError(f"ZIP member escapes work directory: {safe}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)


def inspect_spectrum_source(source: dict[str, Any], expected_nucleus: str, materialize_root: Path | None = None) -> dict[str, Any]:
    if not source.get('path'):
        raise RawSourceError('missing source path')
    _check_path(Path(source['path']))
    if materialize_root is not None:
        _check_path(materialize_root)
        src_path = Path(source['path']).resolve()
        dest_path = materialize_root.resolve()
        if dest_path == src_path or src_path in dest_path.parents or dest_path in src_path.parents:
            raise RawSourceError('materialization overlaps input')
    nucleus = str(source.get("nucleus") or expected_nucleus)
    if nucleus != expected_nucleus or nucleus not in ALLOWED_NUCLEI:
        raise RawSourceError(f"source nucleus mismatch key={expected_nucleus} declared={nucleus}")
    kind = str(source.get("source_kind") or "")
    if kind not in ALLOWED_SOURCE_KINDS:
        raise RawSourceError(f"unsupported source_kind: {kind or 'missing'}")
    profile = str(source.get("processing_profile") or ("process_from_raw" if kind in {"bruker_zip", "bruker_folder"} else "curate_existing"))
    if profile not in ALLOWED_PROCESSING_PROFILES:
        raise RawSourceError(f"unsupported processing_profile: {profile}")
    path = Path(str(source.get("path") or "")).resolve()
    if kind == "bruker_folder":
        manifest = directory_manifest(path)
        expected_sha = str(source.get("sha256") or "").upper()
        if not expected_sha or manifest["tree_sha256"] != expected_sha:
            raise RawSourceError(f"directory tree SHA drift expected={expected_sha} actual={manifest['tree_sha256']}")
        if profile != "process_from_raw":
            raise RawSourceError("bruker_folder requires processing_profile=process_from_raw")
        work = path
        if materialize_root is not None:
            work = materialize_root.resolve() / f"folder_{manifest['tree_sha256'][:16]}"
            _copy_folder(path, work)
            if directory_manifest(work)['tree_sha256'] != manifest['tree_sha256']:
                raise RawSourceError('copied folder SHA drift')
        experiments = discover_experiments(work, str(source.get("pdata_procno") or "1"))
        selected = _choose_experiment(experiments, str(source.get("experiment_id") or ""), nucleus)
        return {**source, "path": str(path), "sha256": manifest["tree_sha256"], "hash_kind": "directory_tree", "processing_profile": profile, "manifest": manifest, "materialized_root": str(work), "selected_experiment": selected}
    if not path.is_file():
        raise RawSourceError(f"spectrum source missing: {path}")
    actual_sha = sha256_file(path)
    expected_sha = str(source.get("sha256") or "").upper()
    if not expected_sha or actual_sha != expected_sha:
        raise RawSourceError(f"source SHA drift expected={expected_sha or 'missing'} actual={actual_sha}")
    if kind == "bruker_zip":
        if profile != "process_from_raw":
            raise RawSourceError("bruker_zip requires processing_profile=process_from_raw")
        manifest = zip_manifest(path)
        if materialize_root is None:
            experiments = discover_zip_experiments(path, str(source.get("pdata_procno") or "1"))
            selected = _choose_experiment(experiments, str(source.get("experiment_id") or ""), nucleus)
            return {**source, "path": str(path), "sha256": actual_sha, "hash_kind": "file", "processing_profile": profile, "manifest": manifest, "selected_experiment": selected}
        work = materialize_root.resolve() / f"zip_{actual_sha[:16]}"
        _extract_zip(path, work)
        experiments = discover_experiments(work, str(source.get("pdata_procno") or "1"))
        selected = _choose_experiment(experiments, str(source.get("experiment_id") or ""), nucleus)
        return {**source, "path": str(path), "sha256": actual_sha, "hash_kind": "file", "processing_profile": profile, "manifest": manifest, "materialized_root": str(work), "selected_experiment": selected}
    if kind == "mnova_container":
        if path.suffix.casefold() != ".mnova" or type(source.get("page_index")) is not int or source['page_index'] < 0:
            raise RawSourceError("mnova_container requires .mnova path and explicit page_index")
    if kind == "bruker_1r" and path.name.casefold() != "1r":
        raise RawSourceError("bruker_1r path must name a 1r file")
    return {**source, "path": str(path), "sha256": actual_sha, "hash_kind": "file", "processing_profile": profile}


def inventory_request(request: dict[str, Any], materialize_root: Path | None = None) -> dict[str, Any]:
    sources = request.get("spectrum_sources")
    if not isinstance(sources, dict) or not sources:
        raise RawSourceError("sample request requires spectrum_sources")
    # Validate every entry before writing anything; shared-package cache must not bypass checks.
    for nucleus, source in sources.items():
        if not isinstance(source, dict):
            raise RawSourceError(f'invalid spectrum source entry: {nucleus}')
        inspect_spectrum_source(source, nucleus)
    if materialize_root is not None:
        validate_output(materialize_root, [Path(s['path']) for s in sources.values()])
    records: dict[str, Any] = {}
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    for nucleus, source in sources.items():
        if nucleus not in ALLOWED_NUCLEI or not isinstance(source, dict):
            raise RawSourceError(f"invalid spectrum source entry: {nucleus}")
        cache_key = (os.path.normcase(str(Path(source['path']).resolve())), str(source.get("source_kind") or ""))
        if not source.get("source_kind"):
            path = Path(str(source.get("path") or "")).resolve()
            expected = str(source.get("sha256") or "").upper()
            if not path.is_file():
                raise RawSourceError(f"legacy spectrum source missing: {path}")
            actual = sha256_file(path)
            if not expected or actual != expected:
                raise RawSourceError(f"legacy source SHA drift expected={expected or 'missing'} actual={actual}")
            records[nucleus] = {**source, "path": str(path), "sha256": actual, "hash_kind": "file", "source_kind": "legacy_file", "processing_profile": "curate_existing"}
            continue
        # ZIP/folder materialization occurs once even when H and C share a package.
        root_for_item = materialize_root
        if materialize_root is not None and cache_key in cache and source.get("source_kind") in {"bruker_zip", "bruker_folder"}:
            cached = cache[cache_key]
            work = Path(cached["materialized_root"])
            experiments = discover_experiments(work, str(source.get("pdata_procno") or "1"))
            selected = _choose_experiment(experiments, str(source.get("experiment_id") or ""), nucleus)
            record = {**source, "path": cached["path"], "sha256": cached["sha256"], "hash_kind": cached["hash_kind"], "processing_profile": "process_from_raw", "manifest": cached["manifest"], "materialized_root": str(work), "selected_experiment": selected}
        else:
            record = inspect_spectrum_source(source, nucleus, root_for_item)
            if record.get("materialized_root"):
                cache[cache_key] = record
        records[nucleus] = record
    return {
        "schema_version": "nmr-raw-source-inventory.v1",
        "compound_id": request.get("compound_id"),
        "sources": records,
        "raw_processing_required": any(item.get("processing_profile") == "process_from_raw" for item in records.values()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect/materialize NMR sample sources")
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--materialize-root", type=Path)
    args = parser.parse_args(argv)
    try:
        request = json.loads(args.request.read_text(encoding="utf-8-sig"))
        for source in request.get('spectrum_sources', {}).values():
            if source.get('path') and not Path(source['path']).is_absolute():
                source['path'] = str(args.request.resolve().parent / source['path'])
        validate_output(args.output, [args.request] + [Path(s['path']) for s in request.get('spectrum_sources', {}).values()])
        if args.materialize_root and (args.output.resolve() == args.materialize_root.resolve() or args.output.resolve() in args.materialize_root.resolve().parents):
            raise RawSourceError('report path conflicts with materialization directory')
        result = inventory_request(request, args.materialize_root)
        _write_json(args.output, result)
        print(json.dumps({"status": "pass", "output": str(args.output), "raw_processing_required": result["raw_processing_required"]}, ensure_ascii=False))
        return 0
    except (OSError, json.JSONDecodeError, RawSourceError, ValueError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
