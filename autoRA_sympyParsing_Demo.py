
from sympy.parsing.latex import parse_latex
import numpy as np
import os
import sympy as sp

#### SET EQUATION 
#https://en.wikipedia.org/wiki/Adams%E2%80%93Williamson_equation
eq = r"\sqrt{\frac{K+(4/3)\mu}{\rho}}"
#eq = r"-V\frac{dP}{dV}"

def parseEquation(eq):
    tempEq = parse_latex(eq)
    sympyTree = [tempEq]
    x=0
    while x < len(sympyTree):
        try:
            tempEq = sympyTree[x]
            for i in range(len(tempEq.args)):
                sympyTree.append(tempEq.args[i])
            x += 1
        except:
            break

    #Extract Numbers, Symbols, and Operations from equation
    symbols = list(parse_latex(eq).free_symbols)
    operations = []
    for element in sympyTree:
        if 'sympy.core.symbol' in str(type(element)):
            pass
        elif 'sympy.core.numbers' in str(type(element)):
            pass
        elif 'sympy.core.containers' in str(type(element)):
            pass
        else:
            setOperation = 1
            opType = str(type(element)).split('.')[-1][:-2]
            if (opType == 'Pow') & (element.args[1] == 1/2):
                opType = 'Sqrt'
            elif (opType == 'Pow') & (element.args[1] == -1):
                opType = 'Div'
            elif (opType == 'Mul') & ('Pow' in str(type(element.args[1]))): #If the multiplication is actually talking about a division down the line...
                if (element.args[1].args[1] == -1):
                    setOperation = 0 #Skip it, it will be handled down the tree
            elif (opType == 'Mul') & ('sympy.core.numbers' in str(type(element.args[1]))):
                if (element.args[1] < 1): 
                    opType = 'Div'
            elif (opType == 'Add') & ('-' in str(element.args[1])):
                setOperation = 0 #Skip it, it will be handled down the tree
            elif (opType == 'Mul') & (-1 in element.args):
                operations.append(['Sub',element.args.count(-1)])
                if element.args.count(-1) < len(element.args):
                    operations.append(['Mul',((len(element.args)-1)-(element.args.count(-1)))])
                setOperation = 0
            else:
                pass
            
            if setOperation:
                opCount = len(element.args)-1
                operations.append([opType,opCount])
    
    #Determine all operations and their frequency
    operations = np.array(operations)
    uniqueOps = np.unique(operations[:,0])
    operationDict = {}
    for op in uniqueOps:
        operationDict[op] = np.sum(operations[operations[:,0]==op,1].astype(int))
            
    return (symbols, operationDict)

#### SYMPY PARSING
tempEq = parse_latex(eq)
eqSymbols = list(tempEq.free_symbols)
eqOperations = str(sp.count_ops(tempEq,visual=True)).split('+')
operations = []
for eqOp in eqOperations:
    if '*' in eqOp:
        operations.append([eqOp.split('*')[1].strip(),eqOp.split('*')[0].strip()])
    else:
        operations.append([eqOp.strip(), 1])

print('\nSYMPY PARSING\n')
print('EQUATION:')
print(tempEq)
print('SYMBOLS:')
print(eqSymbols)
print('OPERATIONS:')
print(operations)
print('*----------------*')


#### MANUAL PARSING
symbolDict, operationDict = parseEquation(eq)
print('\nMANUAL PARSING\n')
print('EQUATION:')
print(tempEq)
print('SYMBOLS:')
print(symbolDict)
print('OPERATIONS:')
print(operationDict)
print('*----------------*')

#BMS PARSING:
if eq == r"\sqrt{\frac{K+(4/3)\mu}{\rho}}":
    print('\nBMS PARSING\n')
    print('EQUATION:')
    print(tempEq)
    print('SYMBOLS:')
    print("{'mu': 1, 'K': 1, 'rho': 1, 'v_s': 1}")
    print('OPERATIONS:')
    print("{'Mul': 2, 'Div': 1, 'Add': 1, 'sqrt': 1}")
    print('*----------------*')
else:
    print('\nBMS PARSING\n')
    print('EQUATION:')
    print(tempEq)
    print('SYMBOLS:')
    print("{'P': 1}")
    print('OPERATIONS:')
    print("{'Neg': 1}")
    print('*----------------*')