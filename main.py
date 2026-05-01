import streamlit as st
from agent.planner import run_planner
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pawpal.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🐾 PawPal - AI Pet Care Planner",
    page_icon="🐾",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3em;
        margin-bottom: 1em;
    }
    .success-box {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check AI service status
    from agent.tools import AI_CONFIG

    if AI_CONFIG["type"] == "anthropic":
        st.success("✅ **AI Mode**: Connected to Claude AI for real responses!")
    elif AI_CONFIG["type"] == "openrouter":
        st.info("🔄 **OpenRouter Mode**: Using free AI service for responses")
    else:
        st.warning("⚠️ **Demo Mode**: Showing sample responses. Add API keys for real AI!")

    st.markdown('<h1 class="main-header">🐾 PawPal - AI Pet Care Planner</h1>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    **Welcome to PawPal!** 🐕🐱🐦🐠

    Our AI-powered pet care assistant helps you create personalized care schedules for your furry, feathery, or scaly friends.
    Simply enter your pet's details and available time, and we'll suggest tasks, optimize your schedule, and provide helpful explanations.
    """)

    # Input form
    with st.form("pet_form"):
        col1, col2 = st.columns(2)

        with col1:
            pet_name = st.text_input(
                "Pet Name",
                placeholder="Fluffy",
                help="Enter your pet's name"
            )

            species = st.selectbox(
                "Species",
                ["Dog", "Cat", "Bird", "Fish", "Rabbit", "Hamster", "Other"],
                help="Select your pet's species"
            )

        with col2:
            available_minutes = st.slider(
                "Available Minutes",
                min_value=15,
                max_value=240,
                value=60,
                step=15,
                help="How much time do you have for pet care today?"
            )

            st.markdown(f"**Selected time: {available_minutes} minutes**")

        submitted = st.form_submit_button("🪄 Create Care Plan", use_container_width=True)

    # Process form submission
    if submitted:
        # Input validation
        if not pet_name.strip():
            st.error("❌ Please enter your pet's name")
            st.stop()

        if available_minutes < 15:
            st.error("❌ Please allocate at least 15 minutes for pet care")
            st.stop()

        try:
            with st.spinner("🤖 AI is planning your pet's perfect day..."):
                logger.info(f"Creating plan for {pet_name} ({species}) with {available_minutes} minutes")
                result = run_planner(pet_name, species, available_minutes)

            # Check for errors
            if "error" in result:
                st.error(f"❌ **Error**: {result['error']}")
                logger.error(f"Plan creation failed: {result['error']}")
                st.stop()

            # Success message
            st.success(f"✅ **Care plan created for {result['pet_name']}!**")
            logger.info(f"Plan created successfully for {pet_name}")

            # Display results in organized sections
            tab1, tab2, tab3 = st.tabs(["📋 Suggested Tasks", "📅 Optimized Schedule", "💬 Plan Summary"])

            with tab1:
                st.markdown("### 🔍 AI-Suggested Tasks")
                st.markdown("Based on your pet's species and available time, here are the recommended care tasks:")
                st.text_area(
                    "Suggested Tasks",
                    result["suggested_tasks"],
                    height=300,
                    disabled=True,
                    key="tasks"
                )

            with tab2:
                st.markdown("### 📅 Optimized Daily Schedule")
                st.markdown("Tasks arranged in the most logical order, fitting within your available time:")
                st.text_area(
                    "Optimized Schedule",
                    result["optimized_schedule"],
                    height=300,
                    disabled=True,
                    key="schedule"
                )

            with tab3:
                st.markdown("### 💬 Plan Summary")
                st.info(result["explanation"])

            # Additional features (outside the form)
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🔄 Create Another Plan", use_container_width=True):
                    st.rerun()

            with col2:
                st.download_button(
                    label="📥 Download Plan",
                    data=f"""# PawPal Care Plan for {result['pet_name']}

## Pet Details
- Name: {result['pet_name']}
- Species: {result['species']}
- Available Time: {result['available_minutes']} minutes

## Suggested Tasks
{result['suggested_tasks']}

## Optimized Schedule
{result['optimized_schedule']}

## Summary
{result['explanation']}
""",
                    file_name=f"pawpal_plan_{result['pet_name'].lower()}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col3:
                st.markdown("**⏰ Pro tip:** Set a reminder for your first task!")

        except Exception as e:
            logger.error(f"Unexpected error in main app: {e}")
            st.error(f"❌ **Unexpected Error**: {str(e)}")
            st.info("Please try again or check your API key configuration.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>
        🐾 PawPal uses AI to help pet owners create better care routines.<br>
        Built with Claude by Anthropic • Powered by Streamlit
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()