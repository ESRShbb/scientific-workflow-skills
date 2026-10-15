"""Windows: independent native ExportTable job per verified sheet; no new fitting.

Requires pywin32 for PID-specific normal window cleanup, never force termination.
Native command encoding and result-title language must be checked on the host.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, time
from prepare_native_export import prepare

def close_owned(pid):
    import win32gui, win32process, win32con
    windows=[]
    def collect(hwnd,_):
        if win32process.GetWindowThreadProcessId(hwnd)[1]==pid: windows.append(hwnd)
    win32gui.EnumWindows(collect,None)
    for hwnd in windows:
        try:
            kind=win32gui.GetClassName(hwnd)
            if kind.startswith('IPMainClass') or kind=='#32770':
                win32gui.PostMessage(hwnd,win32con.WM_CLOSE,0,0)
        except Exception:pass

def ensure_no_session(software):
    exe=Path(software).name
    # tasklist /FO CSV gives exact image names, not substring matching.
    import csv, io
    p=subprocess.run(['tasklist','/FI','IMAGENAME eq '+exe,'/FO','CSV','/NH'],capture_output=True)
    if p.returncode:raise RuntimeError('Cannot inspect existing native sessions')
    # tasklist's localized no-process message can use a different code page
    # from Python UTF-8 mode. Match the vendor's ASCII executable field only.
    listing=p.stdout.decode('utf-8',errors='replace')
    if any(row and row[0].casefold()==exe.casefold() for row in csv.reader(io.StringIO(listing))):
        raise RuntimeError('Existing Prism session; no session was changed')

def run(source,sheet_map,output,software,encoding,timeout):
    import win32gui  # fail before native launch when dependency is absent
    source,output=Path(source).resolve(),Path(output).resolve()
    if output.exists() or source.is_relative_to(output):raise ValueError('fresh independent output required')
    sheets=json.loads(Path(sheet_map).read_text(encoding='utf-8-sig'))['sheets']
    if not Path(software).is_file():raise ValueError('executable missing')
    ensure_no_session(software)
    output.mkdir(parents=True);rows=[];baseline=hashlib.sha256(source.read_bytes()).hexdigest()
    for sheet in sheets:
        n=sheet['number'];row={'number':n,'navigator_title':sheet['expected_title']};rows.append(row)
        if sheet.get('skip') is True:
            if not sheet.get('evidence'):raise ValueError('skipped sheet needs explicit evidence')
            row.update(state='SKIPPED',evidence=sheet['evidence']);continue
        job=output/f'R{n}';mapfile=output/f'map_R{n}.json'
        mapfile.write_text(json.dumps({'sheets':[sheet]},ensure_ascii=False),encoding='utf-8')
        prepare(source,mapfile,job,encoding,'native')
        script=job/'export.pzc'
        # Only an independently launched process; never Exit in a shared session.
        # Keep the script host alive until Exit is actually executed.
        # CloseScriptDialog can end command processing before a following Exit.
        code=script.read_bytes().decode(encoding).replace('CloseScriptDialog\n','')
        script.write_bytes((code+'Exit\n').encode(encoding))
        ensure_no_session(software)
        proc=subprocess.Popen([str(software),'@'+str(script)],creationflags=subprocess.CREATE_NO_WINDOW)
        row['pid']=proc.pid;deadline=time.monotonic()+timeout;complete=False
        try:
            while time.monotonic()<deadline:
                title=job/f'title_R{n}.txt';table=job/f'result_R{n}.txt'
                complete=title.is_file() and table.is_file() and title.stat().st_size>0 and table.stat().st_size>0
                if proc.poll() is not None:break
                # Export files can precede Close/Exit. Do not interrupt native
                # cleanup merely because the table has appeared.
                time.sleep(.5)
        finally:
            if proc.poll() is None:
                # Prism can first close its script/document, then expose its main window.
                # Continue normal close requests only to this job's own process.
                closing=time.monotonic()+30
                while proc.poll() is None and time.monotonic()<closing:
                    close_owned(proc.pid)
                    try:proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:pass
            row.update(process_exited=proc.poll() is not None,exit_code=proc.poll(),
                       state='EXPORTED_REVIEW_REQUIRED' if complete else 'EXPORT_FAILED',
                       title_file=str(job/f'title_R{n}.txt'),table_file=str(job/f'result_R{n}.txt'))
            if not row['process_exited']:row['state']='CLEANUP_PENDING'
            (output/'execution.json').write_text(json.dumps({'sheets':rows,'source_sha256':baseline,
                'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==baseline,
                'fitting_commands':'NOT_ISSUED'},ensure_ascii=False,indent=2),encoding='utf-8')
        if not row['process_exited']:break
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--sheets',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--software',type=Path,required=True);p.add_argument('--encoding',default='utf-8')
    p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    r=run(a.input,a.sheets,a.output,a.software,a.encoding,a.timeout)
    print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if all(x['state'] in {'SKIPPED','EXPORTED_REVIEW_REQUIRED'} for x in r) else 2)
