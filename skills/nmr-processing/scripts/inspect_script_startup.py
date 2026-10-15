"""Recognize common automatic QS startup side effects, without executing scripts.

This small conservative preflight is not a JavaScript sandbox. It recognizes
named function declarations and their top-level callers, including try blocks.
Review unusual scripts manually; no script/configuration is changed here.
"""
from pathlib import Path
import argparse, json, re

TOKEN = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
DANGEROUS = re.compile(r'(?:\bserialization\s*\.\s*(?:open|save)|\bApplication\s*\.\s*(?:quit|exit)|\.\s*(?:write|remove|rename)\s*\()')

def masked(code):
    return TOKEN.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), code)

def inspect_text(code):
    clean = masked(code); top = list(clean); functions = {}
    for match in re.finditer(r'\bfunction\s+([\w$]+)\s*\([^)]*\)\s*\{', clean):
        start = match.end(); depth = 1; end = start
        while end < len(clean) and depth:
            if clean[end] == '{': depth += 1
            elif clean[end] == '}': depth -= 1
            end += 1
        functions[match[1]] = (clean[start:end-1], start)
        for i in range(match.start(), end):
            if top[i] != '\n': top[i] = ' '
    top = ''.join(top)
    def effects(body, offset, visited):
        hits = [{'line':code.count('\n',0,offset+m.start())+1, 'operation':m.group().strip()}
                for m in DANGEROUS.finditer(body)]
        for name, (inner, pos) in functions.items():
            if name in visited: continue
            for call in re.finditer(r'\b'+re.escape(name)+r'\s*\(', body):
                downstream = effects(inner, pos, visited|{name})
                if downstream:
                    hits.append({'line':code.count('\n',0,offset+call.start())+1,
                                 'operation':name+'()', 'calls_effects':downstream})
        return hits
    return effects(top,0,set())

def inspect_directory(directory):
    directory = Path(directory).resolve()
    if not directory.is_dir(): raise ValueError('existing scripts directory required')
    files = []
    for p in sorted(directory.glob('*.qs')):
        try:
            data = p.read_bytes()
            try: code = data.decode('utf-8-sig')
            except UnicodeDecodeError: code = data.decode('cp1252')
            hits = inspect_text(code)
            if hits: files.append({'file':str(p),'startup_effects':hits})
        except Exception as e: files.append({'file':str(p),'inspection_error':str(e)})
    return {'directory':str(directory),'state':'BLOCKED' if files else 'NO_COMMON_STARTUP_EFFECTS_FOUND',
            'findings':files,'scope':'Common named-function/top-level side effects; not a sandbox'}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists(): raise ValueError('new report path required')
    r=inspect_directory(a.directory);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(2 if r['state']=='BLOCKED' else 0)
