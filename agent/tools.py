import anthropic
import logging
import os
import requests

logger = logging.getLogger(__name__)

# Try different AI services in order of preference
def initialize_ai_client():
    """Initialize AI client with fallback options"""
    # Try Anthropic first (if API key available)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        try:
            client = anthropic.Anthropic(api_key=anthropic_key)
            return {"type": "anthropic", "client": client}
        except Exception as e:
            logger.warning(f"Anthropic initialization failed: {e}")

    # Fallback to OpenRouter (free tier available)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            return {"type": "openrouter", "client": openrouter_key}
        except Exception as e:
            logger.warning(f"OpenRouter initialization failed: {e}")

    # Demo mode as final fallback
    logger.info("Using demo mode - no API keys available")
    return {"type": "demo", "client": None}

AI_CONFIG = initialize_ai_client()
client = AI_CONFIG["client"]
MODEL = "claude-3-5-sonnet-20241022"  # Default model name

def call_ai_service(prompt: str, max_tokens: int = 1024) -> str:
    """Unified function to call different AI services"""
    if AI_CONFIG["type"] == "anthropic" or (client is not None and hasattr(client, "messages")):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: {e}"

    elif AI_CONFIG["type"] == "openrouter":
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_CONFIG['client']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                err = f"OpenRouter API error: {response.status_code} - {response.text}"
                logger.error(err)
                return f"Error: {err}"
        except Exception as e:
            logger.error(f"OpenRouter request error: {e}")
            return f"Error: {e}"

    else:  # demo mode
        return None

# ── Tool 1: Task Suggester ──────────────────────────────────────────────────
def suggest_tasks(pet_name: str, species: str, available_minutes: int) -> str:
    """Uses AI to suggest appropriate care tasks for the pet."""
    try:
        if not pet_name.strip() or not species.strip():
            return "Error: Pet name and species are required."

        if available_minutes < 5:
            return "Error: At least 5 minutes are needed for basic care."

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

        # Try AI service first
        ai_response = call_ai_service(prompt, 1024)
        if ai_response:
            return ai_response

        # Fallback to demo responses
        logger.info("Using demo responses for task suggestions")
        if species.lower() == "dog":
            return f"""TASK: Feed {pet_name} | DURATION: 10 | PRIORITY: high | REASON: Essential nutrition for energy and health
TASK: Take {pet_name} for a walk | DURATION: 20 | PRIORITY: high | REASON: Exercise prevents obesity and provides mental stimulation
TASK: Brush {pet_name}'s fur | DURATION: 5 | PRIORITY: medium | REASON: Reduces shedding and strengthens bond
TASK: Play with {pet_name} | DURATION: 15 | PRIORITY: medium | REASON: Mental stimulation and exercise
TASK: Clean {pet_name}'s water bowl | DURATION: 2 | PRIORITY: low | REASON: Fresh water prevents dehydration"""
        elif species.lower() == "cat":
            return f"""TASK: Feed {pet_name} | DURATION: 5 | PRIORITY: high | REASON: Cats need regular small meals
TASK: Clean {pet_name}'s litter box | DURATION: 10 | PRIORITY: high | REASON: Hygiene prevents health issues
TASK: Brush {pet_name}'s fur | DURATION: 8 | PRIORITY: medium | REASON: Reduces hairballs and grooming needs
TASK: Play with {pet_name} | DURATION: 12 | PRIORITY: medium | REASON: Prevents boredom and maintains health
TASK: Check {pet_name}'s water | DURATION: 2 | PRIORITY: low | REASON: Fresh water is essential"""
        else:
            return f"""TASK: Feed {pet_name} | DURATION: 5 | PRIORITY: high | REASON: Essential nutrition
TASK: Clean {pet_name}'s habitat | DURATION: 15 | PRIORITY: high | REASON: Clean environment prevents illness
TASK: Check {pet_name}'s health | DURATION: 5 | PRIORITY: medium | REASON: Monitor for any issues
TASK: Provide enrichment | DURATION: 10 | PRIORITY: medium | REASON: Mental stimulation is important"""

    except Exception as e:
        logger.error(f"Error in suggest_tasks: {e}")
        return f"Error: Unable to suggest tasks. {str(e)}"

# ── Tool 2: Schedule Optimizer ──────────────────────────────────────────────
def optimize_schedule(tasks_text: str, available_minutes: int) -> str:
    """Uses AI to intelligently order and schedule the tasks."""
    try:
        if not tasks_text.strip():
            return "Error: No tasks provided to optimize."

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

        # Try AI service first
        ai_response = call_ai_service(prompt, 1024)
        if ai_response:
            return ai_response

        # Fallback to demo scheduling logic
        logger.info("Using demo scheduling logic")
        lines = tasks_text.strip().split('\n')
        total_time = 0
        scheduled = []
        skipped = []

        for line in lines:
            if line.startswith('TASK:'):
                parts = line.split(' | ')
                if len(parts) >= 2:
                    task_name = parts[0].replace('TASK: ', '')
                    duration_part = parts[1].replace('DURATION: ', '').replace('min', '').strip()
                    try:
                        duration = int(duration_part)
                        if total_time + duration <= available_minutes:
                            time_str = f"8:{total_time:02d} AM" if total_time < 60 else f"9:{(total_time-60):02d} AM"
                            scheduled.append(f"SCHEDULED: {time_str} | TASK: {task_name} | DURATION: {duration}min | NOTE: Essential care")
                            total_time += duration
                        else:
                            skipped.append(f"SKIPPED: {task_name} | REASON: Not enough time remaining")
                    except ValueError:
                        continue

        result = '\n'.join(scheduled)
        if skipped:
            result += '\n' + '\n'.join(skipped)
        return result

    except Exception as e:
        logger.error(f"Error in optimize_schedule: {e}")
        return f"Error: Unable to optimize schedule. {str(e)}"

# ── Tool 3: Plan Explainer ───────────────────────────────────────────────────
def explain_plan(pet_name: str, schedule_text: str) -> str:
    """Uses AI to generate a friendly explanation of the final plan."""
    try:
        if not pet_name.strip() or not schedule_text.strip():
            return "Error: Pet name and schedule are required."

        prompt = f"""You are a friendly pet care assistant.
Here is today's care schedule for {pet_name}:
{schedule_text}

Write a short, warm, encouraging summary (3-5 sentences) for the pet owner explaining:
- What the plan covers
- Why this order makes sense
- One tip to make the day go smoothly

Keep it friendly and conversational."""

        # Try AI service first
        ai_response = call_ai_service(prompt, 512)
        if ai_response:
            return ai_response

        # Fallback to demo explanation
        logger.info("Using demo explanation")
        scheduled_count = schedule_text.count('SCHEDULED:')
        skipped_count = schedule_text.count('SKIPPED:')

        if scheduled_count > 0:
            explanation = f"Great job planning time for {pet_name} today! Your schedule covers {scheduled_count} essential care tasks that will keep your pet healthy and happy. "
            if skipped_count > 0:
                explanation += f"Some tasks were skipped to fit within your time, but the most important ones are included. "
            explanation += f"This logical order ensures {pet_name} gets their basic needs met first. Pro tip: Set a timer for each task to stay on schedule!"
        else:
            explanation = f"Based on your available time, we've focused on the most essential care tasks for {pet_name}. While some activities couldn't fit today, the included tasks will keep your pet well cared for. You can always add more time tomorrow!"

        return explanation

    except Exception as e:
        logger.error(f"Error in explain_plan: {e}")
        return f"Error: Unable to generate explanation. {str(e)}"