###############################################################################
## Written by Chad C. Williams, 2022                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

'''
Environment Info

py -m venv webScrapingEnv
.\webScrapingEnv\Scripts\activate

pip install beautifulsoup4
pip install lxml
pip install requests

Note: There exists a requirements.txt file
'''

###############################################################################
#0. User Inputs - Determine Which Category Pages to Scrape
###############################################################################

searchKeywords = ['Psychophysics'] #User defined category pages to scrape

#Create filename to save to
saveKeywords = '_'.join(searchKeywords) #Create string of keywords for file name
saveName = 'operationsNamed_' + saveKeywords + '.txt' #Create file name

#Save search parameters to file
with open('Data/'+saveName, 'a') as f: #Open file to be saved to
    _ = f.write('#CATEGORIES: ' + str(searchKeywords) + '\n') #Save title to file
    _ = f.write('#--------------------#\n\n') #Add separator to file

###############################################################################
#1. Import Modules
###############################################################################

from bs4 import BeautifulSoup, SoupStrainer
from pip._vendor import requests
import time

###############################################################################
#2. Determine Functions
###############################################################################

#Searches for all links on given URL
def searchLinks(URL):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    webText = requests.get(URL).text #Download URL content
    soup = BeautifulSoup(webText, 'lxml') #Create soup object
    bodyText = soup.find("div",{"id":"mw-content-text"}) #Isolate the body content
    bodyLinks = bodyText.find_all('a', href=True, class_=False, dir=False) #Find all links in body
    currentLinks = [link.get('href') for link in bodyLinks] #Extract links from list
    return currentLinks

#Removes any duplicate or unwanted links
def removeLinks(listOfInterest):
    '''
    [INSERT FUNCTION DESCRIPTION]
    
    '''
    seen = set() #Create set
    seen_add = seen.add #For optimization
    uniqueLinks = [x for x in listOfInterest if not (x in seen or seen_add(x))] #Remove duplicates
    pageLinks = [x for x in uniqueLinks if 'Category:' not in x] #Remove unwanted #cite links
    keptLinks = [x for x in pageLinks if '#cite' not in x] #Remove unwanted #cite links
    return keptLinks

###############################################################################
#3. Determine all links to be scraped
###############################################################################

#Create empty list to be populated
links = []

#Iterate through keywords, grabbing links from each page
links.extend([searchLinks('https://en.wikipedia.org/wiki/Category:' + str(keyword)) for keyword in searchKeywords]) 

#Concatenate the lists from each keyword
expandedLinks = [item for sublist in links for item in sublist] 

#Remove any duplicates and unwated lists
links = removeLinks(expandedLinks)

###############################################################################
#4. Extract and Save Equations from Each Link
###############################################################################

numberEquations = 0 #Initiate equation count
fullInitial = time.time() #Initiate timing for entire process
segmentInitial = time.time() #Initiate timing for each segment
for linkIndex, link in enumerate(links):
    #First, add page links to link list
    if link: #Only run if link exists
        
        #Display metrics for every 10 links scraped
        if linkIndex%10 == 0:
            print('Current Link: ' + 'https://en.wikipedia.org/' + link)
            print('Current Link Index: ' + str(linkIndex))
            print('Total Number of Links: ' + str(len(links)))
            print('Current Percentage Complete: ' + str(round((linkIndex/len(links)*100),4)) + '%')
        
        #Download webpage
        linkText = requests.get('https://en.wikipedia.org/' + link).text
        
        #Create Soup Object
        categorySoup = BeautifulSoup(linkText, 'lxml', parse_only = SoupStrainer("div",{"id":"mw-normal-catlinks"}))
        
        #Scan all equations on this page
        equations = []
        
        #Begin by searching for math tags
        mathTag = 1
        equationSoup = BeautifulSoup(linkText, 'lxml', parse_only = SoupStrainer('math',{'xmlns':'http://www.w3.org/1998/Math/MathML'}))
        equations = equationSoup.find_all('math',{'xmlns':'http://www.w3.org/1998/Math/MathML'})

        #Save equations to a file
        if equations: #If equations exist on this page
            with open('Data/'+saveName, 'a') as f: #Open file to be saved to
                titleSoup = BeautifulSoup(linkText, 'lxml', parse_only = SoupStrainer('h1')) #Extract title of page
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
        if linkIndex%10 == 0: 
            print('Total Equations Added: ' + str(numberEquations))
            print('Time Since Last Report: ' + str(round(time.time()-segmentInitial,2)) + ' seconds')
            print('----------------------------------------')
            segmentInitial = time.time() #Reset timer
            
print('Web Scraping Complete in ' +str(round(time.time()-fullInitial,2)) + ' seconds!')