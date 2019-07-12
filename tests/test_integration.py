import json
import logging
import pprint
import unittest

from pytezos.rpc.node import Node, RpcError
from pytezos.rpc.shell import Shell

import tzbot.tezos as tezos

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

# enable to see debug output from urllib
#logging.basicConfig(level=logging.DEBUG)


class TestPytezos(unittest.TestCase):
    def setUp(self):
        rpc_url = "http://f.ostraca.org:8732/"
        self.shell = Shell(Node(rpc_url))
        self.pkh1 = "tz1fyYJwgV1ozj6RyjtU1hLTBeoqQvQmRjVv"

    def test_head(self):
        head = self.shell.head()
        #logger.debug(f"head = {head}")
        hash = head.get("hash")
        self.assertIsNotNone(hash)

    def test_head_hash(self):
        head_hash = self.shell.head.hash()
        #logger.debug(f"head_hash = {head_hash}")
        self.assertRegex(head_hash, r"^B[KLM].{49}$")

    def test_head_hash2(self):
        head_hash = self.shell.head.get("hash")
        #logger.debug(f"head_hash = {head_hash}")
        self.assertRegex(head_hash, r"^B[KLM].{49}$")

    def test_constants(self):
        constants = self.shell.head.context.constants()
        #logger.debug(f"constants = {constants}")
        self.assertIsNotNone(constants)
        self.assertIsNotNone(constants.get("blocks_per_cycle"))

    def test_counter(self):
        contract = self.shell.head.context.contracts[self.pkh1]
        #logger.debug(f"contract = {contract}")
        counter = contract.counter()
        self.assertIsNotNone(counter)


class TestTezos(unittest.TestCase):
    def setUp(self):
        rpc_url = "http://f.ostraca.org:8732/"
        self.node = Node(rpc_url)
        self.shell = Shell(self.node)
        self.pkh1 = "tz1fyYJwgV1ozj6RyjtU1hLTBeoqQvQmRjVv"
        self.pkh2 = "tz1Nhj1wHs7nzHSwdybxrYjpEQCTaEpWwu6w"
        self.fake_sig = "edsigtXomBKi5CTRf5cjATJWSyaRvhfYNHqSUGrn4SdbYRcGwQrUGjzEfQDTuqHhuA8b2d8NarZjz8TRf65WkpQmo423BtomS8Q"

    def test_transaction_low_level(self):
        head_hash = self.shell.head.hash()
        contract = self.shell.head.context.contracts[self.pkh1]
        counter = int(contract.counter()) + 1

        trans_oper = tezos.make_transaction_operation(self.pkh1, self.pkh2, 17, head_hash,
                                                           signature=self.fake_sig, counter=counter)
        #logger.debug(f"oper = {trans_oper_json}")
        try:
            resp = self.node.post("/chains/main/blocks/head/helpers/scripts/run_operation",
                                  json=trans_oper)
        except RpcError as exc:
            self.fail(f"RpcError fail: {exc}")
        except Exception as exc:
            self.fail(f"post exception: {exc}")
        else:
            #logger.debug(f"resp = {resp}")
            resp_oper = resp['contents'][0]
            self.assertEqual(resp_oper['counter'], str(counter))
            self.assertEqual(resp_oper['kind'], "transaction")
            #self.fail(f"STUB:\nresp={pprint.pformat(resp)}")

if __name__ == "__main__":
    unittest.main()
