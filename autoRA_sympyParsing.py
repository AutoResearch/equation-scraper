

#from latex2sympy2 import latex2sympy
from sympy.parsing.latex import parse_latex
import numpy as np
import os
import sympy as sp

#Read scraped operations file
os.chdir('C:/Users/cwill/Experiments/2022_WebScrapingPriors')
#eq = r"\sqrt{\frac{K+(4/3)\mu}{\rho}}"
with open("operationsNamed.txt",'r') as f:
    scrapedWiki = f.readlines()

for currentLine in scrapedWiki:
    if '#LINK' in currentLine:
        print(currentLine)
        
def checkExceptions(currentLine):
    currentEquation = []
    if (currentLine[0] != '#') & (currentLine != '\n'):
            searchExceptions = 1
            while searchExceptions:
                currentLine = currentEquation
                if '&=&' in currentLine:
                    currentEquation = currentLine.split('&=&')[1]
                elif '&=' in currentLine:
                    currentEquation = currentLine.split('&=')[1]
                elif '\leq' in currentLine:
                    currentEquation = currentLine.split('\leq')[1]
                elif '\heq' in currentLine:
                    currentEquation = currentLine.split('\heq')[1]
                elif '>' in currentLine:
                    currentEquation = currentLine.split('>')[1]
                elif '<' in currentLine:
                    currentEquation = currentLine.split('<')[1]    
                elif ('\in' in currentLine) & ('infty' not in currentLine):
                    currentEquation = currentLine.split('\in')[0]
                else:
                    currentEquation = currentLine
                    searchExceptions = 0
            currentEquation = currentEquation.replace(';','')   
    return currentEquation
        
#Create list of all equations from file 
scrapedEquations = []
for currentLine in scrapedWiki:
    if '{\displaystyle' in currentLine:
        currentLine = currentLine.replace('{\displaystyle','')#[:-1]
    if '\\\\' in currentLine:
        currentLine = currentLine.split('\\\\')
        for subEquation in currentLine:
            if subEquation:
                if (subEquation[0] != '#') & (currentLine != '\n'):
                    if '&=' in subEquation:
                        currentEquation = subEquation.split('&=')[1]
                    if '\leq' in subEquation:
                        currentEquation = subEquation.split('\leq')[1]
                    if '\heq' in subEquation:
                        currentEquation = subEquation.split('\heq')[1]
                else:
                    currentEquation = subEquation
                scrapedEquations.append(currentEquation)
            
    else:
    currentEquation = checkExceptions(currentLine)
    scrapedEquations.append(currentEquation.strip())

skip = 0
parsedEquations = []
rejectedEquations = []
parsedEq = 0
unparsedEq = 0
for x, eq in enumerate(scrapedEquations):
    if x % 100 == 0:
        print('Completed: ' + str(round((x/len(scrapedEquations))*100,2))+ '% ... Parsed: ' + str(parsedEq) + ' ... Unparsed: '+ str(unparsedEq))
    #Create tree of computation graph
    try:
        tempEq = parse_latex(eq)
        eqSymbols = list(tempEq.free_symbols)
        eqOperations = str(sp.count_ops(tempEq,visual=True)).split('+')
        operations = []
        for eqOp in eqOperations:
            if '*' in eqOp:
                operations.append([eqOp.split('*')[1].strip(),eqOp.split('*')[0].strip()])
            else:
                operations.append([eqOp.strip(), 1])
            
        parsedEquations.append(['EQUATION: ', tempEq, ', SYMBOLS: ', eqSymbols, ', OPERATIONS: ', dict(operations)])
        parsedEq += 1
    except:
        #print('FAILURE - Likely not convertible from latex to sympy')
        unparsedEq += 1
        if skip > -1:
            print(eq)
            break
        else:
            skip += 1
            pass


for eq in scrapedEquations:
    print('***********')
    print(eq)
    if eq =='\sum _{n=0}^{':
        break



#for pEq in parsedEquations:
#    print(pEq)
    
        '''
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
        symbols = []
        numbers = []
        operations = []
        for element in sympyTree:
            if 'sympy.core.symbol' in str(type(element)):
                symbols.append(str(element))
            elif 'sympy.core.numbers' in str(type(element)):
                numbers.append(element)
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
                elif (opType == 'Mul') & (element.args[0] == -1):
                    opType = 'Sub'
                else:
                    pass
                
                if setOperation:
                    opCount = len(element.args)-1
                    operations.append([opType,opCount])
        
        if (len(operations) > 0) & (len(symbols) > 0):
            #Determine all symbols and their frequency
            uniqueSyms = set(symbols)
            symbolDict = {}
            for sym in uniqueSyms:
                symbolDict[sym] = symbols.count(sym)

            #Determine all operations and their frequency
            operations = np.array(operations)
            uniqueOps = np.unique(operations[:,0])
            operationDict = {}
            for op in uniqueOps:
                operationDict[op] = np.sum(operations[operations[:,0]==op,1].astype(int))
            
            parsedEquations.append(['EQUATION: ', eq, parse_latex(eq), ', SYMBOLS: ', symbolDict, ', OPERATIONS: ', operationDict])
            
        parsedEq +=1
    except:
        rejectedEquations.append(eq)
        unparsedEq +=1
        continue

for pEq in parsedEquations:
    print(pEq)
    
for rEq in rejectedEquations:
    print(rEq)
    
#print(len(parsedEquations))


scrapedEquations[0]
tempEq = r"S_{i}-S_{j}=x_{{ij}}{\sqrt  {\sigma _{i}^{2}+\sigma _{j}^{2}-2r_{{ij}}\sigma _{i}\sigma _{j}}}"
tempEQ = r"{  \mathrm {logodds} (A {\text{beats}} Bmid v_{a},v_{b})=v_{a}-v_{b}}"

eq= r"{\\sqrt  {{\\frac  {K+(4/3)\\mu }{\\rho }}}}\\\\v_{s}".split('\\\\\\\\')[0].replace('\\\\','\\')
parse_latex(scrapedEquations[0])
#latex2sympy(eq)
'''