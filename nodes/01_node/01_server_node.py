import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from nodes.node import Node
from cluster_config import NODES, MASTER_URL

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "storage")

node = Node(
    node_id=1,
    port=5001,
    storage_path=STORAGE_PATH,
    nodes=NODES,
    master_url=MASTER_URL
)

if __name__ == "__main__":
    node.run()
