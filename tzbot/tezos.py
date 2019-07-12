import json

from pytezos.rpc.shell import Shell, Node


class Tezos:

    def __init__(self, rpc_url):
        self.rpc_url = rpc_url
        self.shell = Shell(Node(self.rpc_url))

    def head_hash(self):
        return self.shell.head.get('hash')



def make_transaction_operation(source, destination, amount, branch,
                               fee=1, counter=1, gas_limit=800000, storage_limit=60000,
                               signature=None) -> str:
    operation = {
        'branch': branch,
        'contents': [
            {
                'kind': "transaction",
                "source": source,
                "fee": str(fee),
                "counter": str(counter),
                "gas_limit": str(gas_limit),
                "storage_limit": str(storage_limit),
                "amount": str(amount),
                "destination": destination,
            }
        ],
    }
    if signature:
        operation['signature'] = signature

    #return json.dumps(operation, indent=4)
    return operation
