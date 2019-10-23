import json
import pprint
import sys

from pytezos.crypto import Key

#from pytezos.rpc.node import Node
#from pytezos.rpc.shell import Shell


def received_message(message):
    print(f"message: {message}")

    outputs = []
    body = message["body"].strip()

    if body.startswith("!ping"):
        outputs += ping(message)

    elif body.startswith("!key"):
        outputs += key(message)

    return outputs


def ping(message):
    content = {"body": "pong", "msgtype": "m.notice"}
    return [content]


def key(message):
    key = Key.from_alias("fy", tezos_client_dir=".")
    pk = key.public_key()
    pkh = key.public_key_hash()

    content = code_notice(f"pkh = {pkh}")
    return [content]


"""
def head(message):
    node_url = "http://f.ostraca.org:8732"
    shell = Shell(Node(node_url))
    head = shell.head()

    body = pprint.pformat(head.get("header"))

    content = {
        "body": body,
        "formatted_body": "<pre><code>" + body + "</code></pre",
        "msgtype": "m.notice",
        "format": "org.matrix.custom.html",
    }
    return [content]


def sign(message):
    keychain = Keychain("secret_keys")
    key = keychain.get_key("foobar")

    signature = key.sign(message["body"])
    content = {
        "body": signature,
        "formatted_body": "<pre><code>" + signature + "</code></pre>",
        "msgtype": "m.notice",
        "format": "org.matrix.custom.html",
    }
    return [content]


def constants(message):
    node_url = "http://f.ostraca.org:8732"
    shell = Shell(Node(node_url))

    constants = shell.head.context.constants()
    content = code_notice(pprint.pformat(constants))
    return [content]


"""

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
