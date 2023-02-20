###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

#TODO: Make variables a structure
#TODO: Delete files before writing

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

print("Scraping Wikipedia...")

saveName = defineCategory(searchKeywords)
links = scrapeLinks(searchKeywords)
extractLinks(links, saveName)

###############################################################################
#2. sympyParsing.py
###############################################################################

print("\nParsing Equations...")

loadName, scrapedWiki = loadScrapedData(searchKeywords)
scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations = cycleEquations(scrapedWiki)
parsedEquations = parseEquations(scrapedWikiEquations, scrapedLinks, scrapedEquations, skippedEquations)
saveFiles(loadName, parsedEquations, skippedEquations) 

print("Parsing Complete...")

###############################################################################
#2. plotParsedEquations.py
###############################################################################

print("\nPlotting Results...")

loadName, parsedEqs = loadParsedData(searchKeywords)
allOps, opCounts = extractOperations(parsedEqs)
plotOps, plotCounts = reformatOperations(allOps, opCounts)
createFigure(plotOps, plotCounts, searchKeywords)
saveFigure(searchKeywords)

print("Results Plotted and saved.")