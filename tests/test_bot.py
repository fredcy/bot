import json
import logging
import unittest

#import sys; print(sys.path)

from tzbot import __version__
from tzbot.tezos import make_transaction_operation 

logger = logging.getLogger()


class TestBot(unittest.TestCase):
    def setUp(self):
        # several alphanet accounts of mine
        self.pkh1 = "tz1fyYJwgV1ozj6RyjtU1hLTBeoqQvQmRjVv"
        self.pkh2 = "tz1Nhj1wHs7nzHSwdybxrYjpEQCTaEpWwu6w"
        self.branch = "BM8hgE2Fmer4BP6xizFmeiVSSb3DjgomPw538TkPzMBrvqi93Ab"
        self.fake_sig = "edsigtXomBKi5CTRf5cjATJWSyaRvhfYNHqSUGrn4SdbYRcGwQrUGjzEfQDTuqHhuA8b2d8NarZjz8TRf65WkpQmo423BtomS8Q"

    def test_version(self):
        assert __version__ == '0.1.0'

    def test_make_trans_sig(self):
        counter = 26146
        trans_oper = make_transaction_operation(self.pkh1, self.pkh2, 42, self.branch,
                                                counter=counter, signature=self.fake_sig)

        self.assertEqual(trans_oper['branch'], self.branch)
        self.assertEqual(trans_oper['contents'][0]['source'], self.pkh1)
        self.assertEqual(trans_oper['contents'][0]['counter'], str(counter))
        self.assertEqual(trans_oper['signature'], self.fake_sig)

    def test_make_trans(self):
        counter = 26146
        trans_oper = make_transaction_operation(self.pkh1, self.pkh2, 42, self.branch,
                                                counter=counter)

        self.assertEqual(trans_oper['branch'], self.branch)
        self.assertEqual(trans_oper['contents'][0]['source'], self.pkh1)
        self.assertEqual(trans_oper['contents'][0]['counter'], str(counter))
        self.assertEqual(trans_oper.get('signature'), None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #logger.setLevel(logging.WARN)

    unittest.main()
