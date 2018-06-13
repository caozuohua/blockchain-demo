#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import hashlib

class Block():

    def __init__(self, index, timestamp, data, preHash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.preHash = preHash
        self.hash = self.calculateHash()

    def calculateHash(self):
        sha256 = hashlib.sha256()
        sha256.update((str(self.index) + self.preHash + self.timestamp + self.data).encode('utf-8'))
        res = sha256.hexdigest()
        return res

    def __str__(self):
        return 'index:' + str(self.index) + " timestamp:" + str(self.timestamp) + " data:" + str(self.data) + " preHash:" + str(self.preHash) + " hash:" + str(self.hash)


class BlockChain():

        def __init__(self):
            self.chain = [self.createBenesisBlock()];

        def createBenesisBlock(self):
            return Block(0, "01/01/2018", "Genesis block", "0");

        def getLatestBlock(self):
            return self.chain[len(self.chain) - 1]

        def addBlock(self, newBlock):
            newBlock.preHash = self.getLatestBlock().hash
            newBlock.hash = newBlock.calculateHash()
            self.chain.append(newBlock)

        def display(self):
            for i in range(len(self.chain)):
                print("self.chain[%s]: %s" % (i, self.chain[i]))
                print("")


if __name__ == '__main__':
    coin = BlockChain()
    coin.addBlock(Block(1, '20/03/2018', 'data-1', ''))
    coin.display()