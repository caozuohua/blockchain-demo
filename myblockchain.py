#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

"""
source_url: https://www.cnblogs.com/tinyxiong/p/7761026.html
"""

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

from flask import Flask, jsonify, request


class BlockChain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # use set() to avoid duplication
        self.nodes = set()

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        create a new block and append it to the chain
        :return:
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        create a new transaction to the list of transaction
        :param sender:<str> address of sender
        :param recipient:<str> address of recipient
        :param amount:<int> number of the amount
        :return:<int> the index of the block that hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1


    @staticmethod
    def hash(block):
        """
        hash a block
        :param block:<dict> block
        :return:<str> sha256 of the block
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        :return: the last block in the chain
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        proof of work
        :param last_proof:<int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        proof to be valid or not
        :param last_proof: <int> previous proof
        :param proof: <int> current proof
        :return: <bool> True if correct; False if not
        """

        guess = '{0}{1}'.format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    def register_node(self, address):
        """
        add new worker nodes
        :param address: <str> ip:port of the node
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        whether given blockchain is valid
        :param chain: <list> blockchain list
        :return: <bool> True for valid, False for invalid
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n------------------------------------------\n")

            if block['previous_hash'] != self.hash(lash_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_confilicts(self):
        """
        to resolve confilicts
        :return: <bool> True if chain been replaced, False if don`t
        """

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get("http://{0}/chain".format(node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


app = Flask(__name__)

node_identifier = str(uuid4()).replace('_', '')

blockchain = BlockChain()


@app.route('/mime', methods=['GET'])
def mime():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1,
    )

    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200
    # return 'To mime a new block'


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    # test whether all items in required are in values
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': 'Transaction will be added to block{0}'.format(index)}
    return jsonify(response), 201
    # return 'To new transaction'


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get("nodes")
    if nodes is None:
        return "Error: Invalid node!"

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New node has been appended',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def conosensus():
    replaced = blockchain.resolve_confilicts()

    if replaced:
        response = {
            'message': 'THIS CHAIN HAS BEEN REPLACED!',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'THIS CHAIN HAS BEEN AUTHORITATIVED! OK!',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='192.168.81.86', port=55555)
