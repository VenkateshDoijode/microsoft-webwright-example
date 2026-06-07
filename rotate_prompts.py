import datetime

# List of Webwright prompts to rotate daily
prompts = [
    "Build a CI/CD pipeline with Webwright",
    "Deploy a Kubernetes cluster using Webwright",
    "Automate Docker builds with Webwright",
    "Integrate Webwright into GitHub Actions",
    "Create a DevOps dashboard with Webwright",
    "Generate Python test cases using Webwright",
    "Monitor cloud deployments via Webwright"
]

# Pick prompt based on day of year
day_index = datetime.datetime.utcnow().timetuple().tm_yday % len(prompts)
selected_prompt = prompts[day_index]

# Write to file
with open("prompts/daily_prompt.txt", "w") as f:
    f.write(f"Prompt of the day ({datetime.date.today()}):\n")
    f.write(selected_prompt + "\n")
