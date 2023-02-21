###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

'''
Environment Info

py -m venv webScrapingEnv
.\webScrapingEnv\Scripts\activate

pip install beautifulsoup4
pip install requests

Note: There exists a requirements.txt file
'''

###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

from bs4 import BeautifulSoup, SoupStrainer
from pip._vendor import requests
import time
import os

#Determine categories to search
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        searchKeywords = sys.argv[1:]
    else:
        searchKeywords = ['Psychophysics']
        
    #Setup databank variable
    databank = {'searchKeywords': searchKeywords}
        
    print('Web Scraping for Priors')
    print('Searching for keyword(s): ' + str(searchKeywords) + '\n')

###############################################################################
#1. Determine Functions
###############################################################################

#Create progress bar
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 30, fill = '█', printEnd = "\r"):
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
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#Searches for all links on given URL
def defineCategory(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    
    #Create filename to save to
    saveKeywords = '_'.join(searchKeywords) #Create string of keywords for file name
    saveName = 'operations_' + saveKeywords + '.txt' #Create file name

    #Save search parameters to file
    with open(os.path.dirname(__file__) + '/../Data/'+saveName, 'w') as f: #Open file to be saved to
        _ = f.write('#CATEGORIES: ' + str(searchKeywords) + '\n') #Save title to file
        _ = f.write('#--------------------#\n\n') #Add separator to file

    #Pack databank
    databank['saveName'] = saveName
    
    return databank

def scrapeLinks(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''        
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    
    #Define internal functions
    def searchLinks(URL):
        '''
        [INSERT FUNCTION DESCRIPTION]
        
        '''
        webText = requests.get(URL).text #Download URL content
        soup = BeautifulSoup(webText, 'html.parser') #Create soup object
        bodyText = soup.find("div",{"id":"mw-content-text"}) #Isolate the body content
        bodyLinks = bodyText.find_all('a', href=True, class_=False, dir=False) #Find all links in body
        currentLinks = [link.get('href') for link in bodyLinks] #Extract links from list
        
        return currentLinks

    #Removes any duplicate or unwanted links
    def removeLinks(databank):
        '''
        [INSERT FUNCTION DESCRIPTION]
        
        '''
        #Unpack databank
        expandedLinks = databank['expandedLinks']
        
        #Assess links
        seen = set() #Create set
        seen_add = seen.add #For optimization
        uniqueLinks = [x for x in expandedLinks if not (x in seen or seen_add(x))] #Remove duplicates
        pageLinks = [x for x in uniqueLinks if 'Category:' not in x] #Remove unwanted #cite links
        keptLinks = [x for x in pageLinks if '#cite' not in x] #Remove unwanted #cite links
        
        #Pack databank
        databank['links'] = keptLinks
        
        return databank
    
    #Create empty list to be populated
    links = []

    #Iterate through keywords, grabbing links from each page
    links.extend([searchLinks('https://en.wikipedia.org/wiki/Category:' + str(keyword)) for keyword in databank['searchKeywords']]) 

    #Concatenate the lists from each keyword
    expandedLinks = [item for sublist in links for item in sublist] 
    databank['expandedLinks'] = expandedLinks

    #Remove any duplicates and unwated lists
    databank = removeLinks(databank)
    
    return databank

def extractLinks(database):
    
    '''
    [INSERT FUNCTION DESCRIPTION]
        
    '''
    #Unpack databank
    links = database['links']
    saveName = database['saveName']

    #Setup variables
    numberEquations = 0 #Initiate equation count
    fullInitial = time.time() #Initiate timing for entire process
    segmentInitial = time.time() #Initiate timing for each segment
    for linkIndex, link in enumerate(links):
        #Progress bar
        printProgressBar(linkIndex, len(links)-1)
        
        #First, add page links to link list
        if link: #Only run if link exists
            
            #Display metrics for every 10 links scraped
            if ((linkIndex%10) == 0) & (__name__ == '__main__'):
                print('Current Link: ' + 'https://en.wikipedia.org/' + link)
                print('Current Link Index: ' + str(linkIndex))
                print('Total Number of Links: ' + str(len(links)))
                print('Current Percentage Complete: ' + str(round((linkIndex/len(links)*100),4)) + '%')
            
            #Download webpage
            linkText = requests.get('https://en.wikipedia.org/' + link).text
            
            #Scan all equations on this page
            equations = []
            
            #Begin by searching for math tags
            mathTag = 1
            equationSoup = BeautifulSoup(linkText, 'html.parser', parse_only = SoupStrainer('math',{'xmlns':'http://www.w3.org/1998/Math/MathML'}))
            equations = equationSoup.find_all('math',{'xmlns':'http://www.w3.org/1998/Math/MathML'})

            #Save equations to a file
            if equations: #If equations exist on this page
                with open(os.path.dirname(__file__) + '/../Data/'+saveName, 'a') as f: #Open file to be saved to
                    titleSoup = BeautifulSoup(linkText, 'html.parser', parse_only = SoupStrainer('h1')) #Extract title of page
                    root = titleSoup.find('h1').text #Convert title to be saved
                    _ = f.write('#ROOT: ' + root + '\n') #Save title to file
                    _ = f.write('#LINK: '+ link + '\n') #Save link to file
                    if mathTag:
                        _ = [f.write(currentEquation['alttext'] + '\n') for currentEquation in equations] #Save all equations to file
                    else:
                        _ = [f.write(currentEquation['alt'] + '\n') for currentEquation in equations] #Save all equations to file
                    _ = f.write('#--------------------#\n\n') #Add separator to file
                numberEquations += len(equations) #Increase equation count for metric report
                    
            #Display metrics for every 10 links scraped 
            if ((linkIndex%10) == 0) & (__name__ == '__main__'):
                print('Total Equations Added: ' + str(numberEquations))
                print('Time Since Last Report: ' + str(round(time.time()-segmentInitial,2)) + ' seconds')
                print('----------------------------------------')
                segmentInitial = time.time() #Reset timer
            
    print('Web Scraping Complete in ' +str(round(time.time()-fullInitial,2)) + ' seconds!')

###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    ###############################################################################
    #2. User Inputs - Determine Which Category Pages to Scrape
    ###############################################################################

    databank = defineCategory(databank)

    ###############################################################################
    #3. Determine all links to be scraped
    ###############################################################################

    databank = scrapeLinks(databank)

    ###############################################################################
    #4. Extract and Save Equations from Each Link
    ###############################################################################

    extractLinks(databank)