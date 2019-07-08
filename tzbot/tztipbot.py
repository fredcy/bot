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

    elif body.startswith("!constants"):
        outputs += constants(message)

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
    keychain = Keychain("secret_keys")
    key = keychain.get_key('foobar')

    signature = key.sign(message['body'])
    content = {
        "body": signature,
        "formatted_body": "<pre><code>" + signature + "</code></pre>",
        "msgtype": "m.notice",
        "format": "org.matrix.custom.html",
    }
    return [content]

def constants(message):
    node_url = "http://f.ostraca.org:8732"
    node = Node(node_url)
    constants = node.get("/chains/main/blocks/head/context/constants")
    content = code_notice(pprint.pformat(constants))
    return [content]


def code_notice(code):
    return {
        "body": code,
        "formatted_body": "<pre><code>" + code + "</code></pre>",
        "msgtype": "m.notice",
        "format": "org.matrix.custom.html",
    }

# several alphanet accounts of mine
fy_pkh = "tz1fyYJwgV1ozj6RyjtU1hLTBeoqQvQmRjVv"
foobar_pkh = "tz1Nhj1wHs7nzHSwdybxrYjpEQCTaEpWwu6w"

def transaction(message):
    head_hash = get_head_hash()

    constants = get_constants()

    source = fy_pkh
    destination = foobar_pkh
    amount = 42 * 1000000
    fee = 1000                  # TODO
    storage_limit = 60000       # TODO

    operation = {
        'branch': head_hash,
        'contents': [
            {
                'kind': "transaction",
                "source": fy_pkh,
                "fee": str(fee),
                "counter": str(counter),
                "gas_limit": constants['hard_gas_limit_per_operation'],
                "storage_limit": str(storage_limit),
                "amount": str(amount),
                "destination": foobar_pkh,
            }
        ]
    }



    
