import os
import pickle


class Trie(object):
    def __init__(self):
        self.root = {}
        self.total = 0
        self.trie_file_path = os.path.join(
            os.path.dirname(__file__), "./Trie.pkl")

    def build(self, tokens):
        """Build trie from a list of tokens
        """
        node = self.root
        sent = ''
        for token in tokens:
            sent += token
            if token not in node:
                node[token] = {'freq': 0, 'value': sent}
            node = node[token]
            node['freq'] += 1
            self.total += 1

    def get(self, tokens):
        result = {'found': True}
        node = self.root
        for token in tokens:
            if token not in node:
                result['found'] = False
                return result
            node = node[token]
            result['value'] = node['value']
            result['freq'] = node['freq']
        return result

    def __len__(self):
        return self.total

    def load(self):
        """Load trie from pickle file
        """
        with open(self.trie_file_path, "rb") as f:
            data = pickle.load(f)
        self.root = data
