"""One bounded, offline child heartbeat. Evidence only, never fake discoveries."""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from student_autonomous import run_autonomous_baseline

def heartbeat(output_dir, runner=subprocess.run):
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    practice_path=output_dir/"practice.json"
    lesson=run_autonomous_baseline("reentrancy-01",practice_path)
    command=["forge","test","--root","student_lab","--match-contract","ReentrancyLessonTest","-vv"]
    try:
        proc=runner(command,capture_output=True,text=True,timeout=180)
        forge={"executed":True,"passed":proc.returncode==0,"returncode":proc.returncode,
               "log_tail":(proc.stdout+"\n"+proc.stderr)[-5000:]}
    except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
        forge={"executed":False,"passed":False,"error":type(exc).__name__}
    result={"timestamp_utc":datetime.now(timezone.utc).isoformat(),
            "phase":"offline_baseline_heartbeat","practice_attempts":len(lesson["attempts"]),
            "practice_record":str(practice_path),"forge":forge,
            "model_inference_executed":False,"independent_learning_verified":False,
            "real_money_earned":False,"heartbeat_ok":bool(forge["passed"])}
    (output_dir/"heartbeat.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if not result["heartbeat_ok"]:
        raise RuntimeError("offline child heartbeat failed; see heartbeat.json")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(heartbeat(a.output_dir),ensure_ascii=False))
if __name__=="__main__":
    main()
