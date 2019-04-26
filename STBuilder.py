import nAryTree

def standardize(node):
    for child in node.children:
        standardize(child)

    if node.data == "let" and node.children[0].data == "=":
        child_0 = node.children[0]
        child_1 = node.children[1]

        node.children[1] = child_0.children[1]
        node.children[0].children[1] = child_1
        node.children[0].data = "lambda"
        node.data = "gamma"

    elif node.data == "where" and node.children[1].data == "=":
        child_0 = node.children[0] #p
        child_1 = node.children[1] #=

        node.children[0] = child_1.children[1]
        node.children[1].children[1] = child_0
        node.children[1].data = "lambda"
        node.children[0], node.children[1] = node.children[1], node.children[0]
        node.data = "gamma"

    elif node.data == "function_form":
        expression = node.children.pop()

        currentNode = node
        for i in range(len(node.children) - 1):
            lambdaNode = nAryTree.Node("lambda")
            child = node.children.pop(1)
            lambdaNode.addChild(child)
            currentNode.addChild(lambdaNode)
            currentNode = lambdaNode

        currentNode.addChild(expression)

        node.data = "="

    elif node.data == "gamma" and len(node.children) > 2:
        expression = node.children.pop()

        currentNode = node
        for i in range(len(node.children) - 1):
            lambdaNode = nAryTree.Node("lambda")
            child = node.children.pop(1)
            lambdaNode.addChild(child)
            currentNode.addChild(lambdaNode)
            currentNode = lambdaNode

        currentNode.addChild(expression)

    elif node.data == "within" and node.children[0].data == node.children[1].data == "=":
        child_0 = node.children[1].children[0]
        child_1 = nAryTree.Node("gamma")

        child_1.addChild(nAryTree.Node("lambda"))
        child_1.addChild(node.children[0].children[1])
        child_1.children[0].addChild(node.children[0].children[0])
        child_1.children[0].addChild(node.children[1].children[1])

        node.children[0] = child_0
        node.children[1] = child_1

        node.data = "="

    elif node.data == "@":
        expression = node.children.pop(0)
        identifier = node.children[0]

        gammaNode = nAryTree.Node("gamma")
        gammaNode.addChild(identifier)
        gammaNode.addChild(expression)

        node.children[0] = gammaNode

        node.data = "gamma"

    elif node.data == "and":
        child_0 = nAryTree.Node(",")
        child_1 = nAryTree.Node("tau")

        for child in node.children:
            child_0.addChild(child.children[0])
            child_1.addChild(child.children[1])

        node.children.clear()

        node.addChild(child_0)
        node.addChild(child_1)

        node.data = "="

    elif node.data == "rec":
        temp = node.children.pop()
        temp.data = "lambda"

        gammaNode = nAryTree.Node("gamma")
        gammaNode.addChild(nAryTree.Node("Y*"))
        gammaNode.addChild(temp)

        node.addChild(temp.children[0])
        node.addChild(gammaNode)

        node.data = "="

    return node


