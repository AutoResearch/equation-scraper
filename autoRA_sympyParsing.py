###############################################################################
## Written by Chad C. Williams, 2022                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

'''
Environment info

pip install sympy
pip install antlr4-python3-runtime==4.10

Note: There exists a requirements.txt file
'''

###############################################################################
#0. User Inputs - Determine Which Category Pages to Scrape
###############################################################################

#User defined category pages to scrape
searchedKeywords = ['Psychophysics'] 

#Debug mode prints the information to be more easily readable 
printDebug = True

#Determine filename to load
saveKeywords = '_'.join(searchedKeywords) #Create string of keywords for file name
loadName = 'operations_' + saveKeywords + '.txt' #Create file name

###############################################################################
#1. Import Modules
###############################################################################

from sympy.parsing.latex import parse_latex
import sympy as sp
import re
import string

###############################################################################
#2. Determine Functions
###############################################################################

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
    elif '\\;' in currentLine:
        currentLine = currentLine.split('\\;')
        for subEquation in currentLine:
            if subEquation:
                currentEquation = formatEquation(subEquation) #Calls the format equation function 
                scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,currentEquation)
    else: #There only exists one equation
        currentEquation = formatEquation(currentLine) #Calls the format equation function 
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = appendVariables(wikiLine,currentLink,currentEquation,currentLine) #Calls the append variables function

    return scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations

def formatEquation(currentLine):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    if (currentLine[0] != '#') & (currentLine != '\n') & (currentLine.count('=') < 2):
            
            #Split equations to remove the left hand side
            separators = {'&=&': -1,'&=': -1,',&': 0, ':=': -1, '=:': -1,'=': -1, '\leq': 0, '\heq': 0, '\he': 0, '>': -1, '>=': -1, '\geq': -1, '\seq': -1, '<=': -1, '<': -1, '\in': 0, '\cong': 0}
            if ('\\equiv' not in currentLine) | ('\\approx' not in currentLine): #TODO: Removes equivalencies and approximations but should it?
                currentEquation = [currentLine := currentLine.split(separator)[separators[separator]] if separator in currentLine else currentLine for separator in separators.keys()][-1] #TODO: I think this new method removed two equations, figure out if so and why
              
            #Removes specific notations that Sympy cannot comprehend 
            excludedNotations = ['\|',';','\\,',',','.','\'','%','~',' ','\\,','\\bigl(}','{\\bigr)','\\!','!','\\boldsymbol','\\cdots','aligned','\\ddot','\\dot','\Rightarrow','\n'] #TODO: Are removing the cdots/ddots a problem mathematically?
            if 'currentEquation' in locals():             
                currentEquation = [currentEquation := currentEquation.replace(excludedNotation,'') for excludedNotation in excludedNotations][-1]
                
                #Change cdot to multiplication
                currentEquation = currentEquation.replace('\\cdot','*')
                
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
        if (currentEquation != ''):
            return currentEquation
        else:
            return []
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
    
###############################################################################
#3. Load Data and Setup Variables
###############################################################################

#Read scraped operations file
with open('Data/'+loadName,'r') as f:
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
    #Hold scraped equation
    wikiLine = currentLine
    
    #Determine if current line represents link
    if '#LINK:' in currentLine:
        print(currentLine)
        currentLink = currentLine
        
    #Remove breakline notation when there exists an equation
    if (currentLine[-1] == '\n') & (len(currentLine) > 1):
        currentLine = currentLine[:-1]
    
    ####TODO: Add these to the formatEquation function
    #Removing latex formatting
    if '{\\displaystyle' in currentLine:
        currentLine = currentLine.replace('{\\displaystyle','')[:-1]
        
    #Removes superscript notations because they are part of a symbol but treated as a power operator
    superBrackets = re.findall(r'\{\(.*?\)\}', currentLine)
    if superBrackets:
        for superBracket in superBrackets:
            if (superBracket.count('(')==1) | (superBracket.count(')')==1) | (superBracket.count('{')==1) | (superBracket.count('}')==1):
                currentLine = currentLine.replace('^'+superBracket,'')
    
    #Remove bmatrices 
    subText = re.findall(r'{\\begin{bmatrix}.*?\\end{bmatrix}}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'')
    
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
    
###############################################################################
#5. Split and Store all Data, Including Assigning Equations to a Variable
###############################################################################

    #Begin loop to adapt equations to be proper latex    
    if  ('{\\begin{array}{c}' in currentLine): #Sometimes multiple equations are placed within an array and this must be split
        currentLine = currentLine.split('{\\begin{array}{c}')
        for arrayLine in currentLine:
            scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,arrayLine)
            
    elif ('\\begin{aligned}' in currentLine): #Remove website formatting tags
        currentLine = currentLine.split('\end{aligned}}')[0]
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,currentLine)

    else: #Normal cases
        scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = processEquation(wikiLine,currentLink,currentLine)

###############################################################################
#6. Parse Equations
###############################################################################

#Setup variables
skip = 0
parsedEquations = []
rejectedEquations = []
parsedEq = 0
unparsedEq = 0

#Cycle through each formatted equation
for x, eq in enumerate(scrapedEquations):
    #Display metrics for every 10 equations scraped 
    if x % 10 == 0:
        print('\nCurrent Equation:')
        print(eq)
        print('Completed: ' + str(round((x/len(scrapedEquations))*100,2))+ '% ... Parsed: ' + str(parsedEq) + ' ... Unparsed: '+ str(unparsedEq))
    #Create tree of computation graph
    try:
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
                    
            #Adjust Operations (Sympy sometimes represents operations weirdly - e.g., square root = power and division)
            
            #Square Root
            if ('POW' in opTypes) & ('sqrt' in eq): #Square root is represented as both power and division
                operations[opTypes.index('DIV')][1] = int(operations[opTypes.index('DIV')][1])-eq.count('sqrt') #Remove the division count by number of square roots
                if operations[opTypes.index('DIV')][1] == 0: #Remove division if it has decreased count to zero
                    del operations[opTypes.index('DIV')]
                    del opTypes[opTypes.index('DIV')]
                    
            #Functions
            funcIndexes = [idx for idx, opType in enumerate(opTypes) if 'FUNC' in opType]
            for funcIdx in funcIndexes[::-1]:
                del operations[funcIdx]
                del opTypes[funcIdx]
                                
            #Record operations into variable to be saved
            if (eqOperations != ['0']):
                if operations: #Some of the above deletes operations and sometimes it will delete all operations, so we check to make sure there are some left before printing
                    if eqSymbols: #When there exists no symbols, the equation is just a numerical transformation (e.g., 1/3) and should be ignored
                        parsedEquations.append(['EQUATION:', tempEq, 'SYMBOLS:', eqSymbols, 'OPERATIONS:', dict(operations), 'LINK:', scrapedLinks[x],'WIKIEQUATION:',scrapedWikiEquations[x]])
            
            #Increase counter
            parsedEq += 1 
    except: #If the translation from latex to Sympy of the parsing fails
        unparsedEq += 1 #Increase counter 
        print('FAILURE - Likely not convertible from latex to sympy') #Error warning
        if skip > -1: #This allows the code to proceed with unparsed equations if the value is 0 or greater. E.g., skip > 0 means that one unparsed equation will be let through (mostly for debugging purposes)
            print(scrapedWikiEquations[x]) #Print the scraped equation that failed
            print(eq) #Print the equation that failed
            break
        else:
            skip += 1 #Increase skip count
        
###############################################################################
#6. Save Files
###############################################################################

#Save file of scraped equations
parsedFilename = 'Data/parsed_'+loadName
with open(parsedFilename, 'w') as f:
    for parsedItem in parsedEquations:
        if printDebug==False:
            f.write(parsedItem[4]+'~'+str(parsedItem[5])+'~'+parsedItem[2]+'~'+str(parsedItem[3])+'~'+parsedItem[0]+'~'+str(parsedItem[1])+'~'+parsedItem[6]+'~'+str(parsedItem[7][7:-1])+'~'+str(parsedItem[8])+'~'+str(parsedItem[9]))
        else:
            f.write('\n')
            f.write('************\n')
            f.write(parsedItem[4]+'~'+str(parsedItem[5])+'\n')
            f.write(parsedItem[2]+'~'+str(parsedItem[3])+'\n')
            f.write(parsedItem[0]+'~'+str(parsedItem[1])+'\n')
            f.write(parsedItem[6]+'~'+str(parsedItem[7][7:-1])+'\n')
            f.write(str(parsedItem[8])+'~'+str(parsedItem[9])+'\n')
            f.write('************\n')            

#Save file of skipped equations, if any
skippedFilename = 'Data/skipped_'+loadName
with open(skippedFilename, 'w') as f:
    for skippedItem in skippedEquations:
        if '#' not in skippedItem:
            f.write(skippedItem[0])
            f.write('\n') 