###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

'''
Environment info

pip install matplotlib

Note: There exists a requirements.txt file
'''

###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################
 
import matplotlib.pyplot as plt
import numpy as np 
import collections
import inflect
p = inflect.engine()
import os

#Determine categories to search
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        searchKeywords = sys.argv[1:]
    else:
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
#1. Define Functions
###############################################################################
#Searches for all links on given URL
def loadParsedData(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    
    #Determine filename to load
    saveKeywords = '~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_') #Create string of keywords for file name
    loadName = 'parsed_equations_' + saveKeywords + '.txt' #Create file name
    
    #Read scraped operations file
    with open(os.path.dirname(__file__) + '/../Data/'+loadName,'r') as f:
        parsedEqs = f.readlines()

    #Pack databank
    databank['loadName'] = loadName
    databank['parsedEqs'] = parsedEqs
    
    return databank

def extractOperations(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    parsedEqs = databank['parsedEqs']
    
    #Setup Variables
    allOps = {}
    opCounts = []
    #Cycle through each line to extract operation information
    for parsedEq in parsedEqs:
        
        parsedOps = parsedEq.split('~')[1][1:-1].replace('\'','').split(',') #Deliminate the file using a tilda deliminator
        
        #Partial derivatives are represented as division, so adjust this accordingly 
        #TODO: Add this to the parsing script
        if ('partial' in parsedEq.split('~')[3]) & ('DIV' in str(parsedOps)): #Determines whether a partial derivative exists
            for i, pO in enumerate(parsedOps): #Cycles the parsed operator
                if 'DIV' in pO: #Determine if a division exists
                    parsedOps[i] = 'DIV: '+str(int(pO.split(':')[1])-int(parsedEq.split('~')[3].count('partial')/2)) #Subtract the derivative from the division operator
                    parsedOps.append('DERIVATIVE: ' + str(int(parsedEq.split('~')[3].count('partial')/2))) #Add derivative as a derivative operator
                    break
        
        #Cycle through operators 
        for parsedOp in parsedOps:
            #if ('FUNC' not in parsedOp.split(':')[0]) & ('NEG' not in parsedOp.split(':')[0]): #TODO: I think we keep NEG as it is a special case (could be transformed to MULT maybe?)
            if ('FUNC' not in parsedOp.split(':')[0]): #Skip function operators #TODO: SHOULD WE KEEP THESE?
                try:
                    if parsedOp.split(':')[0].replace(' ','') in allOps.keys(): #If the operator already exists in the tracking variable, increment accordingly
                        allOps[parsedOp.split(':')[0].replace(' ','')] += int((parsedOp.split(':')[1]).replace(' ','')) #Increment by corresponding frequency
                    else: #If operator does not exist in tracking variable, add it
                        allOps[parsedOp.split(':')[0].replace(' ','')] = int((parsedOp.split(':')[1]).replace(' ','')) #Add operator with corresponding frequency
                except:
                    pass #TODO: ADD DEBUG IN CASE CODE REACHES HERE

        #Determine number of operations per equation
        opCount = 0
        for ops in parsedOps:
            opCount += int(ops.split(' ')[-1])
        opCounts.append(opCount)
    
    #Pack databank
    databank['allOps'] = allOps
    databank['opCounts'] = opCounts
    
    return databank

def reformatOperations(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    ##########################################
    ## Format the number of operations data ##
    ##########################################
    
    #Unpack databank
    allOps = databank['allOps']
    opCounts = databank['opCounts']
    
    #Determine frequency table of number of operators
    opCounter = collections.Counter(opCounts)

    #Sort the frequency table
    sortCounter = list(opCounter.keys())
    sortCounter.sort(reverse=True)
    sortedCounter = {i: opCounter[i] for i in sortCounter}

    #Change labels to words
    plotCounts = dict()
    for opCountKey in sortedCounter.keys():
        plotCounts[str(p.number_to_words(opCountKey)).capitalize()] = sortedCounter[opCountKey]
    
    #########################################
    ## Format the types of operations data ##
    #########################################

    plotOps = {} #Create operator variable
    plotOps['Other'] = 0 #Begin other category as absent
    otherKeys = [] #Tracks other category keys
    #First, force any operators that are too infrequent into the 'other category'
    for key in allOps.keys():
        if allOps[key] < round(np.sum(list(allOps.values()))*.03): #Here, determine if the frequency is too low (current = 3% or lower frequencies are forced to other category)
            plotOps['Other'] += allOps[key] #Increment other category if exists with corresponding frequency
            otherKeys.append(key) #Tracks other keys for debugging purposes
        else:
            plotOps[key] = allOps[key] #Add other category with corresponding frequency
            
    #Remove other category if none were determined
    if plotOps['Other'] == 0:
        del plotOps['Other']

    #Rename corresponding operators from Sympy terminology to English
    if 'MUL' in plotOps:
        plotOps['Multiplication'] = plotOps['MUL']
        del plotOps['MUL']

    if 'DIV' in plotOps:
        plotOps['Division'] = plotOps['DIV']
        del plotOps['DIV']    
        
    if 'ADD' in plotOps:
        plotOps['Addition'] = plotOps['ADD']
        del plotOps['ADD'] 
        
    if 'SUB' in plotOps:
        plotOps['Subtraction'] = plotOps['SUB']
        del plotOps['SUB']  
        
    if 'POW' in plotOps:
        plotOps['Power'] = plotOps['POW']
        del plotOps['POW']    
        
    if 'NEG' in plotOps:
        plotOps['Negative'] = plotOps['NEG']
        del plotOps['NEG']    
    
    if 'COS' in plotOps:
        plotOps['Cosine'] = plotOps['COS']
        del plotOps['COS']   

    if 'SIN' in plotOps:
        plotOps['Sine'] = plotOps['SIN']
        del plotOps['SIN']   
        
    if 'DERIVATIVE' in plotOps:
        plotOps['Derivative'] = plotOps['DERIVATIVE']
        del plotOps['DERIVATIVE']    
        
    if 'LOG' in plotOps:
        plotOps['Logarithm'] = plotOps['LOG']
        del plotOps['LOG']  
        
    #Pack databank
    databank['plotOps'] = plotOps
    databank['plotCounts'] = plotCounts
    
    return databank

def createFigure(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    plotOps = databank['plotOps']
    plotCounts = databank['plotCounts']
    searchKeywords = databank['searchKeywords']

    #Setup figure
    fig, (ax,ax2) = plt.subplots(1,2,figsize=(14, 8), subplot_kw=dict(aspect="equal")) #Plot formatting
    fig.subplots_adjust(wspace=.75)
    
    #Capitalize any super categories
    for keyIndex, searchKeyword in enumerate(searchKeywords):
        if "Super:" in searchKeyword:
            searchKeywords[keyIndex] = searchKeyword.replace('Super:','').upper()
            
    #Combine keywords and plot title
    categoryTitle = ', '.join(searchKeywords).replace('_',' ')
    if len(searchKeywords) > 1: #If there are more than one categories searched
        fig.suptitle('Categories:\n' + categoryTitle, fontsize = 20)
    else: #If there is only one category searched
        fig.suptitle('Category:\n' + categoryTitle, fontsize = 20)

    #Define function for plotting
    def plotPieChart(plotData, ax):    
        wedges, texts = ax.pie(plotData.values(), startangle=-40, colors = plt.get_cmap("Pastel1")(np.linspace(0.0, 1, len(plotData.keys())))) #Add pie chart
        ax.set_title('Types of Operations\n\n', loc='left', fontsize = 15) #Add title

        #Move labels outside of the pie chart
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72) #Format label locations
        kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center") #Determine label formats

        #Adjust labels in a cycle
        for i, p in enumerate(wedges): #Cycle through operators
            ang = (p.theta2 - p.theta1)/2. + p.theta1 #Determine current label location angle
            y = np.sin(np.deg2rad(ang)) #Determine current label location y
            x = np.cos(np.deg2rad(ang)) #Determine current label location x
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))] #Push label horizontally
            connectionstyle = "angle,angleA=0,angleB={}".format(ang) #Add line linking label to plot
            kw["arrowprops"].update({"connectionstyle": connectionstyle}) #Add line linking label to plot
            #TODO ADJUST THE FOLLOWING - THIS WAS FOR A SPECIFIC PLOT WHERE LABELS OVERLAPPED, BUT INSTEAD THE SCRIPT SHOULD DETECT OVERLAP AND MOVE THESE AUTOMATICALLY
            if (list(plotData.keys())[i] == 'Derivative') | (list(plotData.keys())[i] == 'Cosine'):
                ax.annotate(list(plotData.keys())[i], xy=(x, y), xytext=(1.8*np.sign(x), 1.4*y), fontsize=14, horizontalalignment=horizontalalignment, **kw) #Add adjusted label to pie chart
            else: 
                ax.annotate(list(plotData.keys())[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), fontsize=14, horizontalalignment=horizontalalignment, **kw) #Add label to pie chart

    #Plot each pie chart
    plotPieChart(plotOps, ax)
    plotPieChart(plotCounts, ax2)
    
def saveFigure(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    searchKeywords = databank['searchKeywords']

    #Save and display figure
    plt.savefig(os.path.dirname(__file__)+'/../Figures/'+'~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_')+'_PriorPieChart.png') #Save figure
    plt.show() #Show figure
    
###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    ###############################################################################
    #2. Load File
    ###############################################################################
    
    databank = loadParsedData(databank)

    ###############################################################################
    #3. Extract Operation Information 
    ###############################################################################

    databank = extractOperations(databank)

    ###############################################################################
    #4. Reformat operation titles
    ###############################################################################
        
    databank = reformatOperations(databank)

    ###############################################################################
    #5. Plot operators as pie chart
    ###############################################################################

    createFigure(databank)

    ###############################################################################
    #6. Save and plot figure
    ###############################################################################

    saveFigure(databank)