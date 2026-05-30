import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set. Add it to your .env file.")

client = OpenAI(api_key=_api_key)

SYSTEM_PROMPT = """You are a web automation agent. Your job is to complete a given task by issuing shell commands.

You operate inside a workspace directory. You can use:
- Python scripts (using playwright for browser automation)
- Shell commands (dir, type, echo, python, etc.)

At each step you will receive the task and the conversation history so far.
You must respond with a JSON object in this exact format:
{
  "thought": "<your reasoning about what to do next>",
  "action": "<the exact shell command to run>",
  "done": false
}

When the task is complete, set "done" to true:
{
  "thought": "<reasoning>",
  "action": "<final shell command or empty string>",
  "done": true
}

Rules:
- One action per response
- Actions are shell commands executed in the workspace directory
- Use Python scripts for browser automation via Playwright
- Keep actions minimal and targeted
- Write results and findings to files in the workspace
"""


def get_next_action(history: list) -> dict:
    """
    Send task history and last observation to the LLM.
    Returns parsed action dict with keys: thought, action, done.
    Raises RuntimeError on API or parse failure.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}") from e

    raw = response.choices[0].message.content
    if not raw or not raw.strip():
        raise RuntimeError("OpenAI returned an empty response.")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse model response as JSON: {e}\nRaw: {raw}") from e

    return {
        "thought": parsed.get("thought", ""),
        "action": parsed.get("action", ""),
        "done": parsed.get("done", False),
    }
