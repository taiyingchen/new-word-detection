import os
import pickle
from queue import Queue
from collections import defaultdict
from marisa_trie import BytesTrie


INT_BYTES = 4
BYTEORDER = 'big'


class Trie(object):
    def __init__(self):
        self.root = {'children': {}, 'depth': 0}
        self.total = 0
        self.trie_file_path = os.path.join(
            os.path.dirname(__file__), "./Trie.pkl")

    def build(self, tokens):
        """Build trie from a list of tokens
        """
        node = self.root
        depth = 0
        for token in tokens:
            depth += 1
            if token not in node['children']:
                node['children'][token] = {'freq': 0, 'depth': depth, 'visit': False, 'value': tokens[:depth], 'children': {}}
            node = node['children'][token]
            node['freq'] += 1
            self.total += 1

    def get(self, tokens):
        result = {'found': True, 'value': ''}
        node = self.root
        for token in tokens:
            if token not in node['children']:
                result['found'] = False
                return result
            node = node['children'][token]
            result = {**result, **node}
        return result

    def bfs(self, min_depth, max_depth=-1):
        """Generator for breadth-first search

        Returns
        -------
        node : Trie tree node
        """
        queue = Queue()
        queue.put(self.root)
        while not queue.empty():
            node = queue.get()

            if max_depth != -1 and node['depth'] > max_depth: 
                return
            elif node['depth'] >= min_depth:
                yield node

            for child in node['children'].values():
                if not child['visit']:
                    child['visit'] = True
                    queue.put(child)
        return

    def visualize(self):
        self.visualize_util(self.root, '')

    def visualize_util(self, node, pre, console=True, queue=[]):
        for i, child in enumerate(node['children']):
            if i != len(node['children'])-1:
                print(f'{pre}├──{child}') if console else queue.append(f'{pre}├──{child}')
                self.visualize_util(node['children'][child], pre+'│  ', console, queue)
            else:
                print(f'{pre}└──{child}') if console else queue.append(f'{pre}└──{child}')
                self.visualize_util(node['children'][child], pre+'   ', console, queue)

    def __len__(self):
        return self.total

    def load(self):
        """Load trie from pickle file
        """
        with open(self.trie_file_path, "rb") as f:
            data = pickle.load(f)
        self.root = data

    def test(self):
        """Testing interface
        """
        queue = []
        self.visualize_util(self.root, '', console=False, queue=queue)
        return '\n'.join(queue)


class BTrie(BytesTrie):
    def build(self, trie):
        trie = {k: v.to_bytes(INT_BYTES, byteorder=BYTEORDER) for k, v in trie.items()}
        super().__init__(trie.items())
        return self

    def items(self, key=''):
        return {k: int.from_bytes(v, byteorder=BYTEORDER) for k, v in super().items(key)}

    def merge(self, trie):
        # Get all elements in both trie
        self_trie = self.items()
        other_trie = trie.items()
        
        merge_trie = defaultdict(int)
        merge_trie.update(self_trie)
        for k, v in other_trie.items():
            merge_trie[k] += v
        
        return self.build(merge_trie)
