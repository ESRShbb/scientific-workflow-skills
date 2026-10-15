"""Windows native result enumeration and bounded title verification on a PZFX copy.

For projects with existing results. Requires supported Prism command scripting and
optional pywin32 for normal cleanup. No guessed upper index or new fitting.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,time
from run_native_exports import ensure_no_session,close_owned

def launch(software,script,timeout):
    ensure_no_session(software)
    proc=subprocess.Popen([str(software),'@'+str(script)],creationflags=subprocess.CREATE_NO_WINDOW)
    try:proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        deadline=time.monotonic()+30
        while proc.poll() is None and time.monotonic()<deadline:
            close_owned(proc.pid)
            try:proc.wait(timeout=2)
            except subprocess.TimeoutExpired:pass
    return {'pid':proc.pid,'process_exited':proc.poll() is not None,'exit_code':proc.poll()}

def run(source,output,software,command_encoding,text_encoding,timeout):
    import win32gui  # Check the optional Windows dependency before launch.
    source,output=Path(source).resolve(),Path(output).resolve()
    if not source.is_file() or source.suffix.lower()!='.pzfx':raise ValueError('existing PZFX required')
    if output.exists() or source.is_relative_to(output):raise ValueError('fresh independent output required')
    if not Path(software).is_file():raise ValueError('executable missing')
    ensure_no_session(software);output.mkdir(parents=True)
    baseline=hashlib.sha256(source.read_bytes()).hexdigest();work=output/'working.pzfx';shutil.copy2(source,work)
    report={'source':str(source),'source_sha256':baseline,'working_copy':str(work),'software':str(software),
            'command_encoding':command_encoding,'text_encoding':text_encoding,'state':'RUNNING',
            'sheets':[],'attempts':[],'fitting_commands':'NOT_ISSUED'}
    def q(p):
        text=str(p)
        if any(c in text for c in ('"','\n','\r')):raise ValueError('unsupported path')
        return '"'+text+'"'
    def command(name,lines):
        script=output/(name+'.pzc')
        script.write_bytes(('\n'.join(['Open '+q(work)]+lines+['Close','Exit'])+'\n').encode(command_encoding))
        attempt=launch(software,script,timeout);report['attempts'].append(attempt)
        if not attempt['process_exited']:raise RuntimeError('CLEANUP_PENDING: stop until this own session is resolved')
        if attempt['exit_code']!=0:raise RuntimeError('Native script failed')
    def titles(p):
        lines=p.read_text(encoding=text_encoding).splitlines()
        if not lines or any(not s.strip() for s in lines):raise ValueError('missing or multiline/empty native titles')
        return lines
    try:
        enumeration=output/'enumerated_titles.txt'
        # A single first-result selection establishes the result sheet type.
        # If the project has no results, stop this native probe; do not probe further indices.
        command('enumerate',['GoTo R 1','OpenOutput '+q(enumeration),'ForEachSheet','WTitle','Next','CloseOutput'])
        listed=titles(enumeration)
        verified=output/'indexed_titles.txt'
        lines=['OpenOutput '+q(verified)]
        for number in range(1,len(listed)+1):lines+=['GoTo R '+str(number),'WTitle']
        command('verify_indices',lines+['CloseOutput'])
        indexed=titles(verified)
        if indexed!=listed:raise ValueError('Native enumeration/index order differs; resolve map in the native navigator')
        report['sheets']=[{'number':n,'expected_title':title,'verified':True,
            'evidence':f'Native result-only ForEachSheet plus bounded GoTo/WTitle; {enumeration.name} and {verified.name}, line {n}'}
            for n,title in enumerate(indexed,1)]
        report['state']='RESULTS_DISCOVERED'
    except Exception as e:report.update(state='BLOCKED',error=str(e))
    finally:
        report['source_unchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==baseline
        (output/'sheet_map.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--software',type=Path,required=True)
    p.add_argument('--encoding',default='utf-8');p.add_argument('--text-encoding',default='utf-8-sig')
    p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    r=run(a.input,a.output,a.software,a.encoding,a.text_encoding,a.timeout)
    print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if r['state']=='RESULTS_DISCOVERED' and r['source_unchanged'] else 2)
