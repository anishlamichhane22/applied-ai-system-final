import anthropic

client = anthropic.Anthropic()

# ── Tool 1: Task Suggester ──────────────────────────────────────────────────
def suggest_tasks(pet_name: str, species: str, available_minutes: int) -> str:
    """Uses Claude to suggest appropriate care tasks for the pet."""
    prompt = f"""You are a pet care expert. 
The owner has {available_minutes} minutes available today.
Their pet is named {pet_name} and is a {species}.

Suggest 4-6 specific care tasks for this pet today.
For each task provide:
- Task name
- Duration in minutes
- Priority (high/medium/low)
- Brief reason why this task matters

Format each task exactly like this:
TASK: [name] | DURATION: [minutes] | PRIORITY: [level] | REASON: [reason]"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ── Tool 2: Schedule Optimizer ──────────────────────────────────────────────
def optimize_schedule(tasks_text: str, available_minutes: int) -> str:
    """Uses Claude to intelligently order and schedule the tasks."""
    prompt = f"""You are a scheduling expert.
Given these pet care tasks:
{tasks_text}

The owner has {available_minutes} minutes total available starting at 8:00 AM.

Create an optimized schedule that:
1. Fits within the available time
2. Orders tasks logically (e.g. feeding before walks)
3. Skips tasks that don't fit and explains why

Format your response exactly like this for each scheduled task:
SCHEDULED: [time] | TASK: [name] | DURATION: [minutes]min | NOTE: [brief note]

Then list any skipped tasks like this:
SKIPPED: [task name] | REASON: [why it was skipped]"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ── Tool 3: Plan Explainer ───────────────────────────────────────────────────
def explain_plan(pet_name: str, schedule_text: str) -> str:
    """Uses Claude to generate a friendly explanation of the final plan."""
    prompt = f"""You are a friendly pet care assistant.
Here is today's care schedule for {pet_name}:
{schedule_text}

Write a short, warm, encouraging summary (3-5 sentences) for the pet owner explaining:
- What the plan covers
- Why this order makes sense
- One tip to make the day go smoothly

Keep it friendly and conversational."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text