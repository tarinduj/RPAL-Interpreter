class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []
    def addChild(self, node):
        self.children.append(node)


def traverse(root):
    s = root.data
    for child in root.children:
        s += "\n" + traverse(child)
    return s


