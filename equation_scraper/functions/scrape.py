###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

from bs4 import BeautifulSoup, SoupStrainer
from pip._vendor import requests
import time
import os
import shutil
import sys
from tqdm import tqdm

###############################################################################
#1. Determine Functions
###############################################################################

#Define main function
def scrape_equations(keywords: list = None):
    databank = _define_search(keywords)
    if databank['searchKeywords']:
        databank = _define_category(databank)
        databank = _scrape_links(databank)
        _extract_links(databank)
    else:
        print('No search keywords were provided.\n')

#Define keywords
def _define_search(keywords: list = None):
    if keywords is not None:
        searchKeywords = keywords
    elif len(sys.argv) > 1:
        searchKeywords = sys.argv[1:]
    else:
        searchKeywords = []

    #Setup databank variable
    databank = {'searchKeywords': searchKeywords}

    if databank['searchKeywords'] and not os.path.isdir('data'):
            os.mkdir('data')
            print(f"Creating a 'data' directory to hold the results in your current directory: {os. getcwd()}")
        
    print('Searching for keyword(s): ' + str(searchKeywords) + '\n')

    return databank

#Searches for all links on given URL
def _define_category(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    #Unpack databank
    searchKeywords = databank['searchKeywords']
    
    #Setup variables
    normalKeywords = []
    superKeywords = []
    directKeywords = []
    
    #Split super categories from normal categories
    for keyIndex, searchKeyword in enumerate(searchKeywords):
        if 'Super:' in searchKeyword:
            superKeywords.append(searchKeyword.replace('Super:',''))
        elif 'Direct:' in searchKeyword:
            directKeywords.append(searchKeyword.replace('Direct:',''))
        else:
            normalKeywords.append(searchKeyword)
        
        if len(searchKeyword.split('_')) > 1: #If the keyword has two words and thus is split by an underscore
            searchKeywords[keyIndex] = searchKeyword.split('_')[0] + '_' + searchKeyword.split('_')[1][0].capitalize() + searchKeyword.split('_')[1][1:] #Capitalize the second word
    
    #Remove directs
    searchKeywords = [searchKeyword for searchKeyword in searchKeywords if 'Direct' not in searchKeyword]
    
    #Create filename to save to, including the creation of folders to store it in
    saveKeywords = '~'.join(searchKeywords).replace('Super:','SUPER').replace('_','').replace('~','_') #Create string of keywords for file name
    savePath = saveKeywords.replace('Super:','SUPER') +'/'
    if searchKeywords:
        if os.path.exists('./data/'+savePath):
            shutil.rmtree('./data/'+savePath) #Remove old scraping

        os.makedirs('./data/'+savePath)
        os.makedirs('./data/'+savePath+'debug/')
    saveName = 'equations_' + saveKeywords + '.txt' #Create file name

    if searchKeywords:
        #Save search parameters to file
        with open('data/'+savePath+saveName, 'w', encoding="utf-8") as f: #Open file to be saved to
            _ = f.write('#CATEGORIES: ' + str(searchKeywords) + '\n') #Save title to file
            _ = f.write('#--------------------#\n\n') #Add separator to file

    #Pack databank
    databank['savePath'] = savePath
    databank['saveName'] = saveName
    
    databank['normalKeywords'] = normalKeywords 
    databank['superKeywords'] = superKeywords
    databank['directKeywords'] = directKeywords
    databank['searchKeywords'] = searchKeywords
    
    return databank

def _scrape_links(databank):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''        
    #Unpack databank
    normalKeywords = databank['normalKeywords']
    superKeywords = databank['superKeywords']
    directKeywords = databank['directKeywords']
    
    #Define internal functions
    def _search_links(URL):
        '''
        [INSERT FUNCTION DESCRIPTION]
        
        '''
        webText = requests.get(URL).text #Download URL content
        soup = BeautifulSoup(webText, 'html.parser') #Create soup object
        bodyText = soup.find("div",{"id":"mw-content-text"}) #Isolate the body content
        bodyLinks = bodyText.find_all('a', href=True, class_=False, dir=False) #Find all links in body
        currentLinks = [link.get('href') for link in bodyLinks] #Extract links from list
        
        return currentLinks
    
    def _search_super_links(URL):
        '''
        [INSERT FUNCTION DESCRIPTION]
        
        '''
        #Setup variable
        currentLinks = []

        #Scrape URL
        webText = requests.get(URL).text #Download URL content
        soup = BeautifulSoup(webText, 'html.parser') #Create soup object
        categoryText = soup.find_all("div",{"class":"mw-category-generated"}) #Isolate the sub-category section

        #Retrieve subcategory links from supercategory
        subCategoryLinks = categoryText[0].find_all('a', href=True, class_=False, dir=False) #Find all links in body
        for subCategory in subCategoryLinks: #Cycle through subcategories
            if 'Category:' in subCategory.get('href'):
                subWebText = requests.get('https://en.wikipedia.org'+subCategory.get('href')).text #Download URL content
                subSoup = BeautifulSoup(subWebText, 'html.parser') #Create soup object
                subCatText = subSoup.find_all("div",{"class":"mw-category-generated"}) #Retrieve direct links from supercategory
                subLinks = subCatText[0].find_all('a', href=True, class_=False, dir=False) #Find all links in body   
                currentLinks.extend([link.get('href') for link in subLinks if 'Category:' not in link.get('href')]) #Extract links from list
            else: #Retrieve direct links from supercategory      
                currentLinks.append(subCategory.get('href')) #Extract links from list
                
        return currentLinks
    
    #Removes any duplicate or unwanted links
    def _remove_links(databank):
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
    allLinks = []
    superLinks = []
    directLinks = []
    normalLinks = []
    links = []

    #Iterate through (Super, Direct, and Normal) keywords, grabbing links from each page
    superLinks.extend([_search_super_links('https://en.wikipedia.org/wiki/Category:' + str(keyword)) for keyword in superKeywords])
    directLinks.extend([_search_super_links(str(keyword)) for keyword in directKeywords])
    normalLinks.extend([_search_links('https://en.wikipedia.org/wiki/Category:' + str(keyword)) for keyword in normalKeywords]) 
     
    #Combine the two outputs
    links.append(allLinks)
    links.extend(superLinks)
    links.extend(directLinks)
    links.extend(normalLinks)

    #Concatenate the lists from each keyword
    expandedLinks = [item for sublist in links for item in sublist] 
    databank['expandedLinks'] = expandedLinks

    #Remove any duplicates and unwated lists
    databank = _remove_links(databank)
    
    return databank

def _extract_links(databank):
    
    '''
    [INSERT FUNCTION DESCRIPTION]
        
    '''
    #Unpack databank
    links = databank['links']
    savePath = databank['savePath']
    saveName = databank['saveName']

    #Setup variables
    numberEquations = 0 #Initiate equation count
    fullInitial = time.time() #Initiate timing for entire process
    for link in tqdm(links):
        
        #First, add page links to link list
        if link: #Only run if link exists
            
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
                with open('data/'+savePath+saveName, 'a', encoding="utf-8") as f: #Open file to be saved to
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
            
    print('Web Scraping Complete in ' +str(round(time.time()-fullInitial,2)) + ' seconds!')

###############################################################################
## IF SCRIPT WAS EXECUTED DIRECTLY:                                          ##
###############################################################################

if __name__ == '__main__':
    scrape_equations()
