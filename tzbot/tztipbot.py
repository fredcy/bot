import json
import pprint
import sys
import logbook

from pytezos.crypto import Key
from pytezos.rpc import RpcNode, RpcQuery


log = logbook.Logger("tztipbot")


class TzTipBot:
    def __init__(self, node_uri):
        self.node_uri = node_uri
        self.rpcQuery = RpcQuery(RpcNode(uri=self.node_uri))

    def received_message(self, message):
        log.debug(f"message: {message}")

        outputs = []
        body = message["body"].strip()

        if body.startswith("!ping"):
            outputs += self.ping(message)

        elif body.startswith("!echo"):
            outputs += self.echo(message)

        elif body.startswith("!key"):
            outputs += self.key(message)

        elif body.startswith("!head"):
            outputs += self.head(message)

        elif body.startswith("!sign"):
            outputs += self.sign(message)

        elif body.startswith("!constants"):
            outputs += self.constants(message)

        return outputs

    def ping(self, message):
        content = {"body": "pong", "msgtype": "m.notice"}
        return [content]

    def echo(self, message):
        content = {"body": f"message.body=\"{message['body']}\"", "msgtype": "m.notice"}
        return [content]

    def key(self, message):
        key = Key.from_alias("fy", tezos_client_dir=".")
        pk = key.public_key()
        pkh = key.public_key_hash()

        content = code_notice(f"pkh = {pkh}")
        return [content]

    def head(self, message):
        header = self.rpcQuery.chains.main.blocks.head.header()
        body = pprint.pformat(header)
        content = code_notice(body)
        return [content]

    def sign(self, message):
        key = Key.from_alias("fy", tezos_client_dir=".")
        signature = key.sign(message["body"])
        content = {
            "body": signature,
            "formatted_body": "<pre><code>" + signature + "</code></pre>",
            "msgtype": "m.notice",
            "format": "org.matrix.custom.html",
        }
        return [content]

    def constants(self, message):
        constants = self.rpcQuery.chains.main.blocks.head.context.constants()
        content = code_notice(pprint.pformat(constants))
        return [content]


def code_notice(code):
    """ Create m.notice message content with formatted code """
    return {
        "body": code,
        "formatted_body": "<pre><code>" + code + "</code></pre>",
        "msgtype": "m.notice",
        "format": "org.matrix.custom.html",
    }


# several alphanet accounts of mine
fy_alias = "fy"
fy_pkh = "tz1fyYJwgV1ozj6RyjtU1hLTBeoqQvQmRjVv"
foobar_pkh = "tz1Nhj1wHs7nzHSwdybxrYjpEQCTaEpWwu6w"


"""
def transaction(message):
    head_hash = get_head_hash()
    constants = get_constants()
    trans_oper = make_transaction_operation(
        fy_pkh, foobar_pkh, 42 * 1_000_000, head_hash
    )
"""
