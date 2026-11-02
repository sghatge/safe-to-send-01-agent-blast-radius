import unittest

from blast_radius import analyse, risk_score

ALL = {"schema_browse": ["read"], "query_run": ["read", "write"], "delivery_send": ["execute"],
       "workflow_control": ["list", "stop"], "js_execute": ["write", "http"]}


class BlastRadiusTest(unittest.TestCase):
    def test_full_access_no_controls_exposes_everything(self):
        rows = analyse(ALL, [])
        self.assertTrue(all(r["status"] == "EXPOSED" for r in rows))
        self.assertEqual(risk_score(rows), 100)

    def test_read_only_agent_reaches_nothing_dangerous(self):
        rows = analyse({"schema_browse": ["read"], "query_run": ["read"]}, [])
        self.assertEqual({r["status"] for r in rows}, {"unreachable"})

    def test_controls_mitigate(self):
        rows = analyse(ALL, ["sql_write_block"])
        delete = next(r for r in rows if r["id"] == "full_table_delete")
        self.assertEqual(delete["status"], "mitigated")
        self.assertEqual(delete["stopped_by"], ["sql_write_block"])

    def test_one_call_outcomes_rank_first_among_equal_severity(self):
        rows = analyse(ALL, [])
        sev8 = [r for r in rows if r["severity"] == 8]
        self.assertEqual(sev8[0]["calls"], 1)


if __name__ == "__main__":
    unittest.main()
