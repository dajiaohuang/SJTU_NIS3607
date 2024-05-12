import random
from tqdm import tqdm
from typing import List
import copy
import numpy as np

SEED = 123
ROUNDS = 2000
NODE_NUM = 500
MAX_ORACLE_QUERY = 100

# 定义节点类
class Node:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.blockchain = [Block(-1, None)]  # 节点的区块链，初始只有一个创世块

    def mine_block(self, block_gen_rate, max_oracle_query):
        ctr = 0
        while ctr < max_oracle_query:  # 最多进行 max_oracle_query 次尝试
            if random.random() < block_gen_rate:  # 以 block_gen_rate 的概率创建新的区块
                self.blockchain.append(Block(self.node_id, self.blockchain[-1]))
                break
            ctr += 1

# 定义区块类
class Block:
    def __init__(self, creator_id: int, prev_block):
        self.creator_id = creator_id
        self.prev_block = prev_block

# 选择最长的区块链作为有效链，并更新其他节点的区块链
def select_chain(node_list: List[Node]):
    id_list = []
    max_length = 0
    for node in node_list:
        if len(node.blockchain) > max_length:
            max_length = len(node.blockchain)
    for node in node_list:
        if len(node.blockchain) == max_length:
            id_list.append(node.node_id)

    for node in node_list:
        selected_id = random.choice(id_list)
        node.blockchain = copy.deepcopy(node_list[selected_id].blockchain[:max_length])
    return max_length

# 设置随机种子
def set_random_seed(seed):
    import os
    import numpy as np
    import torch
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True

if __name__ == "__main__":
    set_random_seed(SEED)

    honest_node_num = NODE_NUM
    nodes = [Node(node_id) for node_id in range(honest_node_num)]  # 创建节点列表

    for block_gen_rate in [1e-7, 1e-6, 1e-5, 1e-4]:  # 不同的区块生成率
        print(f"Block Generation Rate: {block_gen_rate}")
        chain_length_per_round = []  # 每轮的最长有效链长度记录列表

        progress_bar = tqdm(range(ROUNDS))
        for round_num in progress_bar:
            for node in nodes:
                node.mine_block(block_gen_rate, MAX_ORACLE_QUERY)  # 节点进行挖矿
            length = select_chain(nodes)  # 选择最长的区块链
            chain_length_per_round.append(length)
            progress_bar.set_description(f"Max Valid Chain Length: {length}, Chain Growth Rate: {(length - 1) / (round_num + 1)}")

        chain_length_per_round = np.array(chain_length_per_round)
        print(f"Block Generation Rate: {block_gen_rate}, Chain Growth Rate: {(length - 1) / ROUNDS}")