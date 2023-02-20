# webscrapingPriors

The goal of this project is to determine a distribution of mathematical operation priors to help computational models such as Differentiable Architecture Search. These models link predictors to outcome via a mathematical equation.

Specifically, the project scrapes wikipedia pages of a certain category to extract mathematical equations and then determines the distribution of operations contained within them. 

This project contains three main files:

-webScrapingSearch.py: Extracts equations from Wikipedia,

-sympyParsing.py: Determines operation distributions from the extracted equations,

-plotParsedEquations.py: Pots the distribution of operations as a pie chart.
