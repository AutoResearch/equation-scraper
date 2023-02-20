###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

###############################################################################
#0. Import Modules & Determine Keywords
###############################################################################

#Determine categories to search
import sys
if len(sys.argv) > 1:
    searchKeywords = sys.argv[1:]
else:
    searchKeywords = ['Psychophysics']
    
print('Web Scraping for Priors')
print('Searching for keyword(s): ' + str(searchKeywords) + '\n')

###############################################################################
#1. Scrape and Parse Categories
###############################################################################

#Complete the search
from Functions.webScrapingSearch import *
from Functions.sympyParsing import *
from Functions.plotParsedEquations import *

####

####
###############################################################################
#2. webScrapingSearch.py
###############################################################################

print("|---------------------|")
print("Scraping Wikipedia...")

saveName = defineCategory(searchKeywords)
links = scrapeLinks(searchKeywords)
extractLinks(links, saveName)

###############################################################################
#2. sympyParsing.py
###############################################################################

print("\n|---------------------|")
print("Parsing Equations...")

loadName, scrapedWiki = loadData(searchKeywords)
scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = cycleEquations(scrapedWiki)
parsedEquations = parseEquations(scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations)
saveFiles(loadName, parsedEquations, skippedEquations) 

print("Parsing Complete...")

###############################################################################
#2. plotParsedEquations.py
###############################################################################

print("\n|---------------------|")
print("Plotting Results...")

loadName, parsedEqs = loadData(searchKeywords)
allOps, opCounts = extractOperations(parsedEqs)
plotOps, plotCounts = reformatOperations(allOps, opCounts)
createFigure(plotOps, plotCounts, searchKeywords)
saveFigure(searchKeywords)

print("Results Plotted and saved.")