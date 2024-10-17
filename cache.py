import sys
import struct
import numpy as np
import random
from collections import deque
import matplotlib.pyplot as plt  

class CacheEntry:
    def __init__(self):
        self.valid = False
        self.tag = None

class CacheSimulator:
    def __init__(self, num_sets, block_size, assoc, policy, output_mode, input_file):
        self.num_sets = num_sets
        self.block_size = block_size
        self.assoc = assoc
        self.policy = policy
        self.output_mode = output_mode
        self.input_file = input_file
        self.cache = self.initialize_cache()
        self.replacement_data = self.setup_replacement_data()
        self.addresses = self.read_input_file()
        self.global_cache_filled = False  

    def initialize_cache(self):
        return [[CacheEntry() for _ in range(self.assoc)] for _ in range(self.num_sets)]

    def setup_replacement_data(self):
        if self.policy in ['L', 'F']:
            return [deque() for _ in range(self.num_sets)]
        return None

    def read_input_file(self):
        with open(self.input_file, 'rb') as f:
            binary_data = f.read()
        num_addresses = len(binary_data) // 4
        return struct.unpack('>' + 'I' * num_addresses, binary_data)

    def is_cache_full(self, set_index):
        return all(entry.valid for entry in self.cache[set_index])

    def find_empty_way(self, set_index):
        for i, entry in enumerate(self.cache[set_index]):
            if not entry.valid:
                return i
        return None

    def check_global_cache_filled(self):
        self.global_cache_filled = all(
            all(entry.valid for entry in set_entries) for set_entries in self.cache
        )

    def apply_replacement_policy(self, set_index, block_tag):
        if self.policy == 'R':  # Random Replacement
            random_way = random.randint(0, self.assoc - 1)
            self.cache[set_index][random_way].tag = block_tag
        elif self.policy == 'L':  # LRU Replacement
            least_recently_used = self.replacement_data[set_index].popleft()
            self.cache[set_index][least_recently_used].tag = block_tag
            self.replacement_data[set_index].append(least_recently_used)
        elif self.policy == 'F':  # FIFO Replacement
            first_in = self.replacement_data[set_index].popleft()
            self.cache[set_index][first_in].tag = block_tag
            self.replacement_data[set_index].append(first_in)

    def handle_miss(self, set_index, tag, compulsory_miss, capacity_miss, conflict_miss):
        empty_way = self.find_empty_way(set_index)

        if empty_way is not None:  # Miss Compulsório
            self.cache[set_index][empty_way].valid = True
            self.cache[set_index][empty_way].tag = tag
            if self.policy in ['F', 'L']:
                self.replacement_data[set_index].append(empty_way)
            compulsory_miss += 1
            return compulsory_miss, capacity_miss, conflict_miss
        else:
            self.check_global_cache_filled()
            if self.global_cache_filled:
                capacity_miss += 1
            else:
                conflict_miss += 1
            self.apply_replacement_policy(set_index, tag)
        return compulsory_miss, capacity_miss, conflict_miss

    def handle_hit(self, set_index, way):
        if self.policy == 'L':
            if way in self.replacement_data[set_index]:
                self.replacement_data[set_index].remove(way)
            self.replacement_data[set_index].append(way)

    def process_address(self, address, compulsory_miss, capacity_miss, conflict_miss, hit_count):
        tag = address >> (n_bits_offset + n_bits_index)
        set_index = (address >> n_bits_offset) & ((1 << n_bits_index) - 1)

        for way, entry in enumerate(self.cache[set_index]):
            if entry.valid and entry.tag == tag:
                hit_count += 1
                self.handle_hit(set_index, way)
                return compulsory_miss, capacity_miss, conflict_miss, hit_count

        compulsory_miss, capacity_miss, conflict_miss = self.handle_miss(set_index, tag, compulsory_miss, capacity_miss, conflict_miss)
        return compulsory_miss, capacity_miss, conflict_miss, hit_count

    def simulate_cache(self):
        miss_type_counts = {'compulsory': 0, 'capacity': 0, 'conflict': 0}
        hit_count = 0
        for address in self.addresses:
            miss_type_counts['compulsory'], miss_type_counts['capacity'], miss_type_counts['conflict'], hit_count = self.process_address(
                address, miss_type_counts['compulsory'], miss_type_counts['capacity'], miss_type_counts['conflict'], hit_count)

        return miss_type_counts, hit_count, len(self.addresses)

    def generate_report(self, total_accesses, hit_count, miss_type_counts):
        hit_rate = hit_count / total_accesses
        total_misses = sum(miss_type_counts.values())
        miss_rate = total_misses / total_accesses
        compulsory_rate = miss_type_counts['compulsory'] / total_misses if total_misses else 0
        capacity_rate = miss_type_counts['capacity'] / total_misses if total_misses else 0
        conflict_rate = miss_type_counts['conflict'] / total_misses if total_misses else 0

        if self.output_mode == 1:
            print(f"{total_accesses}, {hit_rate:.4f}, {miss_rate:.4f}, {compulsory_rate:.2f}, {capacity_rate:.2f}, {conflict_rate:.2f}")
        else:
            print(f"Relatório da Simulação da Cache:")
            print(f"-------------------------------")
            print(f"Total de acessos: {total_accesses}")
            print(f"Taxa de hits: {hit_rate:.4%}")
            print(f"Taxa de misses: {miss_rate:.4%}")
            print(f"Misses compulsórios: {compulsory_rate:.2%}")
            print(f"Misses de capacidade: {capacity_rate:.2%}")
            print(f"Misses de conflito: {conflict_rate:.2%}")
            print(f"-------------------------------")

    def generate_graph(self, miss_type_counts, hit_count, total_accesses):
        labels = ['Hits', 'Compulsórios', 'Capacidade', 'Conflito']
        sizes = [hit_count, miss_type_counts['compulsory'], miss_type_counts['capacity'], miss_type_counts['conflict']]
        colors = ['#66b3ff', '#99ff99', '#ff6666', '#ffcc99']
        explode = (0.1, 0, 0, 0)  

        plt.figure(figsize=(7, 7))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
        plt.title("Distribuição de Hits e Misses")
        plt.axis('equal')  
        plt.show()

def main():
    if len(sys.argv) != 8:  
        print("Número incorreto de argumentos. Utilize:")
        print("python cache_simulator.py <num_sets> <block_size> <assoc> <policy> <output_mode> <input_file> <show_graph>")
        exit(1)

    num_sets = int(sys.argv[1])
    block_size = int(sys.argv[2])
    assoc = int(sys.argv[3])
    policy = sys.argv[4]
    output_mode = int(sys.argv[5])
    input_file = sys.argv[6]
    show_graph = int(sys.argv[7])  

    global n_bits_offset, n_bits_index
    n_bits_offset = int(np.log2(block_size))
    n_bits_index = int(np.log2(num_sets))

    cache_sim = CacheSimulator(num_sets, block_size, assoc, policy, output_mode, input_file)
    miss_type_counts, hit_count, total_accesses = cache_sim.simulate_cache()
    cache_sim.generate_report(total_accesses, hit_count, miss_type_counts)

    if show_graph == 1:  
        cache_sim.generate_graph(miss_type_counts, hit_count, total_accesses)

if __name__ == '__main__':
    main()
