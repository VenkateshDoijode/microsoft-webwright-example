"""
Skill: google-flights-comparison
---------------------------------
Skill-guided Google Flights comparison for a Hong Kong to Jeju trip.
Shows a generated flight skill being selected and reused as a task-specific workflow.

Skill metadata is consumed by run.py to initialise the agent task,
set constraints, and guide the model with a structured prompt.
"""

SKILL_NAME = "google-flights-comparison"
SKILL_DESCRIPTION = (
    "Skill-guided browser workflow that compares live Google Flights options "
    "and recommends a practical itinerary."
)

ORIGIN = "HKG"
DESTINATION = "CJU"
DEPART_DATE = "2026-08-08"
RETURN_DATE = "2026-08-14"
BUDGET_HKD = 20000
PASSENGERS = 1
CABIN_CLASS = "economy"
MIN_OPTIONS = 3

TASK = (
    f"Compare HKG ⇌ Jeju round-trip flights and recommend the best itinerary.\n"
    f"Route: {ORIGIN} → {DESTINATION}\n"
    f"Dates: {DEPART_DATE} (outbound) → {RETURN_DATE} (return)\n"
    f"Passengers: {PASSENGERS}, Cabin: {CABIN_CLASS}\n"
    f"Budget: HK${BUDGET_HKD:,}\n"
    f"Requirements:\n"
    f"  - Compare at least {MIN_OPTIONS} complete round-trip itineraries\n"
    f"  - Identify the cheapest nonstop option\n"
    f"  - Identify a balanced option (nonstop, avoids early departures)\n"
    f"  - Check booking source and note the platform (e.g. Agoda, Google Flights)\n"
    f"  - Save final recommendation to flights_report.txt\n"
    f"  - Save structured comparison data to flights_data.json"
)

WORKFLOW_STEPS = [
    {
        "id": "00:00",
        "label": "TASK START: flight comparison request",
        "description": (
            f"The agent receives the {ORIGIN} ⇌ {DESTINATION} prompt with fixed dates, "
            f"{CABIN_CLASS} class, {PASSENGERS} passenger, HK${BUDGET_HKD:,} budget, "
            f"and a requirement to compare at least {MIN_OPTIONS} options."
        ),
    },
    {
        "id": "01:00",
        "label": "SETUP: load Google Flights skill",
        "description": "The agent selects the google-flights-comparison skill to run the browser-backed comparison workflow.",
    },
    {
        "id": "01:43",
        "label": "BROWSER TASK START: open Google Flights",
        "description": (
            f"The browser opens Google Flights already scoped to {ORIGIN} and {DESTINATION}, "
            "with the form ready for date and itinerary selection."
        ),
    },
    {
        "id": "02:30",
        "label": "DATA LOAD: first fares appear",
        "description": "Google Flights returns initial fare options while prices are still stabilizing.",
    },
    {
        "id": "03:20",
        "label": "KEY FINDING: cheapest nonstop appears",
        "description": "The cheapest nonstop option is identified and recorded.",
    },
    {
        "id": "03:46",
        "label": "RETURN SELECTION: complete round trip",
        "description": "The workflow advances to the return-leg page and starts pairing outbound and inbound flights into complete itineraries.",
    },
    {
        "id": "04:08",
        "label": "BALANCED OPTION: avoid early departure",
        "description": "The workflow identifies a more practical nonstop option that avoids very early outbound flights.",
    },
    {
        "id": "04:45",
        "label": "BOOKING SOURCE CHECK",
        "description": "The selected itinerary's booking source (e.g. Agoda, Google Flights direct) is noted.",
    },
    {
        "id": "05:20",
        "label": "COMPARISON OPTION: third itinerary",
        "description": "A third itinerary is checked as a comparison point — may be more expensive but with a later return time.",
    },
    {
        "id": "05:56",
        "label": "TASK END: recommendation delivered",
        "description": (
            "The agent recommends the best itinerary because it is nonstop, "
            "remains far under budget, and avoids the very early outbound flight. "
            "Final report saved to flights_report.txt."
        ),
    },
]


def get_task() -> str:
    """Return the full task string for this skill."""
    return TASK


def get_workflow_steps() -> list:
    """Return the ordered workflow steps for logging and display."""
    return WORKFLOW_STEPS


def get_metadata() -> dict:
    """Return skill metadata summary."""
    return {
        "skill": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "origin": ORIGIN,
        "destination": DESTINATION,
        "depart_date": DEPART_DATE,
        "return_date": RETURN_DATE,
        "budget_hkd": BUDGET_HKD,
        "passengers": PASSENGERS,
        "cabin_class": CABIN_CLASS,
        "min_options": MIN_OPTIONS,
    }
