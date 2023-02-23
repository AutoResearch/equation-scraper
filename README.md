# webScrapingPriors

The goal of this project is to determine a distribution of mathematical operation as priors to help computational models such as Bayesian Symbolic Regression (BSR), Bayesian Machine Scientist (BMS), and Differentiable Architecture Search (DARTS). These models link predictors to outcome via a mathematical equation.

Specifically, the project scrapes wikipedia pages of a certain category to extract mathematical equations and then determines the distribution of operations contained within them. 

## There exists a main file:
-webScraping_main.py: Which runs the three function files consecutively using the same keywords. This will take you from scraping wikipedia to parsing the equations to plotting the distributions of equations all in one execution. 

## This project contains three function files:

-webScrapingSearch.py: Extracts equations from Wikipedia,

-sympyParsing.py: Determines operation distributions from the extracted equations,

-plotParsedEquations.py: Plots the distribution of operations as a pie chart.

## How to use this package:
The package is executable through terminal where you run the file normally and any provided arguments (space separated) will be taken as the category keywords to search for. This can come in two forms: Normal Categories and Super Categories. 

### Normal Category Keywords
Normal categories will scrape the pages linked to that category page and go no further (i.e., it takes one step from the category) - to provide normal category arguments, simply write them in plainly:
```
python webScraping_main.py Psychophysics Economics
```

### Super Category Keywords
Super categories will scrape the pages linked to that category page but also treat any subcategories on that page as normal category keywords (i.e., it takes two steps from the category) - to provide super category arguments, write them in with the 'Super:' preface:
```
python webScraping_main.py Super:Cognitive_psychology Super:Cognitive_neuroscience
```

### Hybrid Category Keywords
It is also possible to include both normal and super category keywords:
```
python webScraping_main.py Super:Cognitive_psychology Economics
```

### Running Main Versus Function Scripts
The main script will process your categories from scraping the web to plotting your distributions:
```
python webScraping_main.py Psychophysics Economics
```

However, it is also possible to run the function files directly:
```
python webScrapingSearch.py Psychophysics Economics
```
Note, however, that each consecutive function script relies on a text file created by the last. So, to run sympyParsing.py you must first have gotten a file created by webScrapingSearch.py and so forth. The intent of making these function scripts discrete and themselves executable is so that you can work on one stage of the project without having to wait for the other stages. For example, you can continuously run sympyParsing.py without having to re-scrape wikipedia with webScrapingSearch.py each time. I suppose this is more for development reasons (e.g., debugging or expanding the code). 
