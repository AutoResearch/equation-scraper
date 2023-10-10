###############################################################################
## Written by Chad C. Williams, 2023                                         ##
## www.chadcwilliams.com                                                     ##
###############################################################################

###############################################################################
#0. Import Modules
###############################################################################

#Import modules
from equation_scraper.functions.scrape import scrape_equations
from equation_scraper.functions.parse import parse_equations
from equation_scraper.functions.plot import plot_prior

def scrape_and_parse_equations(keywords: list = None):
    ###############################################################################
    #1. webScrapingSearch.py
    ###############################################################################

    print("**********************\n")
    print("Scraping equations...")
    scrape_equations(keywords)
    print("Scraping complete...")
    print("\n**********************")


    ###############################################################################
    #2. sympyParsing.py
    ###############################################################################

    print("**********************\n")
    print("Parsing equations...")
    parse_equations(keywords)
    print("Parsing complete...")
    print("\n**********************")

    ###############################################################################
    #2. plotPriors.py
    ###############################################################################

    print("**********************\n")
    print("\nPlotting priors...")
    plot_prior(keywords)
    print("Plotting complete...")
    print("\n**********************")

if __name__ == '__main__':
    scrape_and_parse_equations()
