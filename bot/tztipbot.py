import pprint
import sys

sys.path.append('./vendor/pytezos')
from pytezos.tools.keychain import Keychain
from pytezos.rpc.node import Node


def received_message(message):
    print(f"message: {message}")

    outputs = []
    body = message['body'].strip()

    if body.startswith("!ping"):
        outputs += ping(message)

    elif body.startswith("!keys"):
        outputs += keys(message)

    elif body.startswith("!key"):
        outputs += key(message)

    elif body.startswith("!head"):
        outputs += head(message)

    elif body.startswith("!sign"):
        outputs += sign(message)

    return outputs


def ping(message):
    content = {
        "body": "pong",
        "msgtype": "m.notice",
    }
    return [content]


def keys(message):
    keychain = Keychain("secret_keys")
    content = {
        "body": str(keychain.list_keys()),
        "msgtype": "m.notice",
    }
    return [content]


def key(message):
    keychain = Keychain("vendor/secret_keys")
    key = keychain.get_key('foobar')
    pk = key.public_key()
    pkh = key.public_key_hash()

    content = {
        "body": f"pkh = {pkh}",
        "msgtype": "m.notice",
    }
    return [content]

def head(message):
    node_url = "http://f.ostraca.org:8732"
    node = Node(node_url)

    head = node.get("/chains/main/blocks/head")

    content = {
        "body": pprint.pformat(head['header']),
        "formatted_body": "<pre><code>" + pprint.pformat(head['header']) + "</code></pre",
        "msgtype": "m.notice",
        "format": "org.matrix.custom.html",
    }
    return [content]

def sign(message):
    keychain = Keychain("vendor/secret_keys")
    key = keychain.get_key('foobar')

    signature = key.sign(message['body'])
    content = {
        "body": signature,
        "msgtype": "m.notice",
    }
    return [content]
