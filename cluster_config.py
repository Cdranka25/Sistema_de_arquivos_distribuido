MASTER_URL = "http://localhost:5000"

NODES = {
    1: "http://localhost:5001",
    2: "http://localhost:5002",
    3: "http://localhost:5003"
}

REPLICATION_FACTOR = 2


def get_node_list():
    return list(NODES.values())


def get_node_url(node_id):
    return NODES[node_id]


def get_node_port(node_id):
    return int(NODES[node_id].split(":")[-1])