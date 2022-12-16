'''
Environment info

pip install sympy
pip install antlr4-python3-runtime==4.10
'''
#from latex2sympy2 import latex2sympy
from sympy.parsing.latex import parse_latex
import numpy as np
import os
import sympy as sp

#Read scraped operations file
os.chdir('C:/Users/cwill/Experiments/2022_WebScrapingPriors')
#eq = r"\sqrt{\frac{K+(4/3)\mu}{\rho}}"
with open("operationsNamed_Materials_science.txt",'r') as f:
    scrapedWiki = f.readlines()

def checkExceptions(currentLine):
    #TODO: the (currentLine.count('=') > 0) may be too limiting (check equations skipped - code at bottom)
    if (currentLine[0] != '#') & (currentLine != '\n') & (currentLine.count('=') > 0) & (currentLine.count('=') < 2) & ('bmatrix' not in currentLine):
            searchExceptions = 1
            while searchExceptions:
                if '&=&' in currentLine:
                    currentLine = currentLine.split('&=&')[-1]
                elif '&=' in currentLine:
                    currentLine = currentLine.split('&=')[-1]
                elif ',&' in currentLine:
                    currentLine = currentLine.split(',&')[0]
                elif ':=' in currentLine:
                    currentLine = currentLine.split(':=')[-1]
                elif '=:' in currentLine:
                    currentLine = currentLine.split('=:')[-1]
                elif '\sum _{i=1}^{n}' in currentLine:
                    currentLine = currentLine.replace('\sum _{i=1}^{n}','\sum')
                elif '=' in currentLine:
                    currentLine = currentLine.split('=')[-1]
                elif '\leq' in currentLine:
                    currentLine = currentLine.split('\leq')[0]
                elif ('\le' in currentLine) & ('\left' not in currentLine):
                    currentLine = currentLine.split('\le')[0]
                elif '\heq' in currentLine:
                    currentLine = currentLine.split('\heq')[0]
                elif '\he' in currentLine:
                    currentLine = currentLine.split('\he')[0]
                elif '>' in currentLine:
                    currentLine = currentLine.split('>')[-1]
                elif '<' in currentLine:
                    currentLine = currentLine.split('<')[-1]    
                elif ('\in' in currentLine) & ('\infty' not in currentLine):
                    currentLine = currentLine.split('\in')[0]
                elif ('\\equiv' in currentLine) | ('\\approx' in currentLine): #TODO: Removes equivalencies and approximations but should it?
                    skipEquation = 1
                    searchExceptions = 0
                elif '\\' == currentLine[-1:]:
                    currentLine = currentLine[:-1]
                else:
                    currentEquation = currentLine
                    searchExceptions = 0
            if 'currentEquation' in locals():
                currentEquation = currentEquation.replace('\,','\times') #TODO: This might be a problem and only solve one equation while messing others
                currentEquation = currentEquation.replace('\|','') #TODO: This might be a problem as it's removing norm operator
                currentEquation = currentEquation.replace(';','') 
                currentEquation = currentEquation.replace(',','')
                currentEquation = currentEquation.replace('.','')
                currentEquation = currentEquation.replace('\'','')
                currentEquation = currentEquation.replace('%','')
                currentEquation = currentEquation.replace('~','')
                currentEquation = currentEquation.replace(' ','')
                currentEquation = currentEquation.replace('\\,','')
                currentEquation = currentEquation.replace('\\bigl(}','')
                currentEquation = currentEquation.replace('{\\bigr)','')
                currentEquation = currentEquation.replace('\\!','')
                currentEquation = currentEquation.replace('\\\\','\\')
                
    if ('currentEquation' in locals()) & ('skipEquation' not in locals()):
        return currentEquation
    else:
        return []
        
#Create list of all equations from file 
mathFormats = ['\mathnormal {', '\mathrm {', '\mathbf {', '\mathsf {', '\mathtt {','\mathfrak {','\mathcal {','\mathbb {','\mathscr {']

scrapedEquations = []
for currentLine in scrapedWiki:
    if '{\displaystyle' in currentLine:
        currentLine = currentLine.replace('{\displaystyle','')#[:-1]
        
    for mathFormat in mathFormats:
        if mathFormat in currentLine:
            tempLine = currentLine.split(mathFormat)
            formattedLine = tempLine[0]
            for i in range(1,len(tempLine)):
                formattedLine = formattedLine + tempLine[i][:tempLine[i].find('}')]+ tempLine[i][(tempLine[i].find('}')+1):]
            #currentLine = tempLine[0] + tempLine[1][:tempLine[1].find('}')] + tempLine[1][(tempLine[1].find('}')+1):] 
            currentLine = formattedLine
        
    if  ('{\\begin{array}{c}' in currentLine):
        currentLine = currentLine.split('{\\begin{array}{c}')
        for arrayEquation in currentLine:
            if '\\\\' in arrayEquation:
                arrayEquation = arrayEquation.split('\\\\')
                for subEquation in arrayEquation:
                    if subEquation:
                        currentEquation = checkExceptions(subEquation)
                        if currentEquation:
                            scrapedEquations.append(currentEquation)
            else:
                currentEquation = checkExceptions(arrayEquation)
                if currentEquation:
                    scrapedEquations.append(currentEquation.strip())
    
    elif '\\\\' in currentLine:
        currentLine = currentLine.split('\\\\')
        for subEquation in currentLine:
            if subEquation:
                currentEquation = checkExceptions(subEquation)
                if currentEquation:
                    scrapedEquations.append(currentEquation)
    else:
        currentEquation = checkExceptions(currentLine)
        if currentEquation:
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
        if skip > 10:
            print(eq)
            break
        else:
            skip += 1
            pass
        
#for pEq in parsedEquations:
#    print(pEq)



#nonEqs = []
#for currentLine in scrapedWiki:
#    if currentLine.count('=') == 0:
#        nonEqs.append(currentLine)
#        
#for i, nonEq in enumerate(nonEqs):
#    print(nonEq)
#    print('********')
#    if i == 1000:
#        print('made it')
#        break