###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

#import matplotlib as mpl
#mpl.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np 
import pickle
import re

from equation_scraper.functions.parse import _define_parse

###############################################################################
#1. Define Functions
###############################################################################

#Define main function
def plot_priors(keywords: list = None):
    databank = _define_parse(keywords)
    if databank['searchKeywords']:
        databank = _load_parsed_data(databank)
        databank = _unpack_priors(databank)
        _plot_priors(databank)
    else:
        print('Equation Parser: No search keywords were provided')

#Searches for all links on given URL
def _load_parsed_data(databank):
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
    priors = pickle.load(open('data/'+loadPath+loadName, 'rb'))

    #Pack databank
    databank['loadPath'] = loadPath
    databank['loadName'] = loadName
    databank['priors'] = priors

    return databank

def _unpack_priors(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    priors = databank['priors']['priors']['operators_and_functions']
    
    #Create function
    renamed_priors = {}
    def _rename_key(priors, renamed_priors, full_name: str):
        renamed_priors[full_name] = priors[key]

        return renamed_priors
    
    for key in priors.keys():
        
        match key:
            case '+':
                renamed_priors = _rename_key(priors, renamed_priors, 'Addition')
            case '-':
                renamed_priors = _rename_key(priors, renamed_priors, 'Subtraction')
            case '*':
                renamed_priors = _rename_key(priors, renamed_priors, 'Multiplication')
            case '/':
                renamed_priors = _rename_key(priors, renamed_priors, 'Division')
            case '**':
                renamed_priors = _rename_key(priors, renamed_priors, 'Power')
            case '**2':
                renamed_priors = _rename_key(priors, renamed_priors, 'Squared')
            case '**3':
                renamed_priors = _rename_key(priors, renamed_priors, 'Cubed')
            case 'sqrt':
                renamed_priors = _rename_key(priors, renamed_priors, 'Square Root')
            case 'log':
                renamed_priors = _rename_key(priors, renamed_priors, 'Logarithm')
            case 'sin':
                renamed_priors = _rename_key(priors, renamed_priors, 'Sine')
            case 'cos':
                renamed_priors = _rename_key(priors, renamed_priors, 'Cosine')
            case 'tan':
                renamed_priors = _rename_key(priors, renamed_priors, 'Tangent')
            case 'asin':
                renamed_priors = _rename_key(priors, renamed_priors, 'Arc Sine')
            case 'acos':
                renamed_priors = _rename_key(priors, renamed_priors, 'Arc Cosine')
            case 'atan':
                renamed_priors = _rename_key(priors, renamed_priors, 'Arc Tangent')
            case 'sinh':
                renamed_priors = _rename_key(priors, renamed_priors, 'Hyperbolic Sine')
            case 'cosh':
                renamed_priors = _rename_key(priors, renamed_priors, 'Hyperbolic Cosine')
            case 'tanh':
                renamed_priors = _rename_key(priors, renamed_priors, 'Hyperbolic Tangent')
            case 'sum':
                renamed_priors = _rename_key(priors, renamed_priors, 'Summation')
            case 'abs':
                renamed_priors = _rename_key(priors, renamed_priors, 'Absolute')
            case 'exp':
                renamed_priors = _rename_key(priors, renamed_priors, 'Exponential')
            case 'max':
                renamed_priors = _rename_key(priors, renamed_priors, 'Maximum')
            case 'min':
                renamed_priors = _rename_key(priors, renamed_priors, 'Minimum')
            case 'relu':
                renamed_priors = _rename_key(priors, renamed_priors, 'ReLU')
            case 'customfunc':
                pass #We do not want to track these
            case _:
                renamed_priors = _rename_key(priors, renamed_priors, key)
    
    #Sort priors
    renamed_priors = {key: value for key, value in sorted(renamed_priors.items(), key=lambda item: item[1], reverse=True)}
    
    #Pack databank
    databank['priors_and_functions'] = renamed_priors 
    
    return databank

def _plot_priors(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    
    #Unpack databank
    priors = databank['priors_and_functions']
    searchKeywords = databank['searchKeywords']
    
    def _add_space(word):
        return re.sub(r"(\w)([A-Z])", r"\1 \2", word)
    title_list = [_add_space(searchKeyword.replace('Super:','')) for searchKeyword in searchKeywords]
    title = ','.join(title_list)
    title = title.replace('_','')
    
    #Setup figure
    fig, ax = plt.subplots(figsize=(16, 4), dpi=100) #Plot formatting
    fig.subplots_adjust(bottom=0.3)
    
    #ax.bar(np.arange(len(priors)), np.log(list(priors.values())))
    bars = ax.bar(np.arange(len(priors)), priors.values(), alpha = .5)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
        textcoords="offset points", ha='center', va='bottom', color='grey')

    ax.set_xticks(np.arange(len(priors)))
    ax.set_xticklabels(priors.keys(), rotation=45, ha='right')
    ax.spines[['left', 'bottom']].set_color('grey')
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(axis='x', colors='grey')
    ax.tick_params(axis='y', colors='grey')
    ax.set_ylabel('Count', color='grey')
    ax.set_ylim(0, np.max(list(priors.values()))*1.1)
    ax.set_title(title, loc='left', color='grey')

    _save_figure(databank)
    
def _save_figure(databank):
    loadPath = databank['loadPath']
    loadName = databank['loadName']
    plt.savefig('data/'+loadPath+loadName.replace('priors_','figure_').replace('.pkl','.png'), dpi='figure') #Save figure
   
###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    plot_priors()

