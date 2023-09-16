###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################


###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

import matplotlib.pyplot as plt
import numpy as np 
import collections
import inflect
p = inflect.engine()
import os
import pickle

#Determine categories to search
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        searchKeywords = sys.argv[1:]
    else:
        searchKeywords = ['Super:MaterialsScience']
        
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
    loadName = 'priors_' + saveKeywords + '.pkl' #Create file name
    
    #Read scraped operations file
    priors = pickle.load(open(os.path.dirname(__file__) + '/../Data/'+loadPath+loadName, 'rb'))

    #Pack databank
    databank['loadPath'] = loadPath
    databank['loadName'] = loadName
    databank['priors'] = priors
    
    return databank

def unpackPriors(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    priors = databank['priors']['priors']['operators_and_functions']
    
    #Create function
    renamed_priors = {}
    def renameKey(priors, renamed_priors, full_name: str):
        renamed_priors[full_name] = priors[key]

        return renamed_priors
    
    for key in priors.keys():
        
        match key:
            case '+':
                renamed_priors = renameKey(priors, renamed_priors, 'Addition')
            case '-':
                renamed_priors = renameKey(priors, renamed_priors, 'Subtraction')
            case '*':
                renamed_priors = renameKey(priors, renamed_priors, 'Multiplication')
            case '/':
                renamed_priors = renameKey(priors, renamed_priors, 'Division')
            case '**':
                renamed_priors = renameKey(priors, renamed_priors, 'Power')
            case '**2':
                renamed_priors = renameKey(priors, renamed_priors, 'Squared')
            case '**3':
                renamed_priors = renameKey(priors, renamed_priors, 'Cubed')
            case 'sqrt':
                renamed_priors = renameKey(priors, renamed_priors, 'Square Root')
            case 'log':
                renamed_priors = renameKey(priors, renamed_priors, 'Logarithm')
            case 'sin':
                renamed_priors = renameKey(priors, renamed_priors, 'Sine')
            case 'cos':
                renamed_priors = renameKey(priors, renamed_priors, 'Cosine')
            case 'tan':
                renamed_priors = renameKey(priors, renamed_priors, 'Tangent')
            case 'asin':
                renamed_priors = renameKey(priors, renamed_priors, 'Arc Sine')
            case 'acos':
                renamed_priors = renameKey(priors, renamed_priors, 'Arc Cosine')
            case 'atan':
                renamed_priors = renameKey(priors, renamed_priors, 'Arc Tangent')
            case 'sinh':
                renamed_priors = renameKey(priors, renamed_priors, 'Hyperbolic Sine')
            case 'cosh':
                renamed_priors = renameKey(priors, renamed_priors, 'Hyperbolic Cosine')
            case 'tanh':
                renamed_priors = renameKey(priors, renamed_priors, 'Hyperbolic Tangent')
            case 'sum':
                renamed_priors = renameKey(priors, renamed_priors, 'Summation')
            case 'abs':
                renamed_priors = renameKey(priors, renamed_priors, 'Absolute')
            case 'exp':
                renamed_priors = renameKey(priors, renamed_priors, 'Exponential')
            case 'max':
                renamed_priors = renameKey(priors, renamed_priors, 'Maximum')
            case 'min':
                renamed_priors = renameKey(priors, renamed_priors, 'Minimum')
            case 'relu':
                renamed_priors = renameKey(priors, renamed_priors, 'ReLU')
            case 'customfunc':
                pass #We do not want to track these
            case _:
                renamed_priors = renameKey(priors, renamed_priors, key)
    
    #Sort priors
    renamed_priors = {key: value for key, value in sorted(renamed_priors.items(), key=lambda item: item[1], reverse=True)}
    renamed_keys = list(renamed_priors.keys())
    mixed_priors = {}
    for ki in range(int(np.ceil(len(renamed_priors)/2))):
        mixed_priors[renamed_keys[ki]] = renamed_priors[renamed_keys[ki]]
        mixed_priors[renamed_keys[-(ki+1)]] = renamed_priors[renamed_keys[-(ki+1)]]
    
    renamed_priors = mixed_priors
    
    #Pack databank
    databank['priors_and_functions'] = renamed_priors 
    print(priors)
    
    return databank

def plotPriors(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    
    #Unpack databank
    priors = databank['priors_and_functions']
    
    #Setup figure
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300) #Plot formatting

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
        
    #Plot figure
    if len(priors.keys()) > 18:
        wedges, texts = ax.pie(priors.values(), startangle=-40, colors = np.concatenate((plt.get_cmap("Pastel1")(np.linspace(0.0, 1, 9)),plt.get_cmap("Pastel2")(np.linspace(0.0, 1,len(priors.keys())-9)),plt.get_cmap("Pastel1")(np.linspace(0.0, 1,len(priors.keys())-9))))) #Add pie chart
    elif len(priors.keys()) > 9:   
        wedges, texts = ax.pie(priors.values(), startangle=-40, colors = np.concatenate((plt.get_cmap("Pastel1")(np.linspace(0.0, 1, 9)),plt.get_cmap("Pastel2")(np.linspace(0.0, 1,len(priors.keys())-9))))) #Add pie chart
    else:
        wedges, texts = ax.pie(priors.values(), startangle=-40, colors = plt.get_cmap("Pastel1")(np.linspace(0.0, 1, len(priors.keys())))) #Add pie chart
    
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
        ax.annotate(list(priors.keys())[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), fontsize=8, horizontalalignment=horizontalalignment, **kw) #Add label to pie chart
    
    #plt.show() #Show figure    
    
def savePriors(databank):
    loadPath = databank['loadPath']
    loadName = databank['loadName']
    plt.savefig(os.path.dirname(__file__)+'/../Data/'+loadPath+loadName.replace('.pkl','')+'_PriorPieChart.png', dpi='figure') #Save figure

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

    databank = unpackPriors(databank)
    
    ###############################################################################
    #7. Plot figure
    ###############################################################################

    plotPriors(databank)
    
    ###############################################################################
    #7. Save figure
    ###############################################################################

    savePriors(databank)
