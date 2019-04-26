import ASTBuilder
import STBuilder
import nAryTree
import sys

def generateControlStructure(root, i):
    global controlStructures
    global count
    while(len(controlStructures) <= i):
        controlStructures.append([])

    if (root.data == "lambda"):
        count += 1
        leftChild = root.children[0]
        if(leftChild.data == ","):
            temp = "lambda" + "_" + str(count) + "_"
            for child in leftChild.children:
                temp += child.data[4:-1] + ","
            temp = temp[:-1]
            controlStructures[i].append(temp)
        else:
            temp = "lambda" + "_" + str(count) + "_" + leftChild.data[4:-1]
            controlStructures[i].append(temp)

        for child in root.children[1:]:
            generateControlStructure(child, count)

    elif (root.data == "->"):
        count += 1
        temp = "delta" + "_" + str(count)
        controlStructures[i].append(temp)
        generateControlStructure(root.children[1], count)
        count += 1
        temp = "delta" + "_" + str(count)
        controlStructures[i].append(temp)
        generateControlStructure(root.children[2], count)
        controlStructures[i].append("beta")
        generateControlStructure(root.children[0], i)

    elif(root.data == "tau"):
        n = len(root.children)
        temp = "tau" + "_" + str(n)
        controlStructures[i].append(temp)
        for child in root.children:
            generateControlStructure(child, i)

    else:
        controlStructures[i].append(root.data)
        for child in root.children:
            generateControlStructure(child, i)


class EnvironmentNode(object):
    def __init__(self, number, parent):
        self.name = "e_" + str(number)
        self.variables = {}
        self.children = []
        self.parent = parent
    def addChild(self, node):
        self.children.append(node)
        node.variables.update(self.variables)
    def addVariable(self, key, value):
        self.variables[key] = value


def lookup(name):
    global environments
    global builtInFunctions
    global stack
    if(name.startswith("INT", 1)):
        return int(name[5:-1])
    elif(name.startswith("STR", 1)):
        return name[5:-1].strip("'")
    elif(name.startswith("ID", 1)):
        variable = name[4:-1]
        if (variable in builtInFunctions):
            return variable
        else:
            value = environments[currentEnvironment].variables[variable]
            return value
    elif(name.startswith("Y*", 1)):
        return "Y*"
    elif(name.startswith("nil", 1)):
        return ()
    elif(name.startswith("true", 1)):
        return True
    elif(name.startswith("false", 1)):
        return False

def applyRules():
    binop = ["+", "-", "*", "/", "**", "gr", "ge","ls", "le", "eq", "ne", "or", "&", "aug"]
    unop = ["neg","not"]

    global control
    global stack
    global environments
    global currentEnvironment

    while(len(control) > 0):  ##while


        #print("CONTROL", control)
        #print("STACK",stack)
        #print("ENVIRONMENT ",currentEnvironment," ", environments[currentEnvironment].variables)
        #print("")
        symbol = control.pop()

        #Rule 1
        if(symbol.startswith("<") and symbol.endswith(">")):
            stack.append(lookup(symbol))

        #Rule 2
        elif(symbol.startswith("lambda")):
            stack.append(symbol+"_"+str(currentEnvironment))

        #Rule 4
        elif(symbol == "gamma"):
            stackSymbol_1 = stack.pop()
            stackSymbol_2 = stack.pop()

            if(type(stackSymbol_1) == str and stackSymbol_1.startswith("lambda")):
                currentEnvironment = len(environments)
                lambdaData = stackSymbol_1.split("_")

                parent = environments[int(lambdaData[3])]
                child = EnvironmentNode(currentEnvironment, parent)
                parent.addChild(child)
                environments.append(child)

                #Rule 11
                variablesList = lambdaData[2].split(",")
                if(len(variablesList)>1):
                    for i in range(len(variablesList)):
                        child.addVariable(variablesList[i],stackSymbol_2[i])
                else:
                    child.addVariable(lambdaData[2],stackSymbol_2)

                stack.append(child.name)
                control.append(child.name)
                control += controlStructures[int(lambdaData[1])]

            #Rule 10
            elif(type(stackSymbol_1) == tuple):
                stack.append(stackSymbol_1[stackSymbol_2-1])

            #Rule 12
            elif(stackSymbol_1 == "Y*"):
                temp = "eta" + stackSymbol_2[6:]
                stack.append(temp)

            #Rule 13
            elif(type(stackSymbol_1) == str and stackSymbol_1.startswith("eta")):
                temp = "lambda" + stackSymbol_1[3:]
                control.append("gamma")
                control.append("gamma")
                stack.append(stackSymbol_2)
                stack.append(stackSymbol_1)
                stack.append(temp)

            #built in
            elif(stackSymbol_1 == "Order"):
                order = len(stackSymbol_2)
                stack.append(order)

            elif(stackSymbol_1 == "Print" or stackSymbol_1 == "print"):
                #print(stackSymbol_2)
                stack.append(stackSymbol_2)

            elif(stackSymbol_1 == "Conc"):
                stackSymbol_3 = stack.pop()
                control.pop()
                temp = stackSymbol_2 + stackSymbol_3
                stack.append(temp)

            elif(stackSymbol_1 == "Stern"):
                stack.append(stackSymbol_2[1:])

            elif(stackSymbol_1 == "Stem"):
                stack.append(stackSymbol_2[0])

            elif(stackSymbol_1 == "Isinteger"):
                if(type(stackSymbol_2) == int):
                    stack.append(True)
                else:
                    stack.append(False)
                
            elif(stackSymbol_1 == "Istruthvalue"):
                if(type(stackSymbol_2) == bool):
                    stack.append(True)
                else:
                    stack.append(False)

            elif(stackSymbol_1 == "Isstring"):
                if(type(stackSymbol_2) == str):
                    stack.append(True)
                else:
                    stack.append(False)

            elif(stackSymbol_1 == "Istuple"):
                if(type(stackSymbol_2) == tuple):
                    stack.append(True)
                else:
                    stack.append(False)

            elif(stackSymbol_1 == "Isfunction"):
                if(stackSymbol_2 in builtInFunctions):
                    return True
                else:
                    False

        #Rule 5
        elif(symbol.startswith("e_")):
            stackSymbol = stack.pop()
            stack.pop()
            if(currentEnvironment != 0):
                for element in reversed(stack):
                    if(type(element) == str and element.startswith("e_")):
                        currentEnvironment = int(element[2:])
                        break
            stack.append(stackSymbol)

        #Rule 6
        elif(symbol in binop):
            rand_1 = stack.pop()
            rand_2 = stack.pop()
            if(symbol == "+"):
                stack.append(rand_1+rand_2)
            elif(symbol == "-"):
                stack.append(rand_1-rand_2)
            elif(symbol == "*"):
                stack.append(rand_1*rand_2)
            elif(symbol == "/"):
                stack.append(rand_1/rand_2)
            elif(symbol == "**"):
                stack.append(rand_1**rand_2)
            elif(symbol == "gr"):
                stack.append(rand_1 > rand_2)
            elif(symbol == "ge"):
                stack.append(rand_1 >= rand_2)
            elif(symbol == "ls"):
                stack.append(rand_1 < rand_2)
            elif(symbol == "le"):
                stack.append(rand_1 <= rand_2)
            elif(symbol == "eq"):
                stack.append(rand_1 == rand_2)
            elif(symbol == "ne"):
                stack.append(rand_1 != rand_2)
            elif(symbol == "or"):
                stack.append(rand_1 or rand_2)
            elif(symbol == "&"):
                stack.append(rand_1 and rand_2)
            elif(symbol == "aug"):
                if(type(rand_2) == tuple):
                    stack.append(rand_1 + rand_2)
                else:
                    stack.append(rand_1+(rand_2,))

        #Rule 7
        elif(symbol in unop):
            rand = stack.pop()
            if(symbol == "not"):
                stack.append(not rand)
            elif(symbol == "-"):
                stack.append(-rand)

        #Rule 8
        elif(symbol == "beta"):
            B = stack.pop()
            deltaElse = control.pop()
            deltaThen = control.pop()
            if(B):
                control += controlStructures[int(deltaThen.split('_')[1])]
            else:
                control += controlStructures[int(deltaElse.split('_')[1])]

        #Rule 9
        elif(symbol.startswith("tau_")):
            n = int(symbol.split("_")[1])
            tauList = []
            for i in range(n):
                tauList.append(stack.pop())
            tauTuple = tuple(tauList)
            stack.append(tauTuple)

        elif(symbol == "Y*"):
            stack.append(symbol)


tokens = None

def runProgram(fileName):
    global tokens
    tokens = ASTBuilder.readFile(fileName)

if __name__ == "__main__":
    fileName = sys.argv[1]
    runProgram(fileName)

AST  = ASTBuilder.buildAST(tokens)
ST = STBuilder.standardize(AST)
traversedST = nAryTree.traverse(ST)

for i in traversedST.strip("\n").split("\n"):
    if ("ID" in i and "_" in i):
        print("This interpreter does not allow underscores(_) in ID/Variable names. Please make sure your ID/Variable names do not contain underscores.")
        exit()

controlStructures = []
count = 0

generateControlStructure(ST,0) ############################

builtInFunctions = ["Order", "Print", "print", "Conc", "Stern", "Stem", "Isinteger", "Istruthvalue", "Isstring", "Istuple", "Isfunction"]

control = []
stack = []
environments = [EnvironmentNode(0, None)]
currentEnvironment = 0

control.append(environments[0].name)
control += controlStructures[0]

stack.append(environments[0].name)

applyRules()

print("Output of the above program is:")
print(stack[0])






