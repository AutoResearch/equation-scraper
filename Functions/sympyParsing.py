###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

'''
Environment info

pip install sympy
pip install antlr4-python3-runtime==4.10

Note: There exists a requirements.txt file
'''

#TODO: It might be skipping anything that ends with \,dy

###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

from sympy.parsing.latex import parse_latex
import sympy as sp
import re
import os
import string
import sys    

#Determine categories to search
if __name__ == '__main__':
    if len(sys.argv) > 1:
        #Check for the debug argument
        debug = False
        debug = [True for arg in sys.argv[1:] if arg=='Debug']
        
        #If debug exists
        if debug:
            debug = debug[0] #Pull it from the list
            sys.argv.remove('Debug') #Remove it from the argument list
            
        #Check for all 
        searchKeywords = sys.argv[1:]
    else:
        debug = False
        searchKeywords = ['Super:Cognitive_psychology', 'Super:Cognitive_neuroscience']
        
    #Split super categories from normal categories
    for keyIndex, searchKeyword in enumerate(searchKeywords):
        if len(searchKeyword.split('_')) > 1: #If the keyword has two words and thus is split by an underscore
            searchKeywords[keyIndex] = searchKeyword.split('_')[0] + '_' + searchKeyword.split('_')[1][0].capitalize() + searchKeyword.split('_')[1][1:] #Capitalize the second word
    
    #Setup databank variable
    databank = {'searchKeywords': searchKeywords}
    
    print('Web Scraping for Priors')
    print('Searching for keyword(s): ' + str(searchKeywords) + '\n')
    
###############################################################################
#1. Determine Functions
###############################################################################
def printProgressBar (databank, iteration, total, prefix = '', suffix = '', decimals = 1, length = 30, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @parameters:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    progressParsed = 'Parsed: ' + str(databank['parsedEq']) + ' ... Skipped: ' + str(databank['skippedEq']) + ' ... Unparsed: '+ str(databank['unparsedEq']) 

    print(f'\r{prefix} |{bar}| {percent}% {suffix} {progressParsed}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#Searches for all links on given URL
def loadScrapedData(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    
    #Determine filename to load
    saveKeywords = '~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_') #Create string of keywords for file name
    loadName = 'equations_' + saveKeywords + '.txt' #Create file name
    
    #Read scraped operations file
    with open(os.path.dirname(__file__) + '/../Data/'+loadName,'r') as f:
        scrapedWiki = f.readlines()

    #Pack databank
    databank['loadName'] = loadName
    databank['scrapedWiki'] = scrapedWiki
    
    return databank

#Cycles through all lines of the data to deal with them accordingly
def cycleEquations(databank, debug = False):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack parameter
    scrapedWiki = databank['scrapedWiki']
    
    #Setup Variables
    databank['scrapedEquations'] = list()
    databank['skippedEquations'] = list()
    databank['scrapedLinks'] = list()
    databank['scrapedWikiEquations'] = list()
    databank['currentLink'] = []

    #Create list of all equations from file 
    for currentLine in scrapedWiki:
        
        #Track current line
        databank['currentLine'] = currentLine
                
        #Hold scraped equation
        databank['wikiLine'] = currentLine
        
        #Determine if current line represents link
        if '#LINK:' in currentLine:
            databank['currentLink'] = currentLine
            
        #Process Equation
        databank = processEquation(databank, debug)
    
    return databank

#The main function that organizes the current equation and it's metadata then feeds these to the processing functions
def processEquation(databank, debug = False):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    currentLine = databank['currentLine']
    
    ##################################
    ## Preliminary equation cleanup ##
    ##################################
    
    #Remove breakline notation when there exists an equation
    if (currentLine[-1] == '\n') & (len(currentLine) > 1):
        currentLine = currentLine[:-1]
    
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
            
    #Replace \mid with |, which will be handled next
    currentLine = currentLine.replace('\\mid','|')
    
    #Remove double vertical bars (norm)
    if '\Vert' in currentLine:
        doubleVBar = currentLine.split('\Vert')
        for vBreak in range(1,len(doubleVBar)):
            if '\|' in doubleVBar[vBreak]:
                currentLine = currentLine.replace('\Vert' + doubleVBar[vBreak].split('\|')[0] + '\|', doubleVBar[vBreak].split('\|')[0])
    
    #Reformat conditional probability notations
    vBarSplit = currentLine.split('|')
    for x in range(len(vBarSplit)-1):
        currentLine = currentLine.replace('(' + vBarSplit[x].split('(')[-1] + '|' + vBarSplit[x+1].split(')')[0] + ')','(x)')
    
    #Reformat conditional probability notations
    subText = re.findall(r'P\\left\(.*?\|.*?\\right\)', currentLine) 
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'p(x)')
            
    #Remove the redundant left and right notations
    currentLine = currentLine.replace('\\left','')
    currentLine = currentLine.replace('\\right','')
            
    #Remove text formatting and replace with t
    subText = re.findall('text\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            #Special circumstance where multiple variables are grouped within text formatting
            if '+' in sub:
                sub.split('{')[1].split('}')[0].count('+')
                currentLine = currentLine.replace('\\'+sub,'+'.join(['x']*(sub.split('{')[1].split('}')[0].count('+')+1)))
            #Normal cases
            else:
                currentLine = currentLine.replace('\\'+sub,'t')
                
    #Reformat subscript notations
    subText = re.findall(r'\_\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            if '=' not in sub:
                currentLine = currentLine.replace(sub,'_{x}')
    
    #The descriptive sum conflicts, and so we convert it to an equation with the same elements
    subText = re.findall(r'\\sum _\{.*?=.*?\}\^\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'x+y')
            
    #The descriptive sum conflicts, and so we convert it to an equation with the same elements
    subText = re.findall(r'\\sum _\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'x+y')
            
    #Reformat leftover sum notations
    currentLine = currentLine.replace('\\sum','x+')
            
    #The descriptive int conflicts, and so we convert it to an equation with the same elements
    subText = re.findall(r'\\int _\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            if sub.count('{') > sub.count('}'): #Integrals have multiple brackets within them and this ensures that it captures the number appropriately
                sub = sub + '}'*(sub.count('{') - sub.count('}'))
            currentLine = currentLine.replace(sub,'\\int{x}')
            
    #Some variables are spelt out as a whole word, and this replaces that word with the starting letter
    subText = re.findall(r'\\mathrm \{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,sub.split('{')[1][0])
            
    #Ignore any euquations with ... as it is more likely a notation
    if ('..' in currentLine) | ('...' in currentLine) | ('\in' in currentLine):
        currentLine = 'x'
        
    ##################################
    ## Equation Splitting           ##
    ##################################
    
    #Split equation dependent on break
    if ('\\\\' in currentLine):
        currentLine = currentLine.split('\\\\') #The equations are split if multiple exist
    #elif (',\\' in currentLine):
    #    currentLine = currentLine.split(',\\') #The equations are split if multiple exist
    #elif ('\\;' in currentLine): #TODO: Is removing this an issue?
    #    currentLine = currentLine.split('\\;')
    elif ('{\\begin{array}{c}' in currentLine):
        currentLine = currentLine.split('{\\begin{array}{c}')
    elif ('\\begin{aligned}' in currentLine):
        currentLine = currentLine.split('\end{aligned}}')[0]
    else: #No splitting necessary
        pass
    
    #Pack parameter
    databank['currentLine'] = currentLine
    
    ##################################
    ## Equation Processing          ##
    ##################################
    
    #Process each sub-equation
    if isinstance(currentLine, list):
        for subEquation in currentLine: #Cycle through each equation
            databank['subEquation'] = subEquation
            if subEquation: #Ensure the sub-equation exists 
                databank = formatEquation(databank, debug) #Calls the format equation function 
                databank = appendVariables(databank) #Calls the append variables function
    else:
        databank = formatEquation(databank, debug) #Calls the format equation function 
        databank = appendVariables(databank) #Calls the append variables function
        
    return databank

def formatEquation(databank, debug = False):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    loadName = databank['loadName']
    if isinstance(databank['currentLine'], list): #Check to see if the input is a list of equations
        currentLine = databank['subEquation'] #If it's a list, use a different variable saying which equation from that list to process
    else:
        currentLine = databank['currentLine'] #If not a list, use the normal variable
    
    if (currentLine[0] != '#') & (currentLine != '\n') & ('{\\begin{cases}' not in currentLine) & ('\\end{cases}' not in currentLine): #The last notation here specifies and if else conditional, and we ignore it as they are generally not equations (but always?)
            
        #TODO: This separator function only keeps one distinct part of the equations, but what about equations where multiple of these exist (e.g., x = f/g = 101). But also, maybe that's alright or else it would bias stronger for these equations as they are interpreted multiple times
        #Split equations to remove the left hand side
        separators = {'&=&': -1,'&=': -1,',&': 0, ':=': -1, '=:': -1, '\leq': 0, '\heq': 0, '\he': 0, '&>': 0, '>': 0, '>=': -1, '\geq': -1, '\seq': -1, '<=': -1, '<': -1, '\cong': 0, '\\equiv': 0, '\\approx': 0}
        #if ('\\equiv' not in currentLine) | ('\\approx' not in currentLine): #TODO: I now use equiv and approx in separators above, but does this cause issues?
        currentEquation = [currentLine := currentLine.split(separator)[separators[separator]] if separator in currentLine else currentLine for separator in separators.keys()][-1]
            
        #The equal symbol alone often results in a numeric number (e.g., f(x) = g*f+g = 0). If this is the case, take what's before the equals, otherwise take what's after
        if '=' in currentEquation:
            if currentEquation.split('=')[-1].isnumeric(): #If the last part of the equation is just a solution (i.e., number)
                if len(currentEquation.split('=')) > 2: #If is more than one equals sign
                    currentEquation = currentEquation.split('=')[1] #Take the second equation
                else: #If there is only one equals sign
                    currentEquation = currentEquation.split('=')[0] #Take the first equation
            else: #If the last equation is not numeric
                currentEquation = currentEquation.split('=')[-1] #Use the end
        
        #Removes specific notations that Sympy cannot comprehend 
            #With comma exclusion
        #excludedNotations = ['\|',';','\\,',',','.','\'','%','~',' ','\\,','\\bigl(}','{\\bigr)','\\!','!','\\boldsymbol','\\cdots','aligned','\\ddot','\\dot','\Rightarrow','\\max','max','\\min','min','\\mid','\mathnormal', '\mathbf', '\mathsf', '\mathtt','\mathfrak','\mathcal','\mathbb','\mathscr','\bar','^{*}','\n'] #TODO: Are removing the cdots/ddots a problem mathematically?           
            #Without comma exclusion:
        excludedNotations = ['\|',';','\\,','.','\'','%','~',' ','\\,','\\bigl(}','{\\bigr)','\\!','!','\\boldsymbol','\\cdots','aligned','\\ddot','\\dot','\Rightarrow','\\max','max','\\min','min','\\mid','\mathnormal', '\mathbf', '\mathsf', '\mathtt','\mathfrak','\mathcal','\mathbb','\mathscr','\\bar','^{*}','\n'] #TODO: Are removing the cdots/ddots a problem mathematically?           
        currentEquation = [currentEquation := currentEquation.replace(excludedNotation,'') for excludedNotation in excludedNotations][-1]
        
        ###################################
        ## Additional Special Exclusions ##
        ###################################
        
        #Change cdot to multiplication
        currentEquation = currentEquation.replace('\\cdot','*')
    
        #Change times to multiplication
        currentEquation = currentEquation.replace('\\times','*')
        
        #Change four slashes
        currentEquation = currentEquation.replace('\\\\','\\') #In some cases, these do not indicate multiple equations (as above), but an artificial combination of two sets of slashes (perhaps due to the splitting of equations)
        
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
                    
        #Change vertical bar notations
        if '\\vert' in currentEquation:
            currentEquation = currentEquation.replace('\\vert','|')
        
        #Remove odd notation (this is caused by the symbol before the addition and not the addition itself)
        if '\+' in currentEquation:
            currentEquation = currentEquation.replace('\+','+')
        
        #Remove odd notation
        if '\-' in currentEquation:
            currentEquation = currentEquation.replace('\-','-')
            
        #Reformat cosine
        if ('cos' in currentEquation) & ('\cos' not in currentEquation):
            currentEquation = currentEquation.replace('cos','\cos')
            
        #Reformat sine
        if ('sin' in currentEquation) & ('\sin' not in currentEquation):
            currentEquation = currentEquation.replace('sin','\sin')
            
        #Reformat over into division
        if ('\\over' in currentEquation):
            currentEquation = currentEquation.replace('\\over','/')
            
        #Different log notations exist, so we need to conform any log operation to fir these notations
        if ('\log' in currentEquation) & ('\log(' not in currentEquation) & ('\log{' not in currentEquation):
            currentEquation = currentEquation.replace('\log','\log ')    
            
        #Encapsulate lambda so it does not concatenate with other notations
        if '\\lambda' in currentEquation:
            currentEquation = currentEquation.replace('\\lambda','(\\lambda)')
            
        #Sometimes comma separated parameters in subscript are split into separate notations, so here we combine them
        if '},_{' in currentEquation:
            currentEquation = currentEquation.replace('},_{','')
            
        #If there is a leading negative sign, we want to treat it as *-1, so we change it to a multiplication
        if '(-{' in currentEquation:
            currentEquation = currentEquation.replace('(-{','(x*{')
            
        #This indicates a ReLU function (max(x,0)), for now removing the ,0 is solving some issues
        #TODO: Change this to explicitly link to ReLU (needs a method for this function to define operations)
        if ',0' in currentEquation:
            currentEquation = currentEquation.replace(',0','')

        #Remove backslashes at the end of the equations
        if '\\' == currentEquation[-1:]:
            currentEquation = currentEquation[:-1]
            
        #Symbols are sometimes within the text as a lone subscript, so we remove this and make it a normal symbol
        if currentEquation:
            if ('_' == currentEquation[0]):
                currentEquation = currentEquation[1:]
            
        #The n_{y}^{z}(a) notation can cause errors, so replace it with n_{x}    
        for outer in string.ascii_letters:
            if '_{x}^{'+outer+'}(' in currentEquation:
                currentEquation = currentEquation.replace('_{x}^{'+outer+'}','_{x}')
                
        #The n_{y}(z) notation can cause errors, so replace it with n_{x}    
        for outer in string.ascii_letters:
            if '_{x}('+outer+')' in currentEquation:
                currentEquation = currentEquation.replace('_{x}('+outer+')','_{x}')
                
        #The n^{y}(z) notation can cause errors, so replace it with n_{x}    
        for inner in string.ascii_letters:
            for outer in string.ascii_letters:
                if '^{'+inner+'}('+outer+')' in currentEquation:
                    currentEquation = currentEquation.replace('^{'+inner+'}('+outer+')','_{x}')
                       
        #Remove land notation
        landSplit = currentEquation.split('\land')
        for x in range(len(landSplit)-1):
            currentEquation = currentEquation.replace('(' + landSplit[x].split('(')[-1] + '\land' + landSplit[x+1].split(')')[0] + ')','(x)')

        #Many notations is simply a comma between two letters (i,j), so we conform these to a symbol (i)
        for first in string.ascii_letters:
            for second in string.ascii_letters:
                if first+','+second in currentEquation:
                    currentEquation = currentEquation.replace(first+','+second,first)
                    
        #Compact arrays (x, y, ...) into a single notation (x)
        commaSplit = currentEquation.split(',')
        for x in range(len(commaSplit)-1): #Check one sub-list at a time
            if '(' in commaSplit[x]: #Check if this sublist begins a bracket
                trackNotations = [] #Create empty variable
                openBracketCount = 0 #Create bracket count
                
                #Determine now many brackets exist within the first notation, while ignoring everything before the bracket itself
                bracketSplit = commaSplit[x].split('(') #Split all brackets
                bracketSplit.reverse() #Reverse order
                openBracketTotal = 0 #Initiate defaul value 
                for sub in bracketSplit: #Iterate through brackets
                    if ')' in sub: #Determine if there is a closed bracket
                        openBracketTotal += 1 #Record number of closed brackets
                    else: #If no closed brackets, this is where the bracket was opened
                        break #Move ahead
                
                for y in range(x+1,len(commaSplit)): #Cycle through all sub-lists after current 
                    if '(' in commaSplit[y].split(')')[0]: #Check if another open bracket exists within these brackets
                        openBracketCount += 1 #If so, keep count
                        openBracketTotal += 1 #If so, keep count
                    if ')' in commaSplit[y]: #Check if the end bracket exists
                        if openBracketCount == 0: #Check if this is the end bracket for the current open bracket
                            trackNotations.append(commaSplit[y].split(')')[0]) #Track what was in the bracket before the end
                            break #Stop searching
                        else: #If it is not the proper end bracket
                            openBracketCount -= 1 #Reduce count
                            trackNotations.append(commaSplit[y]) #Track notation
                    else:
                        trackNotations.append(commaSplit[y]) #Track intermediate notations  
            if 'trackNotations' in locals():
                currentEquation = currentEquation.replace('(' + '('.join(commaSplit[x].split('(')[-1-openBracketTotal:]) + ',' + ','.join(trackNotations) + ')','(x)') #Replace complex bracket with simple one

        #Remove any leftover commas
        currentEquation = currentEquation.replace(',','')
               
        #Check if a number is preceeded by a slash (unsure why this occurs sometimes, but it is here removed) 
        for subEq in currentEquation.split('\\'):
            if subEq:
                if subEq[0].isdigit():
                    currentEquation = currentEquation.replace('\\'+subEq[0],subEq[0])
            
        #Remove the operatorname tag
        if 'operatorname' in currentEquation:
            try:
                operatorVar = currentEquation.split('\operatorname {')[1].split('}')[0]
                currentEquation = currentEquation.replace('\operatorname {'+operatorVar+'}',operatorVar[0])
            except:
                currentEquation = currentEquation.replace('\operatorname {','')[:-1]
                
        #Adapt notations that use entire words
        #Find all words
        regex = r'\b\w+\b'
        equationWords=re.findall(regex,currentEquation)

        #Pull out only words 4+ characters and change notation
        excludedWords = ['frac','sigma','Sigma','delta','Delta','theta','Theta','beta','Beta','lambda','Lambda','epsilon','Epsilon','sqrt','Sqrt','times','Times']
        for equationWord in equationWords:
            exclude = [False if excludedWord not in equationWord else True for excludedWord in excludedWords]
            if (len(equationWord.replace('_',''))> 3) & (True not in exclude) & (equationWord.replace('_','').isnumeric()==False):
                if debug == True:
                    removedFilename = os.path.dirname(__file__) + '/../Data/wordsRemoved_'+loadName
                    with open(removedFilename, 'a') as f:
                        f.write(equationWord.replace('_',''))
                        f.write('\n')
                currentEquation = currentEquation.replace(equationWord.replace('_',''), 'x')
                
    #If an equation was found and reformatted, return it
    if ('currentEquation' in locals()):
        if (currentEquation != ''):
            databank['currentEquation'] = currentEquation
        else:
            databank['currentEquation'] = []
    else:
        databank['currentEquation'] = []
    
    return databank
    
def appendVariables(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    wikiLine = databank['wikiLine']
    currentLink = databank['currentLink']
    currentEquation = databank['currentEquation']
    scrapedWikiEquations = databank['scrapedWikiEquations']
    scrapedLinks = databank['scrapedLinks']
    scrapedEquations = databank['scrapedEquations']
    skippedEquations = databank['skippedEquations']
    if isinstance(databank['currentLine'], list): #Check to see if the input is a list of equations
        currentLine = databank['subEquation'] #If it's a list, use a different variable saying which equation from that list to process
    else:
        currentLine = databank['currentLine'] #If not a list, use the normal variable
    
    if currentEquation:
        scrapedWikiEquations.append(wikiLine) #Track raw equations as scraped from wikipedia
        scrapedLinks.append(currentLink) #Track the URL of the equation
        scrapedEquations.append(currentEquation) #Track reformatted equations used in parsing
    else:
        skippedEquations.append(currentLine) #Track if an equation did not make it through reformatting
    
    #Pack databank
    databank['scrapedWikiEquations'] = scrapedWikiEquations
    databank['scrapedLinks'] = scrapedLinks
    databank['scrapedEquations'] = scrapedEquations
    databank['skippedEquations'] = skippedEquations
    
    return databank

def parseEquations(databank, debug = True):
    parsedEquations = []
    skippedEquations = []
    parsedEq = 0
    skippedEq = 0
    unparsedEq = 0
    
    #Unpack databank
    scrapedWikiEquations = databank['scrapedWikiEquations']
    scrapedLinks = databank['scrapedLinks']
    scrapedEquations = databank['scrapedEquations']
    databank['parsedEquations'] = parsedEquations
    
    #Define a walking function
    def powerWalk(eq, powerLabels):
        if ('Pow' in str(eq.func)) & (str(eq) != '1/2'):
            exponents = [arg for arg in eq.args if 'numbers' in str(arg.func)]
            for exponent in exponents:
                if str(exponent) == '1/2':
                    powerLabels.append('SQRT')
                elif (exponent <= 3) & (exponent > 0):
                    powerLabels.append('POW'+str(exponent))
                else: #If it's a power of 4 or higher, we will keep it as a general label of 'power'
                    pass
        for arg in eq.args:
            powerWalk(arg, powerLabels)
        return powerLabels
    
    #Cycle through each formatted equation
    for x, eq in enumerate(scrapedEquations):
        #Progress bar
        databank['parsedEq'] = parsedEq
        databank['skippedEq'] = skippedEq
        databank['unparsedEq'] = unparsedEq
        printProgressBar(databank,x,len(scrapedEquations)-1)

        #Create tree of computation graph
        try:
            if not eq.isnumeric(): #Sympy crashes if latex is a numeric number without any operations, so we skip if this is the case (but we are also not interested in these cases)

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
                        
                #Adjust Operations (Sympy sometimes represents operations with extra steps - e.g., square root = power and division, because x^(1/2))
                
                #Square Root adjustment (TODO: could combine this with the next process)
                if ('POW' in opTypes) & ('sqrt' in eq): #Square root is represented as both power and division
                    operations[opTypes.index('DIV')][1] = int(operations[opTypes.index('DIV')][1])-eq.count('sqrt') #Remove the division count by number of square roots
                    if operations[opTypes.index('DIV')][1] == 0: #Remove division if it has decreased count to zero
                        del operations[opTypes.index('DIV')]
                        del opTypes[opTypes.index('DIV')]
                        
                #Adjust power operations to be more specific (e.g., power of 2, square root)
                if ('POW' in opTypes):
                    powerLabels = powerWalk(tempEq, [])
                    
                    #Iterate through the labels and add them to the operation
                    for powerLabel in powerLabels:
                        operations[opTypes.index('POW')][1] -= 1
                        if powerLabel not in opTypes: #If the label does not exist, add it
                            opTypes.append(powerLabel)
                            operations.append([powerLabel, 1])
                        else: #If the label exists, add one to it's count
                            operations[opTypes.index(powerLabel)][1] += 1
                            
                    #Remove power if it has decreased count to zero
                    if operations[opTypes.index('POW')][1] == 0:
                        del operations[opTypes.index('POW')]
                        del opTypes[opTypes.index('POW')]   
                                   
                #Natural Logarithm
                if ('LOG' in opTypes) & ('EXP' in opTypes): #Natural logarithm is represented as Log and Exp
                    numberNL = eq.count('\ln') #Determine number of NLs
                    operations[opTypes.index('EXP')][1] -= numberNL #Remove from log
                    operations[opTypes.index('LOG')][1] -= numberNL #Remove from exp
                    operations.append(['NL',numberNL]) #Add as NL
                    if operations[opTypes.index('EXP')][1] == 0: #Remove exp if it has decreased count to zero
                        del operations[opTypes.index('EXP')]
                        del opTypes[opTypes.index('EXP')]
                    if operations[opTypes.index('LOG')][1] == 0: #Remove log if it has decreased count to zero
                        del operations[opTypes.index('LOG')]
                        del opTypes[opTypes.index('LOG')]
                        
                #Functions
                funcIndexes = [idx for idx, opType in enumerate(opTypes) if 'FUNC' in opType]
                for funcIdx in funcIndexes[::-1]:
                    del operations[funcIdx]
                    del opTypes[funcIdx]
                    
                #Record operations into variable to be saved
                if (eqOperations != ['0']) & (len(operations)!=0) &(len(eqSymbols)!=0):
                    parsedEquations.append(['EQUATION:', tempEq, 'SYMBOLS:', eqSymbols, 'OPERATIONS:', dict(operations), 'LINK:', scrapedLinks[x], 'WIKIEQUATION:',scrapedWikiEquations[x]])
                    parsedEq += 1 
                else:
                    skippedEquations.append(['SKIPPED EQUATION: ' + eq + ' ~WIKIEQUATION: ' + scrapedWikiEquations[x]])
                    skippedEq += 1
            else:
                skippedEquations.append(['SKIPPED EQUATION: ' + eq + ' ~WIKIEQUATION: ' + scrapedWikiEquations[x]])
                skippedEq += 1
                
        except: #If the translation from latex to Sympy of the parsing fails
            if not debug:
                raise
            skippedEquations.append(['UNPARSED EQUATION: ' + eq + ' ~WIKIEQUATION: ' + scrapedWikiEquations[x]])
            unparsedEq += 1 #Increase counter 
            print('FAILURE - Likely not convertible from latex to sympy') #Error warning
            if debug: #This allows the code to proceed with unparsed equations if the value is 0 or greater. E.g., skip > 0 means that one unparsed equation will be let through (mostly for debugging purposes)
                print(scrapedWikiEquations[x]) #Print the scraped equation that failed
                print(eq) #Print the equation that failed
            else:
                print(scrapedWikiEquations[x]) #Print the scraped equation that failed
                print(eq) #Print the equation that failed
                break
    
    #Pack databank
    databank['parsedEquations'] = parsedEquations
    databank['skippedEquations'] = skippedEquations
    
    return databank

def saveFiles(databank, debug = False):
    
    #Unpack databank
    loadName = databank['loadName']
    parsedEquations = databank['parsedEquations']
    skippedEquations = databank['skippedEquations']
    
    parsedFilename = os.path.dirname(__file__) + '/../Data/parsed_'+loadName
    with open(parsedFilename, 'w') as f:
        for parsedItem in parsedEquations:
            f.write(parsedItem[4]+'~'+str(parsedItem[5])+'~'+parsedItem[2]+'~'+str(parsedItem[3])+'~'+parsedItem[0]+'~'+str(parsedItem[1])+'~'+parsedItem[6]+'~'+str(parsedItem[7][7:-1])+'~'+str(parsedItem[8])+'~'+str(parsedItem[9]))
        
    #Debug mode prints a new file with a different layout    
    if debug==True:        
        parsedFilename = os.path.dirname(__file__) + '/../Data/debug_parsed_'+loadName
        with open(parsedFilename, 'w') as f:       
            for parsedItem in parsedEquations:
                f.write('\n')
                f.write('************\n')
                f.write(parsedItem[4]+'~'+str(parsedItem[5])+'\n')
                f.write(parsedItem[2]+'~'+str(parsedItem[3])+'\n')
                f.write(parsedItem[0]+'~'+str(parsedItem[1])+'\n')
                f.write(parsedItem[6]+'~'+str(parsedItem[7][7:-1])+'\n')
                f.write(str(parsedItem[8])+'~'+str(parsedItem[9])+'\n')
                f.write('************\n')            

    #Save file of skipped equations, if any
    skippedFilename = os.path.dirname(__file__) + '/../Data/skipped_'+loadName
    with open(skippedFilename, 'w') as f:
        for skippedItem in skippedEquations:
            if '#' not in skippedItem:
                f.write(skippedItem[0])
            
###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    ###############################################################################
    #2. Load Data and Setup Variables
    ###############################################################################
    databank = loadScrapedData(databank)

    ###############################################################################
    #3. Re-Format Latex Equations to Comply with Sympy Translation
    ###############################################################################

    databank = cycleEquations(databank, debug)

    ###############################################################################
    #4. Parse Equations
    ###############################################################################

    databank = parseEquations(databank, debug)

    ###############################################################################
    #5. Save Files
    ###############################################################################

    saveFiles(databank, debug) 