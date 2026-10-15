"""Check distributed resources and run synthetic tests; no native applications."""
from pathlib import Path
import ast
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "nmr-processing", "prism-ic50-analysis", "characterization-curation",
    "chemdraw-ole", "scientific-figure-format", "illustrator-scientific-figure",
)


def check_package():
    errors = []
    actual = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
    if actual != set(SKILLS):
        errors.append(f"Unexpected skill set: {sorted(actual)}")
    for name in SKILLS:
        entry = ROOT / "skills" / name / "SKILL.md"
        if not entry.is_file():
            errors.append(f"Missing entrypoint: {name}")
            continue
        text = entry.read_text(encoding="utf-8-sig")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---", text, re.S)
        if not frontmatter:
            errors.append(f"Missing frontmatter: {name}")
        else:
            header = frontmatter.group(1)
            if not re.search(rf"^name:\s*{re.escape(name)}\s*$", header, re.M):
                errors.append(f"Mismatched name: {name}")
            if not re.search(r"^description:\s*\S", header, re.M):
                errors.append(f"Missing description: {name}")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8-sig")):
            target = target.strip("<>")
            if target.startswith("#") or urlsplit(target).scheme:
                continue
            relative = unquote(target.split("#", 1)[0])
            if relative and not (path.parent / relative).exists():
                errors.append(f"Broken local link: {path.relative_to(ROOT)} -> {target}")
    for path in list((ROOT / "skills").rglob("*.py")) + [Path(__file__)]:
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except SyntaxError as exc:
            errors.append(str(exc))
    return errors


def main():
    errors = check_package()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Package checks passed: {len(SKILLS)} skills", flush=True)
    failed = False
    for name in SKILLS:
        skill = ROOT / "skills" / name
        tests = skill / "scripts" / "tests"
        if not tests.is_dir():
            if name != "scientific-figure-format":
                print(f"Missing synthetic tests: {name}", file=sys.stderr)
                failed = True
            continue
        print(f"\nTesting {name}", flush=True)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(tests), "-v"],
            cwd=skill,
        )
        failed |= result.returncode != 0
    if not failed:
        print("\nSynthetic checks passed; native and scientific validation are separate.")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
