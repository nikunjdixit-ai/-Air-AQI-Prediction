"""
Unit & Integration Tests for Agent Orchestrator & Conversational Memory.
Tests intent decomposition, tool invocation chains, context persistence, and activity transparency.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.agent.memory import SessionMemory
from src.agent.orchestrator import AirQualityAgent


class TestAgent(unittest.TestCase):

    def setUp(self):
        self.agent = AirQualityAgent()

    def test_session_memory_location_extraction(self):
        mem = SessionMemory()
        mem.add_message("user", "What is the air like in Bengaluru?")
        self.assertEqual(mem.get_location(), "Bengaluru")

    def test_session_memory_health_and_activity_extraction(self):
        mem = SessionMemory()
        mem.add_message("user", "I have asthma and I love morning running.")
        self.assertIn("asthma", mem.entities["health_conditions"])
        self.assertIn("running", [act.lower() for act in mem.entities["preferred_activities"]])

    def test_agent_run_kanpur_query(self):
        res = self.agent.run("What is the AQI in Kanpur today?")
        self.assertIn("response", res)
        self.assertIn("activity", res)
        self.assertGreater(len(res["activity"]), 0)
        self.assertEqual(res["location"], "Kanpur")
        self.assertIn("Kanpur", res["response"])

    def test_agent_run_exercise_query(self):
        res = self.agent.run("Should I go for a morning run in Delhi tomorrow?")
        self.assertIn("response", res)
        self.assertIn("activity", res)
        # Should execute live aqi, weather, prediction, and health
        tool_names = [a for a in res["activity"] if "Calling" in a or "Invoked" in a]
        self.assertGreaterEqual(len(tool_names), 2)
        self.assertIn("Exercise Recommendation", res["response"])

    def test_agent_run_cause_query(self):
        res = self.agent.run("Why is the air quality poor today?")
        self.assertIn("response", res)
        self.assertIn("Primary Driving Pollutant", res["response"])

    def test_agent_run_historical_query(self):
        res = self.agent.run("Compare today's AQI with the historical trend in Delhi.")
        self.assertIn("response", res)
        self.assertIn("Historical Mean AQI", res["response"])

    def test_multi_turn_memory(self):
        agent = AirQualityAgent()
        agent.run("I live in Kanpur.")
        self.assertEqual(agent.memory.get_location(), "Kanpur")

        res2 = agent.run("Should I exercise outside tomorrow?")
        self.assertEqual(res2["location"], "Kanpur")
        self.assertIn("Kanpur", res2["response"])


if __name__ == "__main__":
    unittest.main()
