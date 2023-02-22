# webscrapingPriors

The goal of this project is to determine a distribution of mathematical operation priors to help computational models such as Differentiable Architecture Search. These models link predictors to outcome via a mathematical equation.

Specifically, the project scrapes wikipedia pages of a certain category to extract mathematical equations and then determines the distribution of operations contained within them. 

## There exists a main file:
-webScraping_main.py: Which run's the three function files consecutively using the same keywords.

## This project contains three main function files:

-webScrapingSearch.py: Extracts equations from Wikipedia,

-sympyParsing.py: Determines operation distributions from the extracted equations,

-plotParsedEquations.py: Pots the distribution of operations as a pie chart.

## How to use this package:
The package is executable through terminal where you run the file normally and any provided arguments (space separated) will be taken as the keywords to search for:
```
python webScraping_main.py Psychophysics Economics
```
The function files can be run through the main script, but also function if run directly:
```
python webScrapingSearch.py Psychophysics Economics
```
Note, however, that each consecutive function script relies on a text file created by the last. So, to run sympyParsing.py you must first have gotten a file created by webScrapingSearch.py and so forth. The intent of making these function scripts discrete and themselves executable is so that you can work on one stage of the project without having to wait for the other stages. For example, you can continuously run sympyParsing.py without having to re-scrape wikipedia with webScrapingSearch.py each time. I suppose this is more for development reasons (e.g., debugging or expanding the code). 
