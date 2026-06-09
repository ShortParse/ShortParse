import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add project root to sys.path to allow imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from shortparse.metrics.prep import audit_prep_for_player, calculate_prep_audit
from shortparse.reports.tracker import calculate_trend_slope, get_slump_tracker_analytics
from shortparse.reports.bench_builder import build_roster_composition
from shortparse.reports.recruitment import get_candidate_report_card

class TestPrepAuditor(unittest.TestCase):
    def test_prep_loss_calculations(self):
        # 1. Test case: All buffs active, no missing enchants or gems
        events = [
            {"type": "applybuff", "abilityGameID": 439000, "sourceID": 1, "timestamp": 1000},  # Flask
            {"type": "applybuff", "abilityGameID": 446000, "sourceID": 1, "timestamp": 2000},  # Food
            {"type": "applybuff", "abilityGameID": 447405, "sourceID": 1, "timestamp": 3000},  # Rune
        ]
        player_details = {
            "dps": [
                {
                    "name": "SuperPlayer",
                    "gear": [
                        {"slot": 5, "permanentEnchant": 123},  # Chest
                        {"slot": 16, "permanentEnchant": 456}, # Weapon
                        {"slot": 11, "permanentEnchant": 789, "gems": [{"id": 999}]}, # Ring with Gem
                    ]
                }
            ]
        }
        
        audit = audit_prep_for_player(
            actor_id=1,
            player_name="SuperPlayer",
            player_details=player_details,
            events=events,
            fight_start_time=0
        )
        
        self.assertTrue(audit["has_flask"])
        self.assertTrue(audit["has_food"])
        self.assertTrue(audit["has_rune"])
        self.assertEqual(audit["missing_enchants"], [])
        self.assertEqual(audit["missing_gems"], 0)
        self.assertEqual(audit["estimated_output_loss_percent"], 0.0)
        self.assertEqual(audit["preparation_score"], 100)

    def test_prep_loss_penalties(self):
        # 2. Test case: Missing flask and weapon enchant
        events = [
            {"type": "applybuff", "abilityGameID": 999999, "sourceID": 1, "timestamp": 1000}
        ]  # Missing all buffs but bypasses simulation fallback because applybuff is present
        player_details = {
            "tanks": [
                {
                    "name": "TankPlayer",
                    "gear": [
                        {"slot": 16, "permanentEnchant": 0}, # Missing weapon enchant
                        {"slot": 5, "permanentEnchant": 10},  # Has chest enchant
                        {"slot": 11, "gems": [{"id": 0}]},   # Empty socket
                    ]
                }
            ]
        }
        
        audit = audit_prep_for_player(
            actor_id=1,
            player_name="TankPlayer",
            player_details=player_details,
            events=events,
            fight_start_time=0
        )
        
        self.assertFalse(audit["has_flask"])
        self.assertFalse(audit["has_food"])
        self.assertFalse(audit["has_rune"])
        self.assertIn("weapon", audit["missing_enchants"])
        self.assertEqual(audit["missing_gems"], 1)
        
        # Penalties: Weapon enchant = 1.2%, Gem = 0.35%, Flask = 2.5%, Food = 1.0%, Rune = 0.8%, Ring1 enchant = 0.5%
        # Total = 1.2 + 0.35 + 2.5 + 1.0 + 0.8 + 0.5 = 6.35%
        self.assertEqual(audit["estimated_output_loss_percent"], 6.35)
        self.assertEqual(audit["preparation_score"], 36)


class TestSlumpTracker(unittest.TestCase):
    def test_trend_slope_calculation(self):
        # Steady improvement
        y_up = [1, 2, 3, 4, 5]
        slope_up = calculate_trend_slope(y_up)
        self.assertGreater(slope_up, 0.15)
        
        # Steady decline
        y_down = [5, 4, 3, 2, 1]
        slope_down = calculate_trend_slope(y_down)
        self.assertLess(slope_down, -0.15)
        
        # Stable performance
        y_stable = [3, 3, 3, 3, 3]
        slope_stable = calculate_trend_slope(y_stable)
        self.assertEqual(slope_stable, 0.0)

    @patch("shortparse.reports.tracker.SessionLocal")
    def test_slump_tracker_analytics_integration(self, mock_session_cls):
        mock_db = MagicMock()
        mock_session_cls.return_value = mock_db
        
        # Mocking completed jobs
        mock_job = MagicMock()
        mock_job.status = "completed"
        mock_job.result_path = "mock_path.json"
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_job]
        
        # Mock file reading
        result_data = {
            "fight": {"name": "Test Boss", "end_time": 1000},
            "scorecard": [
                {"player": "SwirlyCatcher", "class": "Priest", "spec": "Shadow", "role": "DPS", "grade": "S", "dps": 100, "avoidable_damage": 0},
                {"player": "SwirlyCatcher", "class": "Priest", "spec": "Shadow", "role": "DPS", "grade": "B", "dps": 80, "avoidable_damage": 50},
                {"player": "SwirlyCatcher", "class": "Priest", "spec": "Shadow", "role": "DPS", "grade": "F", "dps": 50, "avoidable_damage": 100},
            ]
        }
        
        # Patch open to return mock json content
        with patch("builtins.open", unittest.mock.mock_open(read_data="")):
            with patch("json.load") as mock_json_load:
                # Mock three files representing three boss pulls
                mock_json_load.side_effect = [
                    {
                        "fight": {"name": "Boss 1", "end_time": 1000},
                        "scorecard": [{"player": "Player1", "class": "Priest", "spec": "Shadow", "role": "DPS", "grade": "S", "dps": 100, "avoidable_damage": 0}]
                    },
                    {
                        "fight": {"name": "Boss 2", "end_time": 2000},
                        "scorecard": [{"player": "Player1", "class": "Priest", "spec": "Shadow", "role": "DPS", "grade": "B", "dps": 80, "avoidable_damage": 50000}]
                    },
                    {
                        "fight": {"name": "Boss 3", "end_time": 3000},
                        "scorecard": [{"player": "Player1", "class": "Priest", "spec": "Shadow", "role": "DPS", "grade": "F", "dps": 50, "avoidable_damage": 150000}]
                    }
                ]
                with patch("pathlib.Path.exists", return_value=True):
                    # Mock completed jobs query to return 3 runs
                    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [MagicMock(), MagicMock(), MagicMock()]
                    
                    analytics = get_slump_tracker_analytics()
                    
                    self.assertEqual(analytics["status"], "success")
                    self.assertEqual(len(analytics["players"]), 1)
                    p = analytics["players"][0]
                    self.assertEqual(p["name"], "Player1")
                    self.assertEqual(p["trend"], "down")
                    self.assertIn("slump", p["alert"])
                    self.assertIsNotNone(p["focus_recommendation"])


class TestBenchBuilder(unittest.TestCase):
    @patch("shortparse.reports.bench_builder.get_slump_tracker_analytics")
    def test_roster_composition(self, mock_get_analytics):
        # Mock slumped/graded players in analytics
        mock_get_analytics.return_value = {
            "status": "success",
            "players": [
                {"name": "Tank1", "class": "Warrior", "role": "Tank", "avg_grade": "S"},
                {"name": "Tank2", "class": "Paladin", "role": "Tank", "avg_grade": "A"},
                {"name": "Healer1", "class": "Druid", "role": "Healer", "avg_grade": "S"},
                {"name": "Healer2", "class": "Priest", "role": "Healer", "avg_grade": "A"},
                {"name": "Healer3", "class": "Paladin", "role": "Healer", "avg_grade": "B"},
                {"name": "Healer4", "class": "Shaman", "role": "Healer", "avg_grade": "B"},
                {"name": "Healer5", "class": "Monk", "role": "Healer", "avg_grade": "C"},
                {"name": "Dps1", "class": "Mage", "role": "DPS", "avg_grade": "S"},
                {"name": "Dps2", "class": "Warlock", "role": "DPS", "avg_grade": "S"},
                {"name": "Dps3", "class": "Hunter", "role": "DPS", "avg_grade": "A"},
                {"name": "Dps4", "class": "Rogue", "role": "DPS", "avg_grade": "A"},
                {"name": "Dps5", "class": "Demon Hunter", "role": "DPS", "avg_grade": "B"},
                {"name": "Dps6", "class": "Death Knight", "role": "DPS", "avg_grade": "B"},
                {"name": "Dps7", "class": "Priest", "role": "DPS", "avg_grade": "C"},
                {"name": "Dps8", "class": "Evoker", "role": "DPS", "avg_grade": "C"},
                {"name": "Dps9", "class": "Shaman", "role": "DPS", "avg_grade": "D"},
                {"name": "Dps10", "class": "Warrior", "role": "DPS", "avg_grade": "C"},
                {"name": "Dps11", "class": "Monk", "role": "DPS", "avg_grade": "C"},
                {"name": "Dps12", "class": "Paladin", "role": "DPS", "avg_grade": "C"},
                {"name": "Dps13", "class": "Druid", "role": "DPS", "avg_grade": "C"},
                {"name": "Dps14", "class": "Rogue", "role": "DPS", "avg_grade": "D"},
            ]
        }
        
        all_players = [
            "Tank1", "Tank2",
            "Healer1", "Healer2", "Healer3", "Healer4", "Healer5",
            "Dps1", "Dps2", "Dps3", "Dps4", "Dps5", "Dps6", "Dps7", "Dps8", "Dps9", "Dps10", "Dps11", "Dps12", "Dps13", "Dps14"
        ]
        
        # Test composition builder on encounter 3184 (Imperator Averzian: immunities/br)
        comp = build_roster_composition(encounter_id=3184, player_names=all_players)
        
        self.assertEqual(len(comp["roster"]), 20)
        self.assertEqual(len(comp["bench"]), 1)
        self.assertEqual(comp["boss_name"], "Imperator Averzian")
        
        # Verify 2 tanks and 4 healers got selected
        tanks = [p for p in comp["roster"] if p["role"] == "Tank"]
        healers = [p for p in comp["roster"] if p["role"] == "Healer"]
        self.assertEqual(len(tanks), 2)
        self.assertIn(len(healers), [4, 5])
        
        # Verify benched player has a supportive rotation reason
        bench_player = comp["bench"][0]
        self.assertIn("Roster rotation to optimize", bench_player["reason"])


class TestRecruitmentAuditor(unittest.TestCase):
    def test_report_card_structure(self):
        report = get_candidate_report_card("CandidateX", "illidan", "us")
        
        self.assertEqual(report["candidate"]["name"], "CandidateX")
        self.assertEqual(report["candidate"]["realm"], "illidan")
        self.assertEqual(report["candidate"]["region"], "US")
        self.assertIn(report["overall_grade"], ["S", "A", "B", "C", "D", "F"])
        self.assertGreaterEqual(report["panic_defensive_rate"], 0)
        self.assertGreaterEqual(report["preparation_score"], 0)
        self.assertGreater(len(report["history"]), 0)
        self.assertGreater(len(report["focus_tips"]), 0)

if __name__ == "__main__":
    unittest.main()
