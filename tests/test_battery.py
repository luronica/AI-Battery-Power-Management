import unittest

from battery.analytics import BatteryAnalytics
from battery.simulator import BatterySimulator
from battery.power_manager import select_policy


class BatteryTests(unittest.TestCase):
    def test_energy_integrates_in_watt_hours(self):
        analytics = BatteryAnalytics()
        sample = dict(voltage=3.8, current=0.2, temperature=28, device_load=0.45)
        first = analytics.process(sample, 0)
        second = analytics.process(sample, 3600)
        self.assertAlmostEqual(second["power"], 0.76)
        self.assertAlmostEqual(second["energy_consumed"], 0.76)
        self.assertLess(second["soc"], first["soc"])
        self.assertEqual(second["soh"], 94)

    def test_simulator_load_and_discharge(self):
        low, high = BatterySimulator(), BatterySimulator()
        for _ in range(60):
            a = low.sample(120, "LOW")
            b = high.sample(120, "HIGH")
        self.assertGreater(b["current"], a["current"])
        self.assertGreater(b["temperature"], a["temperature"])
        self.assertLess(high.soc, low.soc)
        self.assertLess(low.soc, 78)
        self.assertTrue(3 <= b["voltage"] <= 4.2)

    def test_all_modes_and_non_soc_triggers(self):
        sample = dict(soc=80, predicted_runtime=5, temperature=28, current=0.2, device_load=0.9)
        self.assertEqual(select_policy(sample)["mode"], "PERFORMANCE")
        self.assertEqual(select_policy({**sample, "device_load": 0.4})["mode"], "BALANCED")
        for change in ({"soc": 25}, {"predicted_runtime": 1}, {"temperature": 37}, {"current": 0.45}):
            self.assertEqual(select_policy({**sample, **change})["mode"], "POWER SAVING")
        for change in ({"soc": 5}, {"predicted_runtime": 0.1}, {"temperature": 41}, {"temperature": -1}):
            self.assertEqual(select_policy({**sample, **change})["mode"], "CRITICAL")
        self.assertEqual(select_policy({**sample, "soc": 32}, "POWER SAVING")["mode"], "POWER SAVING")
        self.assertEqual(select_policy({**sample, "current": 0.24}, "POWER SAVING")["mode"], "POWER SAVING")

    def test_optimization_lowers_current(self):
        normal, saving = BatterySimulator(), BatterySimulator()
        for _ in range(20):
            a = normal.sample(120, "HIGH", 1.0)
            b = saving.sample(120, "HIGH", 0.55)
        self.assertLess(b["current"], a["current"] * 0.65)
        self.assertGreater(saving.soc, normal.soc)

    def test_empty_battery(self):
        simulator = BatterySimulator({"soc": 0.001})
        sample = simulator.sample(1000, "HIGH")
        result = BatteryAnalytics().process(sample, 0)
        self.assertEqual(result["soc"], 0)
        self.assertEqual(sample["current"], 0)


if __name__ == "__main__":
    unittest.main()
