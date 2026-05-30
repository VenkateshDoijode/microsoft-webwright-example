import json
import os
import glob
import shutil
from datetime import datetime
from env import execute_command, capture_observation, write_workspace_file, ensure_workspace, WORKSPACE_DIR
from model import get_next_action
from skills.google_flights_comparison import get_task, get_metadata, get_workflow_steps

TASK = get_task()
SKILL_META = get_metadata()
WORKFLOW_STEPS = get_workflow_steps()

MAX_STEPS = 15


def log_step(step: int, thought: str, action: str, observation: str, log_path: str):
    """Append a step entry to the run log file."""
    entry = {
        "step": step,
        "timestamp": datetime.now().isoformat(),
        "thought": thought,
        "action": action,
        "observation": observation,
    }
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[WARNING] Could not write log step {step}: {e}")


def get_next_final_run_dir() -> str:
    """Return the next available final_runs/run_N/ directory path."""
    base = os.path.join(os.path.dirname(__file__), "final_runs")
    os.makedirs(base, exist_ok=True)
    existing = sorted(glob.glob(os.path.join(base, "run_*")))
    next_n = len(existing) + 1
    run_dir = os.path.join(base, f"run_{next_n}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def promote_to_final_run(log_path: str) -> str:
    """Copy final script, log, screenshots, and report to final_runs/run_N/.

    WebWright paradigm: the loop continues until the agent produces a final
    script, reruns it in a fresh folder, and passes self-reflection.
    """
    run_dir = get_next_final_run_dir()

    try:
        for pattern in ["*.py", "*.txt", "*.json", "*.jsonl"]:
            for src in glob.glob(os.path.join(WORKSPACE_DIR, pattern)):
                shutil.copy2(src, run_dir)

        screenshots_src = os.path.join(WORKSPACE_DIR, "screenshots")
        if os.path.exists(screenshots_src):
            shutil.copytree(screenshots_src, os.path.join(run_dir, "screenshots"), dirs_exist_ok=True)
    except OSError as e:
        print(f"[WARNING] Could not copy some artifacts to final run: {e}")

    print(f"[Final Run] Artifacts promoted to: {run_dir}")
    return run_dir


def run():
    ensure_workspace()

    log_path = os.path.join("workspace", f"run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")

    print("=" * 60)
    print(f"MICROSOFT WEBWRIGHT · SKILL WORKFLOW")
    print(f"Skill  : {SKILL_META['skill']}")
    print(f"Route  : {SKILL_META['origin']} ⇌ {SKILL_META['destination']}")
    print(f"Dates  : {SKILL_META['depart_date']} → {SKILL_META['return_date']}")
    print(f"Budget : HK${SKILL_META['budget_hkd']:,}")
    print(f"Cabin  : {SKILL_META['cabin_class']} · {SKILL_META['passengers']} passenger")
    print("=" * 60)
    print("\nWORKFLOW STEPS:")
    for step in WORKFLOW_STEPS:
        print(f"  [{step['id']}] {step['label']}")
    print("=" * 60)
    print(f"\nMax agent steps: {MAX_STEPS}\n")

    history = [{"role": "user", "content": f"Task: {TASK}"}]

    for step in range(1, MAX_STEPS + 1):
        print(f"\n[Step {step}/{MAX_STEPS}] Querying model...")

        try:
            result = get_next_action(history)
        except RuntimeError as e:
            print(f"  [ERROR] Model call failed: {e}")
            log_step(step, "[ERROR]", "", str(e), log_path)
            break

        thought = result["thought"]
        action = result["action"]
        done = result["done"]

        print(f"  Thought  : {thought}")
        print(f"  Action   : {action}")

        if done:
            print("\n[Agent] Task marked as complete.")
            log_step(step, thought, action, "DONE", log_path)
            history.append({"role": "assistant", "content": json.dumps(result)})
            break

        cmd_result = execute_command(action)
        observation = capture_observation(cmd_result)

        print(f"  Observation:\n{observation}")

        log_step(step, thought, action, observation, log_path)

        history.append({"role": "assistant", "content": json.dumps(result)})
        history.append({"role": "user", "content": f"Observation:\n{observation}"})

    else:
        print(f"\n[Agent] Reached max steps ({MAX_STEPS}). Stopping.")

    print("\n" + "=" * 60)
    print(f"Run log saved to: {log_path}")

    try:
        from env import read_workspace_file
        report = read_workspace_file("flights_report.txt")
        print("\nFINAL REPORT:")
        print("=" * 60)
        print(report)
    except Exception:
        print("[No flights_report.txt found in workspace]")

    final_run_dir = promote_to_final_run(log_path)

    abs_log = os.path.join(os.path.dirname(__file__), log_path)
    abs_report = os.path.join(WORKSPACE_DIR, "flights_report.txt")
    abs_reflect = os.path.join(final_run_dir, "self_reflect_result.json")

    try:
        from self_reflection import run_reflection
        run_reflection(TASK, abs_report, abs_log, abs_reflect)
    except Exception as e:
        print(f"[Self-Reflection] Skipped: {e}")

    print("=" * 60)


if __name__ == "__main__":
    run()
