from agent.tools import suggest_tasks, optimize_schedule, explain_plan
import logging

logger = logging.getLogger(__name__)

def run_planner(pet_name: str, species: str, available_minutes: int) -> dict:
    """
    Agentic planner that coordinates all three tools
    in the correct sequence to produce a final care plan.
    """
    logger.info(f"Starting PawPal Agent for {pet_name} the {species} with {available_minutes} minutes available")

    print(f"\n🐾 Starting PawPal Agent for {pet_name} the {species}...")

    try:
        # ── Step 1: Suggest tasks using Claude ──────────────────────────────────
        print("🔍 Step 1: Analyzing pet needs and suggesting tasks...")
        logger.info("Step 1: Suggesting tasks")
        suggested = suggest_tasks(pet_name, species, available_minutes)
        if suggested.startswith("Error:"):
            raise ValueError(suggested)
        print("✅ Tasks suggested!")
        logger.info("Tasks suggested successfully")

        # ── Step 2: Optimize the schedule using Claude ───────────────────────────
        print("📅 Step 2: Optimizing schedule...")
        logger.info("Step 2: Optimizing schedule")
        schedule = optimize_schedule(suggested, available_minutes)
        if schedule.startswith("Error:"):
            raise ValueError(schedule)
        print("✅ Schedule optimized!")
        logger.info("Schedule optimized successfully")

        # ── Step 3: Generate friendly explanation using Claude ───────────────────
        print("💬 Step 3: Generating plan explanation...")
        logger.info("Step 3: Generating explanation")
        explanation = explain_plan(pet_name, schedule)
        if explanation.startswith("Error:"):
            raise ValueError(explanation)
        print("✅ Explanation ready!")
        logger.info("Explanation generated successfully")

        print("\n🎉 Plan complete!\n")

        # ── Return all outputs as a structured dict ──────────────────────────────
        result = {
            "pet_name": pet_name,
            "species": species,
            "available_minutes": available_minutes,
            "suggested_tasks": suggested,
            "optimized_schedule": schedule,
            "explanation": explanation,
        }

        logger.info(f"Plan completed successfully for {pet_name}")
        return result

    except Exception as e:
        logger.error(f"Error in run_planner: {e}")
        print(f"\n❌ Error creating plan: {e}\n")
        return {
            "error": str(e),
            "pet_name": pet_name,
            "species": species,
            "available_minutes": available_minutes,
        }