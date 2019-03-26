import os
import pickle


class Trie(object):
    def __init__(self):
        self.root = {'children': {}}
        self.total = 0
        self.trie_file_path = os.path.join(
            os.path.dirname(__file__), "./Trie.pkl")

    def build(self, tokens):
        """Build trie from a list of tokens
        """
        node = self.root
        for token in tokens:
            if token not in node['children']:
                node['children'][token] = {'freq': 0, 'children': {}}
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
            result['value'] += token
        return result

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
        self.visualize_util(self.root, '', False, queue)
        return '\n'.join(queue)