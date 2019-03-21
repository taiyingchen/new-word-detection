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

    def __len__(self):
        return self.total

    def load(self):
        """Load trie from pickle file
        """
        with open(self.trie_file_path, "rb") as f:
            data = pickle.load(f)
        self.root = data
