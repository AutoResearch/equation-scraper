###############################################################################
## Written by Chad C. Williams, 2022                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

'''
Environment info

pip install numpy
pip install sympy
pip install antlr4-python3-runtime==4.10

Note:There exists a requirements.txt file
'''

###############################################################################
#0. User Inputs - Determine Which Category Pages to Scrape
###############################################################################

searchedKeywords = ['Psychophysics'] #User defined category pages to scrape

#Determine filename to load
saveKeywords = '_'.join(searchKeywords) #Create string of keywords for file name
loadName = 'operationsNamed_' + saveKeywords + '.txt' #Create file name

###############################################################################
#1. Import Modules
###############################################################################

from sympy.parsing.latex import parse_latex
import numpy as np
import os
import sympy as sp
import re

###############################################################################
#2. Determine Functions
###############################################################################

def processEquation(wikiLine,currentLink,currentLine):
    if '\\\\' in currentLine:
        currentLine = currentLine.split('\\\\') 
        for subEquation in currentLine:
            if subEquation:
                currentEquation = checkExceptions(subEquation)
                scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = appendVariables(wikiLine,currentLink,currentEquation,subEquation)
    else:
        currentEquation = checkExceptions(currentLine)
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = appendVariables(wikiLine,currentLink,currentEquation,currentLine)

    return scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations

def checkExceptions(currentLine):
    if (currentLine[0] != '#') & (currentLine != '\n') & (currentLine.count('=') < 2) & ('bmatrix' not in currentLine):
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
                elif '>=' in currentLine:
                    currentLine = currentLine.split('>=')[-1]
                elif '\geq' in currentLine:
                    currentLine = currentLine.split('\geq')[-1]
                elif '\seq' in currentLine:
                    currentLine = currentLine.split('\seq')[-1]
                elif '<=' in currentLine:
                    currentLine = currentLine.split('<=')[-1]
                elif '<' in currentLine:
                    currentLine = currentLine.split('<')[-1] 
                elif ('\in' in currentLine):
                    currentLine = currentLine.split('\in')[0]   
                elif ('\\equiv' in currentLine) | ('\\approx' in currentLine): #TODO: Removes equivalencies and approximations but should it?
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
                excludedNotations = ['\|',';','\\,',',','.','\'','%','~',' ','\\,','\\bigl(}','{\\bigr)','\\!','\\boldsymbol','\\cdot','\\cdots','aligned','\\ddot','\\dot','\Rightarrow'] #TODO: Are removing the cdots/ddots a problem mathematically?
                
                currentEquation = [currentEquation := currentEquation.replace(excludedNotation,'') for excludedNotation in excludedNotations][-1]
                currentEquation = currentEquation.replace('\\\\','\\')
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
    
def appendVariables(wikiLine,currentLink,currentEquation, currentLine):
    if currentEquation:
        scrapedWikiEquations.append(wikiLine)
        scrapedLinks.append(currentLink)
        scrapedEquations.append(currentEquation)
    else:
        skippedEquations.append(currentLine)
    
    return scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations
    
###############################################################################
#3. Load Data and Setup Variables
###############################################################################

#Read scraped operations file
with open(loadName,'r') as f:
    scrapedWiki = f.readlines()

#Setup Variables
scrapedEquations = []
skippedEquations = []
scrapedLinks = []
scrapedWikiEquations = []
currentLink = []

###############################################################################
#4. Re-Format Latex Equations to Comply with Sympy Translation
###############################################################################

#Create list of all equations from file 
for currentLine in scrapedWiki:
    wikiLine = currentLine
    if '#LINK:' in currentLine:
        currentLink = currentLine
    
    #Removing latex formatting
    if '{\displaystyle' in currentLine:
        currentLine = currentLine.replace('{\displaystyle','')[:-2]
    
    #Removes superscript notations because they are part of a symbol but treated as a power operator
    superBrackets = re.findall(r'\{\(.*?\)\}', currentLine)
    if superBrackets:
        for superBracket in superBrackets:
            if (superBracket.count('(')==1) | (superBracket.count(')')==1) | (superBracket.count('{')==1) | (superBracket.count('}')==1):
                currentLine = currentLine.replace('^'+superBracket,'')
    
    #Reformat subscript notations
    subText = re.findall(r'p\(.*?\|.*?\)', currentLine) 
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'p(x)')
            
    #Reformat conditional probability notations
    subText = re.findall(r'\_\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'_{x}')
        
    #Removing math formatting
    mathFormats = ['\mathnormal {', '\mathrm {', '\mathbf {', '\mathsf {', '\mathtt {','\mathfrak {','\mathcal {','\mathbb {','\mathscr {']
    for mathFormat in mathFormats:
        if mathFormat in currentLine:
            tempLine = currentLine.split(mathFormat)
            formattedLine = tempLine[0]
            for i in range(1,len(tempLine)):
                formattedLine = formattedLine + tempLine[i][:tempLine[i].find('}')]+ tempLine[i][(tempLine[i].find('}')+1):]
            currentLine = formattedLine
    
###############################################################################
#5. Split and Store all Data, Including Assigning Equations to a Variable
###############################################################################

    #Begin loop to adapt equations to be proper latex    
    if  ('{\\begin{array}{c}' in currentLine):
        currentLine = currentLine.split('{\\begin{array}{c}')
        for arrayLine in currentLine:
            scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,arrayLine)
            
    elif ('\\begin{aligned}' in currentLine):
        currentLine = currentLine.split('\end{aligned}}')[0]
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,currentLine)

    else:
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,currentLine)

###############################################################################
#6. Parse Equations
###############################################################################

skip = 0
parsedEquations = []
rejectedEquations = []
parsedEq = 0
unparsedEq = 0
for x, eq in enumerate(scrapedEquations):
    if x % 1 == 0:
        print('\nCurrent Equation:')
        print(eq)
        print('Completed: ' + str(round((x/len(scrapedEquations))*100,2))+ '% ... Parsed: ' + str(parsedEq) + ' ... Unparsed: '+ str(unparsedEq))
    #Create tree of computation graph
    try:
        if not eq.isnumeric(): #Sympy crashes if latex is a numeric number without any operations
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
        
        unparsedEq += 1
        if skip > -1:
            print('FAILURE - Likely not convertible from latex to sympy')
            print(eq)
            break
        else:
            skip += 1
            pass
        
###############################################################################
#6. Save Files
###############################################################################

#Save file of scraped equations
parsedFilename = 'parsed_'+loadName
with open(parsedFilename, 'w') as f:
    for parsedItem in parsedEquations:
        f.write(parsedItem[4]+'~'+str(parsedItem[5])+'~'+parsedItem[2]+'~'+str(parsedItem[3])+'~'+parsedItem[0]+'~'+str(parsedItem[1])+'~'+parsedItem[6]+'~'+str(parsedItem[7][7:-1])+'~'+str(parsedItem[8])+'~'+str(parsedItem[9]))
        
#Save file of skipped equations, if any
skippedFilename = 'skipped_'+loadName
with open(skippedFilename, 'w') as f:
    for skippedItem in skippedEquations:
        if '#' not in skippedItem:
            f.write(skippedItem[0])
            f.write('\n')