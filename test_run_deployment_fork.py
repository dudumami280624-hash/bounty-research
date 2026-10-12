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

class SnapshotTests(unittest.TestCase):
    def reader(self,method,params):
        if method=="eth_chainId":return hex(2651420)
        if method=="eth_blockNumber":return "0x64"
        if method=="eth_getBlockByNumber":return {"number":"0x64","hash":"0x"+"ab"*32}
        self.assertEqual(params[1],"0x64")
        return "0x6000"
    def test_snapshot_pins_every_code_read(self):
        from run_deployment_fork import deployment_snapshot
        s=deployment_snapshot(self.reader)
        self.assertEqual(s["fork_block_number"],100)
        self.assertEqual(len(s["deployment_code"]),3)
        self.assertFalse(s["deployment_source_match_verified"])
    def test_wrong_chain_and_empty_code_rejected(self):
        from run_deployment_fork import deployment_snapshot
        for method,bad in (("eth_chainId","0x1"),("eth_getCode","0x")):
            with self.assertRaises(ValueError):
                deployment_snapshot(lambda m,p: bad if m==method else self.reader(m,p))
    def test_writes_are_rejected_before_network(self):
        from run_deployment_fork import rpc_read
        with self.assertRaises(ValueError):
            rpc_read("eth_sendTransaction",[])
if __name__=="__main__":unittest.main()

