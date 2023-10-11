# Overview

`equation_scraper` is a Python package that scrapes Wikipedia pages for mathematical equations and then parses the equations into its components to build prior distributions. Specifically, these priors include information such as the number of times an operator or function appears across all equations scraped. For example, the expression `m*x+b*sin(y)` would be parsed into the simple prior: `{*: 2, +: 1, sin: 1}`. The package includes much more information than this simple prior, for example conditional priors---a full breakdown of the included metrics is detailed on the `Priors` section of our documentation. The package was designed to provide equation discovery modelling techniques, such as Symbolic Regression and the Bayesian Machine Scientist, with informed priors; however, the application of this package can extend far beyond this.

# Equation-Scraper in Research

There are no current publications using the `equation-scraper`; however, we have two manuscripts currently under review. They are in a double-blind review process, so we are at this point refraining from sharing preprints, but will do so as soon as we are able.

# About

This project is in active development by the [Autonomous Empirical Research Group](https://musslick.github.io/AER_website/Research.html), led by [Sebastian Musslick](https://smusslick.com). The package was built by [Chad Williams](http://www.chadcwilliams.com). Furthermore, the package depends on another package of ours, `equation-tree`, which was developped by Younes Strittmatter and Ioana Marinescu.

This research program is supported by Schmidt Science Fellows, in partnership with the Rhodes Trust, as well as the Carney BRAINSTORM program at Brown University.


