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
import re

#Read scraped operations file
os.chdir('C:/Users/cwill/Experiments/2022_WebScrapingPriors')
#eq = r"\sqrt{\frac{K+(4/3)\mu}{\rho}}"
operationsFilename = 'operationsNamed_Materials_science.txt'
with open(operationsFilename,'r') as f:
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
                elif ('\in' in currentLine):
                    currentLine = currentLine.split('\in')[0]   
                #elif ('\in' in currentLine) & ('\infty' not in currentLine):
                #    currentLine = currentLine.split('\in')[0]
                elif ('\\equiv' in currentLine) | ('\\approx' in currentLine): #TODO: Removes equivalencies and approximations but should it?
                    skipEquation = 1
                    searchExceptions = 0
                elif '\\' == currentLine[-1:]:
                    currentLine = currentLine[:-1]
                elif 'operatorname' in currentLine:
                    operatorVar = currentLine.split('\operatorname {')[1].split('}')[0]
                    currentLine = currentLine.replace('\operatorname {'+operatorVar+'}',operatorVar[0])
                else:
                    currentEquation = currentLine
                    searchExceptions = 0
            if 'currentEquation' in locals():
                #currentEquation = currentEquation.replace('\,','\times') #TODO: This might be a problem and only solve one equation while messing others
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
                currentEquation = currentEquation.replace('\\boldsymbol','')
                #currentEquation = currentEquation.replace('\\operatorname','')
                currentEquation = currentEquation.replace('\\cdots','')
                currentEquation = currentEquation.replace('aligned','')
                currentEquation = currentEquation.replace('\\ddot','') #TODO: This might be a problem as it's changing the symbol
                currentEquation = currentEquation.replace('\\dot','') #TODO: This might be a problem as it's changing the symbol
                if '**{' in currentEquation:
                    powerVar = currentEquation.split('**{')[1].split('}')[0]
                    try:
                        int(powerVar)
                    except:
                        currentEquation = currentEquation.replace('**{'+powerVar+'}','')
            
    if ('currentEquation' in locals()) & ('skipEquation' not in locals()):
        return currentEquation
    else:
        return []
        
#Create list of all equations from file 
mathFormats = ['\mathnormal {', '\mathrm {', '\mathbf {', '\mathsf {', '\mathtt {','\mathfrak {','\mathcal {','\mathbb {','\mathscr {']

scrapedEquations = []
scrapedLinks = []
scrapedWikiEquations = []
for currentLine in scrapedWiki:
    wikiLine = currentLine
    if '#LINK:' in currentLine:
        currentLink = currentLine
    
    #Removing latex formatting
    if '{\displaystyle' in currentLine:
        currentLine = currentLine.replace('{\displaystyle','')#[:-1]
    
    #TODO: Is this wrong? Removing derivative superscript notation...
    #Ah this is too general and removes things it shouldn't (so added the if statement to make sure it does this locally)
    #superBrackets = re.findall(r'\{\(.*?\)\}', currentLine)
    #if superBrackets:
    #    for superBracket in superBrackets:
    #        if (superBracket.count('(')==1) | (superBracket.count(')')==1) | (superBracket.count('{')==1) | (superBracket.count('}')==1):
    #            currentLine = currentLine.replace(superBracket,'{'+superBracket[2:-2]+'}')
    
    #ALTERNATIVE TO ABOVE: HERE, THESE ARE REMOVED BECAUSE THE ABOVE METHOD TURNS THEM TO POWER FUNCTIONS
    superBrackets = re.findall(r'\{\(.*?\)\}', currentLine)
    if superBrackets:
        for superBracket in superBrackets:
            if (superBracket.count('(')==1) | (superBracket.count(')')==1) | (superBracket.count('{')==1) | (superBracket.count('}')==1):
                currentLine = currentLine.replace('^'+superBracket,'')
    
    #Reformat subscript notations
    subText = re.findall(r'\_\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine.replace(sub,'_{x}')
        
    #Removing math formatting
    for mathFormat in mathFormats:
        if mathFormat in currentLine:
            tempLine = currentLine.split(mathFormat)
            formattedLine = tempLine[0]
            for i in range(1,len(tempLine)):
                formattedLine = formattedLine + tempLine[i][:tempLine[i].find('}')]+ tempLine[i][(tempLine[i].find('}')+1):]
            #currentLine = tempLine[0] + tempLine[1][:tempLine[1].find('}')] + tempLine[1][(tempLine[1].find('}')+1):] 
            currentLine = formattedLine
            
    #Begin loop to adapt equations to be proper latex
    if  ('{\\begin{array}{c}' in currentLine):
        currentLine = currentLine.split('{\\begin{array}{c}')
        for arrayEquation in currentLine:
            if '\\\\' in arrayEquation:
                arrayEquation = arrayEquation.split('\\\\')
                for subEquation in arrayEquation:
                    if subEquation:
                        currentEquation = checkExceptions(subEquation)
                        if currentEquation:
                            scrapedWikiEquations.append(wikiLine)
                            scrapedLinks.append(currentLink)
                            scrapedEquations.append(currentEquation)
            else:
                currentEquation = checkExceptions(arrayEquation)
                if currentEquation:
                    scrapedWikiEquations.append(wikiLine)
                    scrapedLinks.append(currentLink)
                    scrapedEquations.append(currentEquation.strip())
    
    elif '\\\\' in currentLine:
        currentLine = currentLine.split('\\\\')
        for subEquation in currentLine:
            if subEquation:
                currentEquation = checkExceptions(subEquation)
                if currentEquation:
                    scrapedWikiEquations.append(wikiLine)
                    scrapedLinks.append(currentLink)
                    scrapedEquations.append(currentEquation)
    else:
        currentEquation = checkExceptions(currentLine)
        if currentEquation:
            scrapedWikiEquations.append(wikiLine)
            scrapedLinks.append(currentLink)
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
        
        if eqOperations != ['0']:
            parsedEquations.append(['EQUATION:', tempEq, 'SYMBOLS:', eqSymbols, 'OPERATIONS:', dict(operations), 'LINK:', scrapedLinks[x],'WIKIEQUATION:',scrapedWikiEquations[x]])
        parsedEq += 1
    except:
        #print('FAILURE - Likely not convertible from latex to sympy')
        unparsedEq += 1
        if skip > 1000:
            print(eq)
            break
        else:
            skip += 1
            pass
    
        
parsedFilename = 'parsed_'+operationsFilename
with open(parsedFilename, 'w') as f:
    for parsedItem in parsedEquations:
        f.write(parsedItem[4]+'~'+str(parsedItem[5])+'~'+parsedItem[2]+'~'+str(parsedItem[3])+'~'+parsedItem[0]+'~'+str(parsedItem[1])+'~'+parsedItem[6]+'~'+str(parsedItem[7][7:])+'~'+str(parsedItem[8])+'~'+str(parsedItem[9]))
        #f.write('\n')
#                
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