import json
import logging
from pprint import pformat
import unittest
from binascii import hexlify, unhexlify

from pytezos.rpc.node import Node, RpcError
from pytezos.rpc.shell import Shell
from pytezos.tools.keychain import Keychain
from pytezos.encoding import base58_decode

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

    def make_trans_oper(self):
        head_hash = self.shell.head.hash()
        contract = self.shell.head.context.contracts[self.pkh1]
        counter = int(contract.counter()) + 1
        trans_oper = tezos.make_transaction_operation(self.pkh1, self.pkh2, 17, head_hash,
                                                           signature=self.fake_sig, counter=counter)
        return trans_oper


    def test_trans_oper(self):
        trans_oper = self.make_trans_oper()
        self.assertEqual(len(trans_oper['contents']), 1)
        oper = trans_oper['contents'][0]
        self.assertEqual(oper['kind'], 'transaction')


    def test_transaction_low_level(self):
        head_hash = self.shell.head.hash()

        contract = self.shell.head.context.contracts[self.pkh1]
        counter = int(contract.counter()) + 1

        constants = self.shell.head.context.constants()
        #logger.debug(f"constants = {pformat(constants)}")
        gas_limit = constants['hard_gas_limit_per_operation']
        storage_limit = constants['hard_storage_limit_per_operation']

        trans_oper = tezos.make_transaction_operation(self.pkh1, self.pkh2, 17, head_hash,
                                                      signature=self.fake_sig, counter=counter,
                                                      gas_limit=gas_limit)
        #print(f"oper = {pformat(trans_oper)}")
        try:
            resp = self.node.post("/chains/main/blocks/head/helpers/scripts/run_operation",
                                  json=trans_oper)
        except RpcError as exc:
            self.fail(f"RpcError fail: {exc}")
        except Exception as exc:
            self.fail(f"post exception: {exc}")
        else:
            trans_oper = trans_oper['contents'][0]
            resp_oper = resp['contents'][0]
            self.assertEqual(resp_oper['counter'], trans_oper['counter'])
            self.assertEqual(resp_oper['kind'], "transaction")

            result = resp_oper['metadata']['operation_result']
            self.assertEqual(result['status'], 'applied', f'result = {pformat(result)}')

            consumed_gas = int(result['consumed_gas'])
            self.assertGreater(consumed_gas, 1000)

            storage_used = 0    # TODO: how to get this? not appearing in results from scriptless address

            protocols = self.shell.head.protocols()
            protocol = protocols.get("protocol")
            self.assertRegex(protocol, r"^P")

            trans_oper2 = tezos.make_transaction_operation(self.pkh1, self.pkh2, 17, head_hash,
                                                           counter=counter,
                                                           gas_limit=consumed_gas+100,
                                                           storage_limit=0)

            resp2 = self.node.post("/chains/main/blocks/head/helpers/forge/operations",
                                  json=trans_oper2)
            self.assertRegex(resp2, r"^[a-f0-9]+$")
            oper_hex = resp2

            keychain = Keychain("secret_keys")
            key = keychain.get_key("fy") # TODO: name corresponds to self.pkh1

            signature = key.sign("03" + oper_hex)
            self.assertRegex(signature, r"^edsig")

            trans_oper3 = tezos.make_transaction_operation(self.pkh1, self.pkh2, 17, head_hash,
                                                           counter=counter,
                                                           gas_limit=consumed_gas+100,
                                                           storage_limit=0,
                                                           protocol=protocol,
                                                           signature=signature)
            resp3 = self.node.post("/chains/main/blocks/head/helpers/preapply/operations",
                                   json=[trans_oper3])

            raw_signature = base58_decode(signature.encode())
            hex_signature = raw_signature.hex()
            logger.debug(f"raw_signature = {raw_signature}")
            logger.debug(f"hex_signature = {hex_signature}")

            signed_oper_hex = oper_hex + hex_signature

            resp4 = self.node.post("/injection/operation?chain=main", signed_oper_hex)
            logger.debug(f"\nresp4 = {pformat(resp4)}\n")


if __name__ == "__main__":
    unittest.main()
