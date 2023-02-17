####
##User input
####
equation = r"{\displaystyle dx=Adt+cdW\ ,\ x(0)=0}"

####
#Load Modules
####
from sympy.parsing.latex import parse_latex
import sympy as sp
import re
import string

####
#Load Functions 
####
#The main function that organizes the current equation and it's metadata then feeds these to the processing functions
def processEquation(wikiLine,currentLink,currentLine):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    if '\\\\' in currentLine: #\\\\ is used to split multiple equations that are stored in one string
        currentLine = currentLine.split('\\\\') #The equations are split if multiple exist
        for subEquation in currentLine: #Cycle through each equation
            if subEquation: #Ensure the sub-equation exists 
                currentEquation = formatEquation(subEquation) #Calls the format equation function 
                scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = appendVariables(wikiLine,currentLink,currentEquation,subEquation) #Calls the append variables function
    elif ',\\' in currentLine: #,\\ is used to split multiple equations that are stored in one string
        currentLine = currentLine.split(',\\') #The equations are split if multiple exist
        for subEquation in currentLine: #Cycle through each equation
            if subEquation: #Ensure the sub-equation exists 
                currentEquation = formatEquation(subEquation) #Calls the format equation function 
                scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = appendVariables(wikiLine,currentLink,currentEquation,subEquation) #Calls the append variables function        
    else: #There only exists one equation
        currentEquation = formatEquation(currentLine) #Calls the format equation function 
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = appendVariables(wikiLine,currentLink,currentEquation,currentLine) #Calls the append variables function

    return scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations

def formatEquation(currentLine):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    if (currentLine[0] != '#') & (currentLine != '\n') & (currentLine.count('=') < 2) & ('bmatrix' not in currentLine):
            
            #Split equations to remove the left hand side
            separators = {'&=&': -1,'&=': -1,',&': 0, ':=': -1, '=:': -1,'=': -1, '\leq': 0, '\heq': 0, '\he': 0, '>': -1, '>=': -1, '\geq': -1, '\seq': -1, '<=': -1, '<': -1, '\in': 0}
            if ('\\equiv' not in currentLine) | ('\\approx' not in currentLine): #TODO: Removes equivalencies and approximations but should it?
                currentEquation = [currentLine := currentLine.split(separator)[separators[separator]] if separator in currentLine else currentLine for separator in separators.keys()][-1] #TODO: I think this new method removed two equations, figure out if so and why
              
            #Removes specific notations that Sympy cannot comprehend 
            excludedNotations = ['\|',';','\\,',',','.','\'','%','~',' ','\\,','\\bigl(}','{\\bigr)','\\!','\\boldsymbol','\\cdot','\\cdots','aligned','\\ddot','\\dot','\Rightarrow'] #TODO: Are removing the cdots/ddots a problem mathematically?
            if 'currentEquation' in locals():             
                currentEquation = [currentEquation := currentEquation.replace(excludedNotation,'') for excludedNotation in excludedNotations][-1]
                
                #Additional Special Exclusions
                
                currentEquation = currentEquation.replace('\\\\','\\') #In some cases, these do not indicate multiple equations (as above)
                
                #If these are superscripts, and not exponents, it will be interpreted as a power operation. So, remove it if it is a superscript
                if '**{' in currentEquation: #Check if the power function exists
                    powerVar = currentEquation.split('**{')[1].split('}')[0] #Determine what is contained within the power function
                    try:
                        int(powerVar) #Determine whether it is a number, and if not it is a superscript
                    except:
                        currentEquation = currentEquation.replace('**{'+powerVar+'}','') #Remove it if it is a superscript
                
                #Here, \le refers to <= and so we must split the equation. However, if conflicts with \left notation and so we only remove it if it is not this
                if ('\le' in currentEquation) & ('\left' not in currentEquation):
                    currentEquation = currentEquation.split('\le')[0]
                            
                #The descriptive sum conflicts, and so we convert it to a simple sum
                if '\sum _{i=1}^{n}' in currentEquation:
                    currentEquation = currentEquation.replace('\sum _{i=1}^{n}','\sum')
                    
                #Remove backslashes at the end of the equations
                if '\\' == currentEquation[-1:]:
                    currentEquation = currentEquation[:-1]
                    
                #Remove the operatorname tag
                if 'operatorname' in currentEquation:
                    try:
                        operatorVar = currentEquation.split('\operatorname {')[1].split('}')[0]
                        currentEquation = currentEquation.replace('\operatorname {'+operatorVar+'}',operatorVar[0])
                    except:
                        currentEquation = currentEquation.replace('\operatorname {','')[:-1]
    
    #If an equation was found and reformatted, return it
    if ('currentEquation' in locals()):
        return currentEquation
    else:
        return []
    
def appendVariables(wikiLine,currentLink,currentEquation, currentLine):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    if currentEquation:
        scrapedWikiEquations.append(wikiLine) #Track raw equations as scraped from wikipedia
        scrapedLinks.append(currentLink) #Track the URL of the equation
        scrapedEquations.append(currentEquation) #Track reformatted equations used in parsing
    else:
        skippedEquations.append(currentLine) #Track if an equation did not make it through reformatting
    
    return scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations
    

####
## Reformat currentLine
####
currentLine = equation

#Removing latex formatting
if '{\\displaystyle' in currentLine:
    currentLine = currentLine.replace('{\\displaystyle','')[:-1]

#Removes superscript notations because they are part of a symbol but treated as a power operator
superBrackets = re.findall(r'\{\(.*?\)\}', currentLine)
if superBrackets:
    for superBracket in superBrackets:
        if (superBracket.count('(')==1) | (superBracket.count(')')==1) | (superBracket.count('{')==1) | (superBracket.count('}')==1):
            currentLine = currentLine.replace('^'+superBracket,'')

#Reformat conditional probability notations
subText = re.findall(r'p\(.*?\|.*?\)', currentLine) 
if subText:
    for sub in subText:
        currentLine = currentLine.replace(sub,'p(x)')
        
#Reformat subscript notations
subText = re.findall(r'\_\{.*?\}', currentLine)
if subText:
    for sub in subText:
        currentLine = currentLine.replace(sub,'_{x}')

#Reformat function notations
for letter in string.ascii_lowercase+string.ascii_uppercase:
    subText = re.findall(letter+r'\(.*?\)', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,letter+'(x)')
    
#Removing math formatting
mathFormats = ['\mathnormal {', '\mathrm {', '\mathbf {', '\mathsf {', '\mathtt {','\mathfrak {','\mathcal {','\mathbb {','\mathscr {']
for mathFormat in mathFormats:
    if mathFormat in currentLine:
        tempLine = currentLine.split(mathFormat)
        formattedLine = tempLine[0]
        for i in range(1,len(tempLine)):
            formattedLine = formattedLine + tempLine[i][:tempLine[i].find('}')]+ tempLine[i][(tempLine[i].find('}')+1):]
        currentLine = formattedLine

####
#Scrape equation
####
#Run Functions
scrapedWikiEquations = []
scrapedLinks = []
scrapedEquations = []
skippedEquations = []
scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(equation,'currentLink',currentLine)

####
#Scrape Equation
####
eq = scrapedEquations[0]
parsedEquations = []
x=0
if not eq.isnumeric(): #Sympy crashes if latex is a numeric number without any operations, so we skip if this is the case
    tempEq = parse_latex(eq) #Translate equation from Latex to Sympy format
    eqSymbols = list(tempEq.free_symbols) #Extract all symbols from the equation
    eqOperations = str(sp.count_ops(tempEq,visual=True)).split('+') #Extract all nodes of the Sympy tree from the equation

    #Cycle through each node
    operations = []
    opTypes = []
    for eqOp in eqOperations:
        if '*' in eqOp: #Determines if an operation occurs more than one time
            operations.append([eqOp.split('*')[1].strip(),int(eqOp.split('*')[0].strip())])
            opTypes.append(eqOp.split('*')[1].strip())
        else: #When an operation only occurs once
            operations.append([eqOp.strip(), 1])
            opTypes.append(eqOp.strip())
            
    #Adjust Operations
    if ('POW' in opTypes) & ('sqrt' in eq): #Square root is represented as both power and division
        operations[opTypes.index('DIV')][1] = int(operations[opTypes.index('DIV')][1])-eq.count('sqrt') #Remove the division count by number of square roots
        if operations[opTypes.index('DIV')][1] == 0: #Remove division if it has decreased count to zero
            operations.remove(['DIV',0])
    
    #Functions
    funcIndexes = [idx for idx, opType in enumerate(opTypes) if 'FUNC' in opType]
    for funcIdx in funcIndexes[::-1]:        
        del operations[funcIdx]
        del opTypes[funcIdx]
            
    #Record operations into variable to be saved
    if eqOperations != ['0']:
        parsedEquations.append(['EQUATION:', tempEq, 'SYMBOLS:', eqSymbols, 'OPERATIONS:', dict(operations), 'LINK:', scrapedLinks[x],'WIKIEQUATION:',scrapedWikiEquations[x]])
else:
    tempEq = ['Rejected as it was numerical']
      
####
##Report Results
####
try:
    print('**********************')
    print('********REPORT********')
    print('**********************')
    print('Scraped: ' + str(equation))
    print('Equation: ' + str(tempEq))
    print('Operations: ' + str(dict(operations)))
    print('Symbols: ' + str(eqSymbols))
    print('**********************')
    print('********REPORT********')
    print('**********************')
except:
    pass

try:
    tree = [tempEq]
    operant = []
    x = 0
    while 1:
        operant.append(tree[x].func)
        for arg in tree[x].args:
            tree.append(arg)
        x+=1
        if x == len(tree):
            break
except:
    pass