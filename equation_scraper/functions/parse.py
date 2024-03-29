###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################
from sympy.parsing.latex import parse_latex
import sympy as sp
import re
import string
import sys   
import pickle
from tqdm import tqdm

from equation_tree.tree import EquationTree
from equation_tree.analysis import get_counts
    
###############################################################################
#1. Determine Functions
###############################################################################
#Define main function
def parse_equations(keywords: list = None):
    databank = _define_parse(keywords)
    if databank['searchKeywords']:
        databank = _load_scraped_data(databank)
        databank = _cycle_equations(databank)
        databank = _parse_equations(databank)
        _save_files(databank) 
    else:
        print('No search keywords were provided.\n')

#Define keyword parsing
def _define_parse(keywords: list = None):
    if keywords is not None:
        searchKeywords = keywords
    elif len(sys.argv) > 1:
        searchKeywords = sys.argv[1:]
    else:
        searchKeywords = []

    #Split super categories from normal categories
    for keyIndex, searchKeyword in enumerate(searchKeywords):
        if len(searchKeyword.split('_')) > 1: #If the keyword has two words and thus is split by an underscore
            searchKeywords[keyIndex] = searchKeyword.split('_')[0] + '_' + searchKeyword.split('_')[1][0].capitalize() + searchKeyword.split('_')[1][1:] #Capitalize the second word
    
    #Setup databank variable
    databank = {'searchKeywords': searchKeywords}
    
    print('Searching for keyword(s): ' + str(searchKeywords) + '\n')

    return databank

#Searches for all links on given URL
def _load_scraped_data(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    
    #Determine filename to load
    saveKeywords = '~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_') #Create string of keywords for file name
    loadPath = saveKeywords.replace('Super:','SUPER')+'/'
    loadName = 'equations_' + saveKeywords + '.txt' #Create file name
    
    #Read scraped operations file
    with open('data/'+loadPath+loadName,'r', encoding="utf-8") as f:
        scrapedWiki = f.readlines()

    #Pack databank
    databank['loadPath'] = loadPath
    databank['loadName'] = loadName
    databank['scrapedWiki'] = scrapedWiki
    
    return databank

#Cycles through all lines of the data to deal with them accordingly
def _cycle_equations(databank):
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
        databank = _process_equation(databank)
    
    return databank

#The main function that organizes the current equation and it's metadata then feeds these to the processing functions
def _process_equation(databank):
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
            currentLine = currentLine.replace(sub,'\Sum(x)')
            
    #The descriptive sum conflicts, and so we convert it to an equation with the same elements
    subText = re.findall(r'\\sum _\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'\Sum(x)')
            
    #Reformat leftover sum notations
    currentLine = currentLine.replace('\\sum','\Sum(x)')
            
    #The descriptive int conflicts, and so we convert it to an equation with the same elements
    subText = re.findall(r'\\int _\{.*?\}', currentLine)
    if subText:
        for sub in subText:
            if sub.count('{') > sub.count('}'): #Integrals have multiple brackets within them and this ensures that it captures the number appropriately
                sub = sub + '}'*(sub.count('{') - sub.count('}'))
            currentLine = currentLine.replace(sub,'\\int{x}')
            
    #Remove any superscripts with brakets as they are not power but instead references
    subText = re.findall(r'\{\(.*?\)\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,'')
            
    #Some variables are spelt out as a whole word, and this replaces that word with the starting letter
    subText = re.findall(r'\\mathrm \{.*?\}', currentLine)
    if subText:
        for sub in subText:
            currentLine = currentLine.replace(sub,sub.split('{')[1].split('}')[0])
            
    #Ignore any euquations with ... as it is more likely a notation
    if ('..' in currentLine) | ('...' in currentLine) | ('\in' in currentLine):
        currentLine = 'x'
        
    ##################################
    ## Equation Splitting           ##
    ##################################

    WikiRelationals = ['<', '\\\nless', '\\\leq', '\\\leqslant', '\\\nleq', '\\\nleqslant', '>', '\\\ngtr', '\\\geq', '\\\geqslant', '\\\ngeq', '\\\ngeqslant', '\\\nleq','\\\nleqslant','\\\nleqq','\\\lneq','\\\lneqq', '\\\lvertneqq', '\\\notin','\\\ngtr','\\\ngeq','\\\ngeqslant','\\\ngeqq','\\\gneq','\\\gneqq','\\\gvertneqq'] #From https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols
    customRelationals = ['\\\heq', '\\\he', '$>', '>=', '$<', '<=', ';']
    splitRelationals = WikiRelationals + customRelationals
    #Split equation dependent on break
    if len(re.split('|'.join(splitRelationals),currentLine))> 1:
        currentLine = re.split('|'.join(splitRelationals),currentLine)
    elif ('\\\\' in currentLine):
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
                databank = _format_equation(databank) #Calls the format equation function 
                databank = _append_variables(databank) #Calls the append variables function
    else:
        databank = _format_equation(databank) #Calls the format equation function 
        databank = _append_variables(databank) #Calls the append variables function
        
    return databank

def _format_equation(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    loadPath = databank['loadPath']
    loadName = databank['loadName']
    if isinstance(databank['currentLine'], list): #Check to see if the input is a list of equations
        currentLine = databank['subEquation'] #If it's a list, use a different variable saying which equation from that list to process
    else:
        currentLine = databank['currentLine'] #If not a list, use the normal variable
        
    if (currentLine[0] != '#') & (currentLine != '\n') & ('{\\begin{cases}' not in currentLine) & ('\\end{cases}' not in currentLine): #The last notation here specifies and if else conditional, and we ignore it as they are generally not equations (but always?)
            
        #Skip equations that are declarations by changing them to x
        wikiExclusions = ['\\neg', '\\prec', '\\nprec', '\\preceq', '\\npreceq', '\\ll', '\\lll', '\\subset', '\\subseteq', '\\sqsubset', '\\sqsubseteq', '\\succ', '\\nsucc', '\\succeq', '\\nsucceq', '\\gg', '\\ggg', '\\supset', '\\supseteq', '\\nsupseteq', '\\sqsubset', '\\sqsupseteq', '\\vdash', '\\smile', '\\models','\\bowtie','\\dashv', '\\frown', '\\nsim', '\\lnsim','\\lnapprox','\\nprec','\\npreceq','\\precneqq','\\precnsim','\\precnapprox','\\nsim','\\nshortmid','\\nmid','\\nvdash','\\nVdash','\\ntriangleleft','\\ntrianglelefteq','\\nsubseteq','\\nsubseteqq','\\subsetneq','\\varsubsetneq','\\subsetneqq','\\varsubsetneqq', '\\gnsim','\\gnapprox','\\nsucc','\\nsucceq','\\succneqq','\\succnsim','\\succnapprox','\\ncong','\\nshortparallel','\\nparallel','\\not\\perp','\\nvDash','\\nVDash','\\ntriangleright','\\ntrianglerighteq','\\nsupseteq','\\nsupseteqq','\\supsetneq','\\varsupsetneq','\\supsetneqq','\\varsupsetneqq', '\\O', '\\emptyset','\\varnothing', '\\cap','\\cup','\\uplus','\\sqcap', '\\sqcup','\\vee','\\wedge','\\oplus','\\ominus','\\otimes','\\oslash','\\odot','\\circ','\\setminus','\\amalg', '\\in', '\\notin', '\\ni','\\exists','\\exists!','\\nexists','\\forall','\\lor','\\land','\\Longrightarrow','\\implies','\\Rightarrow','\\Longleftarrow','\\Leftarrow','\\iff','\\Leftrightarrow','\\top','\\bot','\\angle','\\measuredangle','\\square', '\\rightarrow','\\to','\\mapsto','\\leftarrow','\\gets','\\longmapsto','longrightarrow','longleftarrow', '\\uparrow','\\downarrow','\\updownarrow','\\Uparrow','\\Downarrow','\\Updownarrow', '\\nabla','\\Box','\\infty'] #From https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols
        skipEq = [True for wikiExclusion in wikiExclusions if wikiExclusion in currentLine]
        if len(skipEq) > 0:
            currentLine = 'x'

        #Change special symbols to x symbol
        wikiSpecials = ['\\hbar','\\eth','\\imath','\\jmath','\\ell','\\beth','\\aleph', '\\gimel']
        currentLine = [currentLine := currentLine.replace(excludedSpecial,'x') for excludedSpecial in wikiSpecials][-1]
        
        #Replace other brackets with brackets
        leftBracket = ['\\langle', '\\lceil','\\ulcorner','\\lfloor','\\llcorner', '( \\,', '\\{', '[ \\,']
        rightBracket = ['\\rangle', '\\rceil','\\urcorner', '\\rfloor','\\lrcorner',') \\,', '\\}','] \\,']
        currentLine = [currentLine := currentLine.replace(lB,'(') for lB in leftBracket][-1]
        currentLine = [currentLine := currentLine.replace(rB,')') for rB in rightBracket][-1]
        
        #Change 'set' notations to a single variable x
        wikiSets = ['\\N','\\Z','\\Q','\\mathbb{A}','\\R','\\C','\\mathbb{H}','\\mathbb{O}','\\mathbb{S}']
        currentLine = [currentLine := currentLine.replace(excludedSet,'') for excludedSet in wikiSets][-1]
        
        #Removes specific notations that Sympy cannot comprehend 
        wikiExcludedNotations = ['\\ast', '\\star','\\dagger','\\ddagger', '\\Re','\\Im','\\wp']
        customNotations = ['\\|','\\,','.','\'','%','~',' ','\\,','\\bigl(}','{\\bigr)','\\!','!','\\boldsymbol','\\cdots','\\aligned','\\ddot','\\dot','\mathnormal', '\\mathbf', '\\mathsf', '\\mathtt','\\mathfrak','\\mathcal','\\mathbb','\\mathscr','\\mathit','\\textbf','\\textit','\\texttt','\\ltextsf','\\textrm','\\underline','\\overline','\\bar','\\hat','\\tilde','^{*}','\\overrightarrow','\n'] #TODO: Are removing the cdots/ddots a problem mathematically?           
        excludedNotations = wikiExcludedNotations + customNotations
        currentLine = [currentLine := currentLine.replace(excludedNotation,'') for excludedNotation in excludedNotations][-1]

        #Split equations and retain only one part
        WikiSeparators = {'\\cong': 0,'\\ncong': 0,  '\\equiv': 0, '\\approx': 0, '\\doteq': -1, '\\simeq': -1, '\\sim': -1, '\\propto': 0, '\\neq': 0, '\\parallel': 0, '\\asymp': 0, '\\perp': 0, '\\nparallel': 0}#From https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols
        customSeparators = {'&=&': -1,'&=': -1,',&': 0, ':=': -1, '=:': -1,'\seq': -1}
        separators = WikiSeparators
        separators.update(customSeparators)
        currentLine = [currentLine := currentLine.split(separator)[separators[separator]] if separator in currentLine else currentLine for separator in separators.keys()][-1]
            
        #The equal symbol alone often results in a numeric number (e.g., f(x) = g*f+g = 0). If this is the case, take what's before the equals, otherwise take what's after
        currentEquation = currentLine
        if '=' in currentEquation:
            if currentEquation.split('=')[-1].isnumeric(): #If the last part of the equation is just a solution (i.e., number)
                if len(currentEquation.split('=')) > 2: #If is more than one equals sign
                    currentEquation = currentEquation.split('=')[1] #Take the second equation
                else: #If there is only one equals sign
                    currentEquation = currentEquation.split('=')[0] #Take the first equation
            else: #If the last equation is not numeric
                currentEquation = currentEquation.split('=')[-1] #Use the end
        
        ###################################
        ## Additional Special Exclusions ##
        ###################################
        
        #Change +/-
        currentEquation = currentEquation.replace('\\pm', '+x-')
        currentEquation = currentEquation.replace('\\mp', '+x-')
        
        #Change cdot to multiplication
        currentEquation = currentEquation.replace('\\cdot','*')
    
        #Change times to multiplication
        currentEquation = currentEquation.replace('\\times','*')
        
        #Change div to division
        currentEquation = currentEquation.replace('\\div','/')
        
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
            
        #Transform min notation into a function            
        if ('min' in currentEquation) & ('\min' not in currentEquation):
            currentEquation = currentEquation.replace('min','\min')
            
        #Transform max notation into a function            
        if ('max' in currentEquation) & ('\max' not in currentEquation):
            currentEquation = currentEquation.replace('max','\max')
            
        #Transform max to ReLU
        if ('\max' in currentEquation) & (',0' in currentEquation):
            maxSplits = currentEquation.split('\max')
            for x, maxSplit in enumerate(maxSplits):
                if x > 0:
                    if ',0' in maxSplit:
                        maxSplits[x] = '\ReLU' + maxSplit.replace(',0','')
                    else: 
                        maxSplits[x] = '\max' +  maxSplit
            currentEquation = ''.join(maxSplits)

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
                #currentEquation = currentEquation.replace('(' + '('.join(commaSplit[x].split('(')[-1-openBracketTotal:]) + ',' + ','.join(trackNotations) + ')','(x)') #Replace complex bracket with simple one
                currentEquation = currentEquation.replace('('.join(commaSplit[x].split('(')[-1-openBracketTotal:]) + ',' + ','.join(trackNotations),'(x)') #Replace complex bracket with simple one

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
        wikiExcludedWords = ['Alpha','Beta','Gamma','Delta','Epsilon','Varepsilon','Zeta','Eta','Theta','Vartheta','Iota','Kappa','Varkappa','Lambda','Mu','Nu','Xi','Omicron','Pi','Varpi','Rho','Varrho','Sigma','Varsigma','Tau','Upsilon','Phi','Varphi','Chi','Psi','Omega','Digamma'] #Taken from https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols
        customExcludedWords = ['sum', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'sqrt', 'sum', 'abs', 'exp', 'max', 'min', 'log', 'relu', 'frac'] #Custom inserts
        customExcludedWords.extend([function.capitalize() for function in customExcludedWords])

        excludedWords = wikiExcludedWords+customExcludedWords
        
        for equationWord in equationWords:
            exclude = [False if excludedWord.lower() not in equationWord.lower() else True for excludedWord in excludedWords]
            if (len(equationWord.replace('_',''))> 1) & (True not in exclude) & (equationWord.replace('_','').isnumeric()==False):
                removedFilename = 'data/'+loadPath+'/debug/wordsRemoved_'+loadName
                with open(removedFilename, 'a', encoding="utf-8") as f:
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
    
def _append_variables(databank):
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

def _parse_equations(databank):
    
    parsedEquations = []
    skippedEquations = []
    sympyEquations = []
    latexEquations = []
    allConditionals = {}
    parsedEq = 0
    skippedEq = 0
    unparsedEq = 0
    
    #Unpack databank
    scrapedWikiEquations = databank['scrapedWikiEquations']
    scrapedLinks = databank['scrapedLinks']
    scrapedEquations = databank['scrapedEquations']
    databank['parsedEquations'] = parsedEquations

    #Cycle through each formatted equation
    priorsDict = {
        'metadata':
            {'number_of_equations': 0,
             'unparsed_equations': 0,
             'list_of_operators': ['+','*','-','/','^','**'],
             'list_of_functions': ['**2','**3','sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'sqrt', 'sum', 'abs', 'exp', 'max', 'min', 'log', 'relu'],
             'list_of_constants': ['Alpha','Beta','Gamma','Delta','Epsilon','Varepsilon','Zeta','Eta','Theta','Vartheta','Iota','Kappa','Varkappa','Lambda','Mu','Nu','Xi','Omicron','Pi','Varpi','Rho','Varrho','Sigma','Varsigma','Tau','Upsilon','Phi','Varphi','Chi','Psi','Omega','Digamma'],
             'list_of_equations': []
             }
        }
    
    priorsDict['metadata']['list_of_constants'].extend([constant.lower() for constant in priorsDict['metadata']['list_of_constants']])
    function_list = priorsDict['metadata']['list_of_functions']
    priorsDict['metadata']['list_of_functions'].extend([function.capitalize() for function in function_list])
    priorsDict['metadata']['list_of_functions'].extend([function.upper() for function in function_list])

    equationTrees = []
    for x, eq in enumerate(tqdm(scrapedEquations)):
        #Progress bar
        databank['parsedEq'] = parsedEq
        databank['skippedEq'] = skippedEq
        databank['unparsedEq'] = unparsedEq

        #Create tree of computation graph
        try:
            if not eq.isnumeric(): #Sympy crashes if latex is a numeric number without any operations, so we skip if this is the case (but we are also not interested in these cases)
                tempEq = parse_latex(eq) #Translate equation from Latex to Sympy format
                
                #Convert symbols to variables and constants
                symbols = list(tempEq.free_symbols)
                symbols = [str(symbol) for symbol in symbols]   
                symbols.sort(key=len, reverse=True)
                
                #Reformat variables and constants to carry standardized notation
                for si, symbol in enumerate(symbols):
                    if any([constant in symbol for constant in priorsDict['metadata']['list_of_constants']]):
                        tempEq = tempEq.subs(symbol, sp.Symbol('C̈_'+str(si))) #Constants
                    else:
                        tempEq = tempEq.subs(symbol, sp.Symbol('Ṽ_'+str(si))) #Variables  
                 
                #Reformat all custom functions into the same category     
                def _func_walk(expr, targetFunction):
                    if targetFunction.upper() == expr.func.__name__.upper():
                        return expr.func.__name__
                    for arg in expr.args:
                        formattedFuncName = _func_walk(arg, targetFunction)   
                        if formattedFuncName:
                            return formattedFuncName

                for op in str(sp.count_ops(tempEq, visual=True)).split('+'):
                    funcName = op.split('FUNC_')[-1].replace(' ','')
                    if ('FUNC_' in op) & (funcName.lower() not in priorsDict['metadata']['list_of_functions']):
                        formattedFuncName = _func_walk(tempEq, funcName)
                        tempEq = tempEq.replace(sp.Function(formattedFuncName),sp.Function('customfunc'))
                
                #Define tree rules  
                #is_operator = lambda x: x in ['+','*','-','/','^','**','max','min']   
                is_operator = lambda x: x in priorsDict['metadata']['list_of_operators']
                is_function = lambda x: x in ['customfunc'] + priorsDict['metadata']['list_of_functions']
                is_variable = lambda x: 'Ṽ_' in x
                is_constant = lambda x: 'C̈_' in x  
                              
                #Create tree
                equationTree = EquationTree.from_sympy(
                    tempEq,
                    operator_test=is_operator,
                    variable_test=is_variable,
                    constant_test=is_constant,
                    function_test=is_function)
                                                
                #Record operations into variable to be saved
                eqPriors = get_counts([equationTree])
                if any(depth > 1 for depth in eqPriors['max_depth'].keys()):
                    equationTrees.append(equationTree)
                    priorsDict['metadata']['list_of_equations'].append(str(tempEq))
                    priorsDict['metadata']['number_of_equations'] += 1
                    
                    latexEquations.append(eq)
                    sympyEquations.append(tempEq)
                    parsedEquations.append(['EQUATION:', tempEq, 'SYMBOLS:', eqPriors['features'], 'OPERATIONS:', eqPriors['operators'], 'CONDITIONAL_OPERATIONS:', eqPriors['operator_conditionals'] | eqPriors['function_conditionals'],'LINK:', scrapedLinks[x], 'WIKIEQUATION:',scrapedWikiEquations[x]])
                    parsedEq += 1 
                else:
                    skippedEquations.append(['SKIPPED EQUATION: ' + eq + ' ~WIKIEQUATION: ' + scrapedWikiEquations[x]])
                    skippedEq += 1
            else:
                skippedEquations.append(['SKIPPED EQUATION: ' + eq + ' ~WIKIEQUATION: ' + scrapedWikiEquations[x]])
                skippedEq += 1
                
        except: #If the translation from latex to Sympy of the parsing fails
            skippedEquations.append(['UNPARSED EQUATION: ' + eq + ' ~WIKIEQUATION: ' + scrapedWikiEquations[x]])
            priorsDict['metadata']['unparsed_equations'] += 1
            unparsedEq += 1 #Increase counter 
            pass

    print('Parsed: ' + str(databank['parsedEq']) + ' ... Skipped: ' + str(databank['skippedEq']) + ' ... Unparsed: '+ str(databank['unparsedEq'])) 

    priorsDict['priors'] = get_counts(equationTrees)
    if 'customfunc' in priorsDict['priors']['functions'].keys():
        del priorsDict['priors']['functions']['customfunc']    
    priorsDict['priors']['operators_and_functions'] = priorsDict['priors']['operators'] | priorsDict['priors']['functions']
    
    #Pack databank
    databank['parsedEquations'] = parsedEquations
    databank['sympyEquations'] = sympyEquations
    databank['skippedEquations'] = skippedEquations
    databank['latexEquations'] = latexEquations
    databank['allConditionals'] = allConditionals
    databank['priorsDict'] = priorsDict
    
    return databank

def _save_files(databank):
    
    #Unpack databank
    loadPath = databank['loadPath']
    loadName = databank['loadName']
    parsedEquations = databank['parsedEquations']
    skippedEquations = databank['skippedEquations']
    priorsDict = databank['priorsDict']

    #Save equation-specific priors
    parsedFilename = 'data/'+loadPath+'parsed_'+loadName
    with open(parsedFilename, 'w', encoding="utf-8") as f:
        for parsedItem in parsedEquations:
            f.write(parsedItem[4]+'~'+str(parsedItem[5])+'~'+parsedItem[6]+'~'+str(parsedItem[7])+'~'+parsedItem[2]+'~'+str(parsedItem[3])+'~'+parsedItem[0]+'~'+str(parsedItem[1])+'~'+parsedItem[8]+'~'+str(parsedItem[9][7:-1])+'~'+str(parsedItem[10])+'~'+str(parsedItem[11]))
       
    #Save prior dictionary
    priorFilename = 'data/'+loadPath+'priors_'+loadName.replace('equations_','').replace('.txt','.pkl')
    pickle.dump(priorsDict, open(priorFilename,"wb"))

    #Debug mode prints a new file with a different layout         
    parsedFilename = 'data/'+loadPath+'/debug/debug_parsed_'+loadName
    with open(parsedFilename, 'w', encoding="utf-8") as f:       
        for parsedItem in parsedEquations:
            f.write('\n')
            f.write('************\n')
            f.write(parsedItem[4]+'~'+str(parsedItem[5])+'\n')
            f.write(parsedItem[6]+'~'+str(parsedItem[7])+'\n')
            f.write(parsedItem[2]+'~'+str(parsedItem[3])+'\n')
            f.write(parsedItem[0]+'~'+str(parsedItem[1])+'\n')
            f.write(parsedItem[8]+'~'+str(parsedItem[9][7:-1])+'\n')
            f.write(str(parsedItem[10])+'~'+str(parsedItem[11])+'\n')
            f.write('************\n')            

    #Save file of skipped equations, if any
    skippedFilename = 'data/'+loadPath+'debug/skipped_'+loadName
    with open(skippedFilename, 'w', encoding="utf-8") as f:
        for skippedItem in skippedEquations:
            if '#' not in skippedItem:
                f.write(skippedItem[0])
            
###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    parse_equations()