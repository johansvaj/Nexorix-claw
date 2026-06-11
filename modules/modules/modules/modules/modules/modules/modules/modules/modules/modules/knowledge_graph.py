import json
import os
import networkx as nx

class KnowledgeGraph:
    def __init__(self, store_path: str = "~/.nexcorix/kg.json"):
        self.path = os.path.expanduser(store_path)
        self.graph = nx.DiGraph()
        self.load()
    def load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
                self.graph = nx.node_link_graph(data)
    def save(self):
        data = nx.node_link_data(self.graph)
        with open(self.path, "w") as f:
            json.dump(data, f)
    def add_fact(self, subject: str, predicate: str, obj: str):
        self.graph.add_edge(subject, obj, label=predicate)
        self.save()
    def query(self, subject: str, predicate: str = None):
        if predicate:
            return [v for u,v,d in self.graph.out_edges(subject, data=True) if d.get('label') == predicate]
        return list(self.graph.successors(subject))
