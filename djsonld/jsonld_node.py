

def node_value(node):
    if isinstance(node, dict) and "@value" in node:
        return node['@value']
    else:
        return node


def node_type(node):
    if isinstance(node, dict) and "@type" in node:
        return node['@type']


def node_id(node):
    if isinstance(node, dict) and "@id" in node:
        return node['@id']
