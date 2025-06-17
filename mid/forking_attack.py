import random
from tqdm import tqdm
from typing import List
import copy
import numpy as np
from pow_simulate import Node as HonestNode, Block, set_random_seed, select_chain

SEED = 123  # 随机数种子，用于设置随机数生成的起始点
NUM_SIMULATIONS = 1000  # 模拟的次数
NUM_NODES = 200  # 节点的数量
BLOCK_GEN_PROB = 0.00001  # 生成新区块的概率
MAX_QUERIES = 100  # 最大查询次数

class MaliciousNode(HonestNode):
    def __init__(self, id_: int, malicious_node_count: int):
        super().__init__(id_)
        self.count = malicious_node_count  # 恶意节点的数量
        self.chain = [Block(-1, None)]  # 区块链，初始只有一个创世块
        self.id = id
    
    def mine_block(self, block_gen_prob, max_queries):
        queries = 0
        while queries < max_queries * self.count:
            if random.random() < block_gen_prob:  # 根据生成新区块的概率生成新区块
                self.chain.append(Block(self.id, self.chain[-1]))  # 将新区块添加到区块链上
                break
            queries += 1

if __name__ == '__main__':
    set_random_seed(SEED)  # 设置随机数种子
    max_length = 10  # 最大区块链长度
    for malice_rate in np.linspace(0.1, 0.4, 4):  # 不同的恶意节点比例
        probabilities = []  # 存储不同区块链长度对应的成功概率
        for length in range(1, max_length+1):  # 不同的区块链长度
            honest_count = int(NUM_NODES * (1 - malice_rate))  # 诚实节点的数量
            malicious_count = NUM_NODES - honest_count  # 恶意节点的数量
            success_count = 0  # 成功的次数
            progress_bar = tqdm(range(NUM_SIMULATIONS))  # 进度条
            for _ in progress_bar:
                honest_nodes = [HonestNode(i) for i in range(honest_count)]  # 创建诚实节点列表
                malicious_node = MaliciousNode(honest_count, malicious_count)  # 创建恶意节点
                flag = False
                while not flag:
                    for node in honest_nodes:
                        node.mine_block(BLOCK_GEN_PROB, MAX_QUERIES)  # 诚实节点挖矿
                    malicious_node.mine_block(BLOCK_GEN_PROB, MAX_QUERIES)  # 恶意节点挖矿
                    honest_length = select_chain(honest_nodes)  # 选择诚实节点中最长的区块链长度
                    malicious_length = len(malicious_node.chain)  # 恶意节点的区块链长度
                    if malicious_length >= (length + 1) or honest_length >= (length + 1):
                        flag = True
                        if malicious_length > honest_length:  # 如果恶意节点的区块链更长，则算作成功
                            success_count += 1
                progress_bar.set_description(f'Length: {length}, Success Count: {success_count}')
            probabilities.append(success_count / NUM_SIMULATIONS)  # 计算成功概率
        print(f'Malice Rate: {malice_rate}, Probabilities: {probabilities}, E(Length): {sum([i * probabilities[i - 1] for i in range(1, max_length+1)])}')