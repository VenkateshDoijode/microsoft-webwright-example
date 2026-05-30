import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set. Add it to your .env file.")

client = OpenAI(api_key=_api_key)

REFLECTION_PROMPT = """You are a critical evaluator reviewing the output of a web automation agent.

You will receive:
- The original task
- The agent's final report
- The step-by-step action log

Evaluate the following critical points and respond with a JSON object:
{
  "task_completed": true or false,
  "critical_points": [
    {
      "point": "<what was evaluated>",
      "status": "pass" or "fail" or "warn",
      "detail": "<explanation>"
    }
  ],
  "overall_status": "success" or "partial" or "failure",
  "recommendation": "<what should be improved or re-run if needed>"
}

Be concise and factual. Flag any missing data, hallucinated results, or incomplete steps.
"""

def reflect(task: str, report: str, log_entries: list) -> dict:
    """Run self-reflection on the completed agent run.

    Evaluates critical points: task completion, data accuracy,
    missing steps, and output quality.
    Returns a dict saved as self_reflect_result.json.
    """

    if not log_entries:
        print("[Self-Reflection] Warning: no log entries provided — reflecting on report only.")

    log_summary = "\n".join(
        f"Step {e['step']}: {e['action']} → {e['observation'][:200]}"
        for e in log_entries
    )

    user_content = (
        f"Task: {task}\n\n"
        f"Final Report:\n{report}\n\n"
        f"Action Log Summary:\n{log_summary}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": REFLECTION_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise RuntimeError(f"Self-reflection API call failed: {e}") from e

    raw = response.choices[0].message.content
    if not raw or not raw.strip():
        raise RuntimeError("Self-reflection returned an empty response.")

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse self-reflection response: {e}\nRaw: {raw}") from e

    return result


def run_reflection(task: str, report_path: str, log_path: str, output_path: str):
    """Load report and log, run reflection, save result to output_path."""

    if not os.path.exists(report_path):
        print("[Self-Reflection] No report found — skipping.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()

    log_entries = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        log_entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    print("[Self-Reflection] Evaluating critical points...")
    try:
        result = reflect(task, report, log_entries)
    except RuntimeError as e:
        print(f"[Self-Reflection] Failed: {e}")
        return None

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[Self-Reflection] Warning: could not save result file: {e}")

    print(f"[Self-Reflection] Status: {result.get('overall_status', 'unknown')}")
    print(f"[Self-Reflection] Result saved to: {output_path}")
    return result

if __name__ == "__main__":
    from env import WORKSPACE_DIR
    import glob

    logs = sorted(glob.glob(os.path.join(WORKSPACE_DIR, "run_log_*.jsonl")))
    log_path = logs[-1] if logs else ""
    report_path = os.path.join(WORKSPACE_DIR, "flights_report.txt")
    output_path = os.path.join(WORKSPACE_DIR, "self_reflect_result.json")

    from run import TASK
    run_reflection(TASK, report_path, log_path, output_path)
    
