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
        searchKeywords = ['Super:Cognitive_psychology']
        
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
    loadPath = saveKeywords.replace('Super:','SUPER')+'/'
    loadName = 'parsed_equations_' + saveKeywords + '.txt' #Create file name
    
    #Read scraped operations file
    with open(os.path.dirname(__file__) + '/../Data/'+loadPath+loadName,'r', encoding="utf-8") as f:
        parsedEqs = f.readlines()

    #Pack databank
    databank['loadPath'] = loadPath
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
        total_ops = np.sum([int(parsedOp.split(':')[1]) for parsedOp in parsedOps if 'FUNC' not in parsedOp.split(':')[0]])
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

#Function to rename corresponding operators from Sympy terminology to English
def renameOperations(ops):
    if 'MUL' in ops:
        ops['Multiplication'] = ops['MUL']
        del ops['MUL']

    if 'DIV' in ops:
        ops['Division'] = ops['DIV']
        del ops['DIV']    
        
    if 'ADD' in ops:
        ops['Addition'] = ops['ADD']
        del ops['ADD'] 
        
    if 'SUB' in ops:
        ops['Subtraction'] = ops['SUB']
        del ops['SUB']  
        
    if 'POW' in ops:
        ops['Power'] = ops['POW']
        del ops['POW']   
    
    if 'POW1' in ops:
        del ops['POW1']  
        
    if 'POW2' in ops:
        ops['Squared'] = ops['POW2']
        del ops['POW2']    
    
    if 'POW3' in ops:
        ops['Cubed'] = ops['POW3']
        del ops['POW3'] 
           
    if 'SQRT' in ops:
        ops['Square Root'] = ops['SQRT']
        del ops['SQRT']    
        
    if 'NEG' in ops:
        ops['Negative'] = ops['NEG']
        del ops['NEG']    
    
    if 'COS' in ops:
        ops['Cosine'] = ops['COS']
        del ops['COS']   

    if 'SIN' in ops:
        ops['Sine'] = ops['SIN']
        del ops['SIN']   
        
    if 'DERIVATIVE' in ops:
        ops['Derivative'] = ops['DERIVATIVE']
        del ops['DERIVATIVE']    
        
    if 'LOG' in ops:
        ops['Logarithm'] = ops['LOG']
        del ops['LOG']  
        
    if 'SUM' in ops:
        ops['Summation'] = ops['SUM']
        del ops['SUM']  
        
    if 'NL' in ops:
        ops['Natural Logarithm'] = ops['NL']
        del ops['NL']  
        
    if 'EXP' in ops:
        ops['Exponential'] = ops['EXP']
        del ops['EXP']
        
    if 'MIN' in ops:
        ops['Minimum'] = ops['MIN']
        del ops['MIN']
    
    if 'MAX' in ops:
        ops['Maximum'] = ops['MAX']
        del ops['MAX']
    
    if 'RELU' in ops:
        ops['ReLU'] = ops['RELU']
        del ops['RELU']
        
    if 'ABS' in ops:
        ops['Absolute'] = ops['ABS']
        del ops['ABS']
        
    return ops
    
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

    reportOps = {} #Create operator variable
    plotOps = {} #Create operator variable
    plotOps['Other'] = 0 #Begin other category as absent
    otherKeys = {} #Tracks other category keys
    
    #### Operations with frequency counts first
    #First, force any operators that are too infrequent into the 'other category'
    for key in allOps.keys():
        reportOps[key] = allOps[key] #Add other category with corresponding frequency
        if allOps[key] < round(np.sum(list(allOps.values()))*.03): #Here, determine if the frequency is too low (current = 3% or lower frequencies are forced to other category)
            plotOps['Other'] += allOps[key] #Increment other category if exists with corresponding frequency
            otherKeys[key] = 1 #Tracks other keys for debugging purposes
        else:
            plotOps[key] = allOps[key] #Add other category with corresponding frequency
            
    #Remove other category if none were determined
    if plotOps['Other'] == 0:
        del plotOps['Other']
        
    #Rename labels
    otherKeys = renameOperations(otherKeys)
    plotOps = renameOperations(plotOps)
    reportOps = renameOperations(reportOps)

    #Pack databank
    databank['plotOps'] = plotOps
    databank['reportOps'] = reportOps
    databank['plotCounts'] = plotCounts
    databank['otherKeys'] = otherKeys
    
    return databank

def createFigure(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    plotOps = databank['plotOps']
    plotCounts = databank['plotCounts']
    otherKeys = databank['otherKeys']
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
        fig.suptitle('Categories:\n' + categoryTitle, fontsize = 16)
    else: #If there is only one category searched
        fig.suptitle('Category:\n' + categoryTitle, fontsize = 16)

    #Define function for plotting
    def plotPieChart(plotData, otherKeys, ax, titleLabel):    
        if len(plotData.keys()) > 9:   
            wedges, texts = ax.pie(plotData.values(), startangle=-40, colors = np.concatenate((plt.get_cmap("Pastel1")(np.linspace(0.0, 1, 9)),plt.get_cmap("Pastel2")(np.linspace(0.0, 1,len(plotData.keys())-9))))) #Add pie chart
        else:
            wedges, texts = ax.pie(plotData.values(), startangle=-40, colors = plt.get_cmap("Pastel1")(np.linspace(0.0, 1, len(plotData.keys())))) #Add pie chart

        ax.set_title(titleLabel + '\n\n', loc='left', fontsize = 13) #Add title
        if otherKeys:
            ax.annotate('Note: Other category contains ' + ', '.join(otherKeys.keys()), xy = (-.1, -.2), xycoords='axes fraction', ha='left', va="center", fontsize=8)

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
                ax.annotate(list(plotData.keys())[i], xy=(x, y), xytext=(1.8*np.sign(x), 1.4*y), fontsize=8, horizontalalignment=horizontalalignment, **kw) #Add adjusted label to pie chart
            else: 
                ax.annotate(list(plotData.keys())[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), fontsize=8, horizontalalignment=horizontalalignment, **kw) #Add label to pie chart

    #Plot each pie chart
    plotPieChart(plotOps, otherKeys, ax, 'Type of Operations (Frequency)')
    plotPieChart(plotCounts, [], ax2, 'Number of Operations')
    
def saveFigure(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    
    loadPath = databank['loadPath']
    loadName = databank['loadName']

    #Save and display figure
    
    plt.savefig(os.path.dirname(__file__)+'/../Data/'+loadPath+loadName.replace('parsed_equations_','').replace('.txt','')+'_PriorPieChart.png') #Save figure
    plt.show() #Show figure
    
def savePriors(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    loadPath = databank['loadPath']
    loadName = databank['loadName']
    reportOps = databank['reportOps'] 
    reportCounts = databank['plotCounts']
    
    #Sort the frequency tables
    sortedReportOps = {key: value for key, value in sorted(reportOps.items(), key=lambda item: item[1], reverse=True)}

    #Save operation data into a priors file (frequency)
    with open('./Data/'+loadPath+'priorOperations_'+loadName,'w', encoding="utf-8") as f:
        f.write('CATEGORY'+','+'~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_')+'\n')
        for key in sortedReportOps.keys():
            f.write(key + ',' + str(sortedReportOps[key]) +'\n')
            
    #Save operation count data into a priors file
    with open('./Data/'+loadPath+'priorCounts_'+loadName,'w', encoding="utf-8") as f:
        f.write('CATEGORY'+','+'~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_')+'\n')
        for key in reportCounts.keys():
            f.write(key + ',' + str(reportCounts[key]) +'\n')

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
    #6. Save priors file
    ###############################################################################
    
    savePriors(databank)
        
    ###############################################################################
    #7. Save and plot figure
    ###############################################################################

    saveFigure(databank)
