###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

#Import modules
import sys
from Functions.webScrapingSearch import *
from Functions.sympyParsing import *
from Functions.reportPriors import *

#Determine categories to search
if len(sys.argv) > 1:
    searchKeywords = sys.argv[1:]
else:
    searchKeywords = ['Super:Cognitive_psychology', 'Super:Cognitive_neuroscience']
    
#Setup databank variable
databank = {'searchKeywords': searchKeywords}
    
print('Web Scraping for Priors')
print('Searching for keyword(s): ' + str(searchKeywords) + '\n')

###############################################################################
#1. webScrapingSearch.py
###############################################################################

print("Scraping Wikipedia...")

databank = defineCategory(databank)
databank = scrapeLinks(databank)
extractLinks(databank)

###############################################################################
#2. sympyParsing.py
###############################################################################

print("\nParsing Equations...")

databank = loadScrapedData(databank)
databank = cycleEquations(databank)
databank = parseEquations(databank)
saveFiles(databank) 

print("Parsing Complete...")