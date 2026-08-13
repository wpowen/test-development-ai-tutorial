import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import agent_quality_lab as lab

class AgentQualityLabs(unittest.TestCase):
    def test_all_baselines_and_repairs_pass(self):
        for topic in lab.TOPICS:
            self.assertEqual(lab.report(topic,"baseline")["failed_oracle_ids"],[],topic)
            self.assertEqual(lab.report(topic,"repair")["failed_oracle_ids"],[],topic)

    def test_all_faults_fail_named_oracle(self):
        for topic in lab.TOPICS:
            r=lab.report(topic,"fault")
            self.assertEqual(r["verdict"],"FAIL",topic)
            self.assertTrue(r["failed_oracle_ids"],topic)
            self.assertEqual(r["not_run"][0],"live model")

    def test_security_pages_never_write_in_baseline(self):
        self.assertFalse(lab.state("TD-T16","baseline")["call"]["write_executed"])
        self.assertFalse(lab.state("TD-T17","baseline")["tool"]["write_executed"])
