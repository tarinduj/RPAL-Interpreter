import nAryTree

def readFile(fileName):
    with open(fileName) as file:
        data = file.read()
    tokens = data.strip("\n").strip().split("\n")
    return tokens

def buildAST(tokens):
    root = nAryTree.Node(tokens[0].strip("."))
    if(len(tokens)>1):
        directChildIndices = getDirectChildren(tokens, getTreeLevel(tokens[0]))
        for i in range(len(directChildIndices) - 1):
            root.addChild(buildAST(tokens[directChildIndices[i]:directChildIndices[i+1]]))
        root.addChild(buildAST(tokens[directChildIndices[-1]:]))
    return root

def getDirectChildren(tokens, rootLevel):
    directChildIndices = []
    for i in range(len(tokens)) :
        if(getTreeLevel(tokens[i]) - rootLevel == 1):
            directChildIndices.append(i)
    return directChildIndices

def getTreeLevel(token):
    count = 0
    for char in token:
        if char == ".":
            count += 1
        else:
            break
    return count

