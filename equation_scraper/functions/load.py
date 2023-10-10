
import pickle
import sys
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

def load_prior(keywords: list = None):

    if keywords is not None:
        searchKeywords = keywords
    elif len(sys.argv) > 1:
        searchKeywords = sys.argv[1:]
    else:
        searchKeywords = []

    if searchKeywords:
        #Split super categories from normal categories
        for keyIndex, searchKeyword in enumerate(searchKeywords):
            if len(searchKeyword.split('_')) > 1: #If the keyword has two words and thus is split by an underscore
                searchKeywords[keyIndex] = searchKeyword.split('_')[0] + '_' + searchKeyword.split('_')[1][0].capitalize() + searchKeyword.split('_')[1][1:] #Capitalize the second word
        saveKeywords = '~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_') #Create string of keywords for file name
        loadPath = saveKeywords.replace('Super:','SUPER')+'/'
        loadName = 'priors_' + saveKeywords + '.pkl' #Create file name
        filename = 'data/'+loadPath+loadName
    else:
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    
    return pickle.load(open(filename,'rb'))

###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    es_priors = load_prior()

    print('**********METADATA**********\n')
    for key in es_priors['metadata'].keys():
        print(f"{key}: {es_priors['metadata'][key]}\n")

    print('***********PRIORS***********\n')
    for key in es_priors['priors'].keys():
        print(f"{key}: {es_priors['priors'][key]}\n")
