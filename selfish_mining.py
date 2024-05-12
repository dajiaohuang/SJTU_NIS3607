import random
from typing import List
from tqdm import tqdm
from copy import deepcopy

class BlockChain(object):
    def __init__(self, is_malicious: bool = False, previous_block=None):
        self.is_malicious = is_malicious
        self.previous_block = previous_block

class HonestNode(object):
    def __init__(self):
        self.public_chain: List[BlockChain] = []

class SelfishMiner(object):
    def __init__(self):
        self.public_chain: List[BlockChain] = []
        self.private_chain: List[BlockChain] = []
        self.private_chain_length = 0

class BlockchainSystem(object):
    def __init__(self, malicious_rate: float):
        self.malicious_rate = malicious_rate
        self.honest_node = HonestNode()
        self.selfish_miner = SelfishMiner()
        genesis_block = BlockChain(True, None)
        self.honest_node.public_chain.append(genesis_block)
        self.selfish_miner.public_chain.append(genesis_block)
        self.selfish_miner.private_chain.append(genesis_block)

    def selfish_mining(self, time_unit: int):
        progress_bar = tqdm(range(time_unit))
        for r in progress_bar:
            if random.random() < self.malicious_rate:
                self.selfish_find_block()
            else:
                self.other_find_block()
            if r == time_unit - 1:
                self.selfish_miner.public_chain = deepcopy(self.selfish_miner.private_chain)
            self.select_chain()
        blocks_from_pool = 0
        for block in self.honest_node.public_chain:
            if not block.is_malicious:
                blocks_from_pool += 1
        return blocks_from_pool / len(self.honest_node.public_chain)

    def selfish_find_block(self):
        delta = len(self.selfish_miner.private_chain) - len(self.selfish_miner.public_chain)
        self.selfish_miner.private_chain.append(BlockChain(False, self.selfish_miner.private_chain[-1]))
        self.selfish_miner.private_chain_length += 1
        if delta == 0 and self.selfish_miner.private_chain_length == 2:
            self.selfish_miner.public_chain = deepcopy(self.selfish_miner.private_chain)
            self.selfish_miner.private_chain_length = 0

    def other_find_block(self):
        self.honest_node.public_chain.append(BlockChain(True, self.honest_node.public_chain[-1]))
        delta = len(self.selfish_miner.private_chain) - len(self.selfish_miner.public_chain)
        if delta == 0:
            self.selfish_miner.private_chain = deepcopy(self.honest_node.public_chain)
            self.selfish_miner.private_chain_length = 0
        elif delta == 1:
            self.selfish_miner.public_chain = deepcopy(self.selfish_miner.private_chain)
        elif delta == 2:
            self.selfish_miner.public_chain = deepcopy(self.selfish_miner.private_chain)
            self.selfish_miner.private_chain_length = 0
        else:
            self.selfish_miner.public_chain = deepcopy(self.selfish_miner.private_chain[:len(self.selfish_miner.public_chain) + 1])

    def select_chain(self):
        if len(self.selfish_miner.public_chain) > len(self.honest_node.public_chain):
            self.honest_node.public_chain = deepcopy(self.selfish_miner.public_chain)
        elif len(self.selfish_miner.public_chain) < len(self.honest_node.public_chain):
            self.selfish_miner.public_chain = deepcopy(self.honest_node.public_chain)
        else:
            if random.random() < 0.5:
                self.honest_node.public_chain = deepcopy(self.selfish_miner.public_chain)

if __name__ == '__main__':
    time_unit = 10000
    for malicious_rate in [0.1, 0.2, 0.3, 0.4]:
        print(f"Malicious Rate: {malicious_rate}")
        blockchain_system = BlockchainSystem(malicious_rate)
        print(f"Selfish Mining Revenue: {blockchain_system.selfish_mining(time_unit)}")