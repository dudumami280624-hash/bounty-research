import unittest
from run_deployment_fork import evaluate_output, TESTS

class ForkOutputTests(unittest.TestCase):
    def test_all_real_fork_checks_are_required(self):
        log="\n".join("[PASS] "+x+"(gas: 123)" for x in TESTS)
        log+=f"\nSuite result: ok. {len(TESTS)} tests passed; 0 failed;"
        ok,found=evaluate_output(0,log)
        self.assertTrue(ok)
        self.assertEqual(len(found),len(TESTS))

    def test_do_not_trust_partial_or_failed_fork(self):
        log="[PASS] "+TESTS[0]+"(gas: 123)\n4 tests passed; 0 failed;"
        self.assertFalse(evaluate_output(0,log)[0])
        log="\n".join("[PASS] "+x+"(gas: 123)" for x in TESTS)
        log+="\n4 tests passed; 0 failed;"
        self.assertFalse(evaluate_output(1,log)[0])

    def test_no_broadcast_in_official_runner_source(self):
        from pathlib import Path
        s=(Path(__file__).resolve().parent/"run_deployment_fork.py").read_text()
        self.assertNotIn('"--broadcast"',s)
        self.assertNotIn('"eth_sendRawTransaction"',s)
if __name__=="__main__":unittest.main()
