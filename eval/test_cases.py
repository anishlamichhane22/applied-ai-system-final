import pytest
from unittest.mock import patch, MagicMock
from agent.planner import run_planner
from agent.tools import suggest_tasks, optimize_schedule, explain_plan
import os

# Mock responses for testing
MOCK_TASKS_RESPONSE = """TASK: Feed dog | DURATION: 10 | PRIORITY: high | REASON: Essential nutrition
TASK: Walk dog | DURATION: 20 | PRIORITY: high | REASON: Exercise and mental stimulation
TASK: Brush fur | DURATION: 5 | PRIORITY: medium | REASON: Grooming and bonding
TASK: Play time | DURATION: 15 | PRIORITY: medium | REASON: Mental stimulation and bonding"""

MOCK_SCHEDULE_RESPONSE = """SCHEDULED: 8:00 AM | TASK: Feed dog | DURATION: 10min | NOTE: Start with nutrition
SCHEDULED: 8:15 AM | TASK: Walk dog | DURATION: 20min | NOTE: Morning exercise
SCHEDULED: 8:40 AM | TASK: Brush fur | DURATION: 5min | NOTE: Quick grooming"""

MOCK_EXPLANATION_RESPONSE = """Great job planning time for Buddy today! Your schedule covers essential feeding and exercise needs first, then moves to grooming. This logical flow ensures Buddy gets his basic needs met before fun activities. Pro tip: Keep treats handy to make the brushing session extra enjoyable!"""

class TestTools:
    """Test the individual AI tools"""

    @patch('agent.tools.client')
    def test_suggest_tasks_success(self, mock_client):
        """Test successful task suggestion"""
        # Mock the API response
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = MOCK_TASKS_RESPONSE
        mock_client.messages.create.return_value = mock_message

        result = suggest_tasks("Buddy", "Dog", 60)

        assert "TASK:" in result
        assert "Buddy" not in result  # Should not contain pet name in response
        mock_client.messages.create.assert_called_once()

    @patch('agent.tools.client')
    def test_suggest_tasks_validation(self, mock_client):
        """Test input validation"""
        # Empty pet name
        result = suggest_tasks("", "Dog", 60)
        assert "Error:" in result

        # Insufficient time
        result = suggest_tasks("Buddy", "Dog", 2)
        assert "Error:" in result

    @patch('agent.tools.client')
    def test_optimize_schedule_success(self, mock_client):
        """Test successful schedule optimization"""
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = MOCK_SCHEDULE_RESPONSE
        mock_client.messages.create.return_value = mock_message

        result = optimize_schedule(MOCK_TASKS_RESPONSE, 60)

        assert "SCHEDULED:" in result
        mock_client.messages.create.assert_called_once()

    @patch('agent.tools.client')
    def test_explain_plan_success(self, mock_client):
        """Test successful plan explanation"""
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = MOCK_EXPLANATION_RESPONSE
        mock_client.messages.create.return_value = mock_message

        result = explain_plan("Buddy", MOCK_SCHEDULE_RESPONSE)

        assert "Buddy" in result
        assert len(result) > 50  # Should be a meaningful explanation
        mock_client.messages.create.assert_called_once()

    @patch('agent.tools.client')
    def test_api_error_handling(self, mock_client):
        """Test API error handling"""
        mock_client.messages.create.side_effect = Exception("API Error")

        result = suggest_tasks("Buddy", "Dog", 60)
        assert "Error:" in result
        assert "API Error" in result

class TestPlanner:
    """Test the main planner functionality"""

    @patch('agent.tools.client')
    def test_run_planner_success(self, mock_client):
        """Test successful full planner run"""
        # Mock all API responses
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]

        # Different responses for different calls
        mock_client.messages.create.side_effect = [
            MagicMock(content=[MagicMock(text=MOCK_TASKS_RESPONSE)]),
            MagicMock(content=[MagicMock(text=MOCK_SCHEDULE_RESPONSE)]),
            MagicMock(content=[MagicMock(text=MOCK_EXPLANATION_RESPONSE)])
        ]

        result = run_planner("Buddy", "Dog", 60)

        assert result["pet_name"] == "Buddy"
        assert result["species"] == "Dog"
        assert result["available_minutes"] == 60
        assert "suggested_tasks" in result
        assert "optimized_schedule" in result
        assert "explanation" in result
        assert "error" not in result

    @patch('agent.tools.client')
    def test_run_planner_with_error(self, mock_client):
        """Test planner error handling"""
        mock_client.messages.create.side_effect = Exception("API Error")

        result = run_planner("Buddy", "Dog", 60)

        assert "error" in result
        assert result["pet_name"] == "Buddy"

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @patch('agent.tools.client')
    def test_insufficient_time_scenario(self, mock_client):
        """Test with very limited time"""
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = """TASK: Quick feed | DURATION: 5 | PRIORITY: high | REASON: Basic nutrition
SKIPPED: Walk dog | REASON: Not enough time"""
        mock_client.messages.create.return_value = mock_message

        result = run_planner("Buddy", "Dog", 10)

        assert result["available_minutes"] == 10
        assert "error" not in result

    @patch('agent.tools.client')
    def test_different_species(self, mock_client):
        """Test with different pet species"""
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = """TASK: Feed fish | DURATION: 2 | PRIORITY: high | REASON: Essential nutrition
TASK: Clean tank | DURATION: 10 | PRIORITY: high | REASON: Water quality"""
        mock_client.messages.create.return_value = mock_message

        result = run_planner("Goldie", "Fish", 30)

        assert result["species"] == "Fish"
        assert "error" not in result

class TestIntegration:
    """Integration tests that verify the full workflow"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @patch('agent.tools.client')
    def test_full_workflow(self, mock_client):
        """Test the complete workflow from input to output"""
        # Setup mocks
        mock_client.api_key = "test_key"
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]

        mock_client.messages.create.side_effect = [
            MagicMock(content=[MagicMock(text=MOCK_TASKS_RESPONSE)]),
            MagicMock(content=[MagicMock(text=MOCK_SCHEDULE_RESPONSE)]),
            MagicMock(content=[MagicMock(text=MOCK_EXPLANATION_RESPONSE)])
        ]

        # Run the planner
        result = run_planner("Max", "Cat", 45)

        # Verify structure
        required_keys = ["pet_name", "species", "available_minutes", "suggested_tasks", "optimized_schedule", "explanation"]
        for key in required_keys:
            assert key in result

        # Verify content
        assert result["pet_name"] == "Max"
        assert result["species"] == "Cat"
        assert result["available_minutes"] == 45
        assert len(result["suggested_tasks"]) > 0
        assert len(result["optimized_schedule"]) > 0
        assert len(result["explanation"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])