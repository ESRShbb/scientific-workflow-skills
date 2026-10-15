# Synthetic metadata/file fixtures only; not valid acquisitions or MNOVA containers.
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


import sys

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import raw_source_adapter as adapter


def _acqus(nucleus: str, ns: int = 16) -> bytes:
    return (
        f"##$NUC1= <{nucleus}>\n"
        "##$NUC2= <1H>\n"
        "##$SOLVENT= <DMSO>\n"
        f"##$NS= {ns}\n"
        f"##$SFO1= {'600.13' if nucleus == '1H' else '150.91'}\n"
        "##$PULPROG= <zg30>\n"
    ).encode("latin-1")


def _make_folder(root: Path) -> Path:
    package = root / "bruker"
    for experiment, nucleus in (("10", "1H"), ("11", "13C")):
        exp = package / experiment
        proc = exp / "pdata" / "1"
        proc.mkdir(parents=True)
        (exp / "acqus").write_bytes(_acqus(nucleus, 16 if nucleus == "1H" else 1049))
        (exp / "fid").write_bytes((nucleus + "-fid").encode())
        (proc / "1r").write_bytes((nucleus + "-1r").encode())
        (proc / "procs").write_text("##$SI= 16\n", encoding="latin-1")
    return package


def _make_zip(folder: Path, output: Path) -> Path:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, "package/" + path.relative_to(folder).as_posix())
    return output


class TestRawSourceAdapter(unittest.TestCase):
    def test_folder_tree_hash_is_deterministic_and_selects_nuclei(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = _make_folder(root)
            one = adapter.directory_manifest(folder)
            two = adapter.directory_manifest(folder)
            self.assertEqual(one["tree_sha256"], two["tree_sha256"])
            source = {
                "source_kind": "bruker_folder",
                "path": str(folder),
                "sha256": one["tree_sha256"],
                "nucleus": "13C",
                "experiment_id": "11",
                "pdata_procno": "1",
                "processing_profile": "process_from_raw",
            }
            record = adapter.inspect_spectrum_source(source, "13C", root / "work")
            self.assertEqual(record["selected_experiment"]["nucleus"], "13C")
            self.assertTrue(Path(record["selected_experiment"]["fid"]["path"]).is_file())

    def test_zip_is_materialized_once_for_two_nuclei(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            zip_path = _make_zip(_make_folder(root), root / "raw.zip")
            sha = adapter.sha256_file(zip_path)
            request = {
                "compound_id": "sample-A",
                "spectrum_sources": {
                    "1H": {"source_kind": "bruker_zip", "path": str(zip_path), "sha256": sha, "nucleus": "1H", "experiment_id": "10", "pdata_procno": "1", "processing_profile": "process_from_raw"},
                    "13C": {"source_kind": "bruker_zip", "path": str(zip_path), "sha256": sha, "nucleus": "13C", "experiment_id": "11", "pdata_procno": "1", "processing_profile": "process_from_raw"},
                },
            }
            result = adapter.inventory_request(request, root / "work")
            h = result["sources"]["1H"]
            c = result["sources"]["13C"]
            self.assertEqual(h["materialized_root"], c["materialized_root"])
            self.assertEqual(h["selected_experiment"]["nucleus"], "1H")
            self.assertEqual(c["selected_experiment"]["nucleus"], "13C")
            self.assertEqual(c["selected_experiment"]["nuc2"], "1H")

    def test_nucleus_mismatch_and_missing_experiment_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = _make_folder(root)
            tree = adapter.directory_manifest(folder)["tree_sha256"]
            base = {"source_kind": "bruker_folder", "path": str(folder), "sha256": tree, "nucleus": "1H", "processing_profile": "process_from_raw"}
            with self.assertRaisesRegex(adapter.RawSourceError, "matches=0"):
                adapter.inspect_spectrum_source({**base, "experiment_id": "99"}, "1H")
            with self.assertRaisesRegex(adapter.RawSourceError, "nucleus mismatch"):
                adapter.inspect_spectrum_source({**base, "experiment_id": "11"}, "1H")

    def test_wrong_hash_and_processed_profile_for_raw_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            zip_path = _make_zip(_make_folder(root), root / "raw.zip")
            source = {"source_kind": "bruker_zip", "path": str(zip_path), "sha256": "A" * 64, "nucleus": "1H", "experiment_id": "10", "processing_profile": "process_from_raw"}
            with self.assertRaisesRegex(adapter.RawSourceError, "SHA drift"):
                adapter.inspect_spectrum_source(source, "1H")
            source["sha256"] = adapter.sha256_file(zip_path)
            source["processing_profile"] = "curate_existing"
            with self.assertRaisesRegex(adapter.RawSourceError, "process_from_raw"):
                adapter.inspect_spectrum_source(source, "1H")

    def test_zip_path_traversal_and_duplicate_normalized_member_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            unsafe = root / "unsafe.zip"
            with zipfile.ZipFile(unsafe, "w") as archive:
                archive.writestr("../escape", b"x")
            with self.assertRaisesRegex(adapter.RawSourceError, "unsafe ZIP"):
                adapter.zip_manifest(unsafe)
            duplicate = root / "duplicate.zip"
            with zipfile.ZipFile(duplicate, "w") as archive:
                archive.writestr("Root/file", b"a")
                archive.writestr("root/FILE", b"b")
            with self.assertRaisesRegex(adapter.RawSourceError, "duplicate normalized"):
                adapter.zip_manifest(duplicate)

    def test_mnova_and_legacy_1r_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mnova = root / "sample.mnova"
            mnova.write_bytes(b"mnova")
            source = {"source_kind": "mnova_container", "path": str(mnova), "sha256": adapter.sha256_file(mnova), "nucleus": "1H", "page_index": 0, "processing_profile": "curate_existing"}
            record = adapter.inspect_spectrum_source(source, "1H")
            self.assertEqual(record["processing_profile"], "curate_existing")
            raw_record = adapter.inspect_spectrum_source({**source, "processing_profile": "process_from_raw"}, "1H")
            self.assertEqual(raw_record["processing_profile"], "process_from_raw")
            with self.assertRaisesRegex(adapter.RawSourceError, "page_index"):
                adapter.inspect_spectrum_source({k: v for k, v in source.items() if k != "page_index"}, "1H")
            one_r = root / "1r"
            one_r.write_bytes(b"1r")
            legacy = {"source_kind": "bruker_1r", "path": str(one_r), "sha256": adapter.sha256_file(one_r), "nucleus": "19F", "processing_profile": "curate_existing"}
            self.assertEqual(adapter.inspect_spectrum_source(legacy, "19F")["source_kind"], "bruker_1r")


if __name__ == "__main__":
    unittest.main()
