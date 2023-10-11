
# The Main Function

## `scrape_and_parse_equations()`

Let's begin with the main function that scrapes Wikipedia, parses the equations, and derives priors all at once. We will use the `scrape_and_parse_equations()` function to scrape a category page using the `Super` tag.

```
from equation_scraper import scrape_and_parse_equations

scrape_and_parse_equations(['Super:Cognitive_psychology'])
```

All data produced will be stored in a `data` folder at your current working directory. If this folder does not exists, the package will create it for you. Each search is further organized by creating its own specific sub-folder named after your keywords, separated by underscores. For example `[Super:Cognitive_psychology, Neuroscience]` would create the folder `SUPERCognitivePsychology_Neuroscience` within the `data` folder. Note, keywords using the `Direct:` tag are not included in this filename nomenclature.

If you repeat the exact same search, this folder is first deleted and then rebuilt with the new search. After running this function, you will notice a series of files, as well as a `debug` folder with more files, but we will explain what each file does in the next section of the tutorial when running each of the two sub-functions individually.

An example structure when using the keywords `['Cognitive_psychology']` would be:
```
data
|
└───CognitivePsychology
    │   equations_CognitivePsychology.txt
    │   priors_CognitivePsychology.pkl
    |   parsed_equations_CognitivePsychology.txt
    |   (optional) figure_CognitivePsychology.png
    |
    └───debug
        │   debug_parsed_CognitivePsychology.txt
        │   skipped_equations_CognitivePsychology.txt
        │   wordsRemoved_equations_CognitivePsychology.txt
```

# The Sub-Functions 

## `scrape_equations()`

The `scrape_equations()` function searches Wikipedia and derives a list of equations to be parsed.

```
from equation_scraper import scrape_equations

scrape_equations(['Super:Cognitive_psychology', 'Neuroscience'])
```

This function produces a single file: `equations_*.txt` where `*` corresponds to the keywords you searched for (i.e., the name of the search's sub-folder), for example: `equations_SUPERCognitivePsychology_Neuroscience.txt` in the case of the example code above. The first line of this file lists meta-data of the keywords used for the search (e.g., `#CATEGORIES: ['Super:Cognitive_Psychology', 'Neuroscience]`). After this, you will see a pattern of each Wikipedia page scraped that looks like this:
<hr>


`#ROOT: Biological Motion Perception` <br>
`#LINK: /wiki/`<wbr>`Biological_motion_perception`<br>
`{\displaystyle \nu _{\psi }(t)={\frac {R_{\psi }(t)-{\bar {R}}}{\bar {R}}}}`<br>
`{\displaystyle o_{l}(x)={\sqrt {max(g_{p}(x_{i}))max(g_{r}(x_{j}))}}}`
<hr>

- `#ROOT` is the title of the corresponding Wikipedia page
- `#LINK` is the Wikipedia URL without the  `https://en.wikipedia.org` prefix
 - e.g., `/wiki/`<wbr>`Biological_motion_perception` can be used as `https://en.wikipedia.org/wiki/Biological_motion_perception`
- Everything after this is a scraped equation. The format of these equations has not been modified in any way up to this point, so these are exactly as they were scraped from Wikipedia. For example, from the above example, the equations are:
 - `{\displaystyle \nu _{\psi }(t)={\frac {R_{\psi }(t)-{\bar {R}}}{\bar {R}}}}`
 - `{\displaystyle o_{l}(x)={\sqrt {max(g_{p}(x_{i}))max(g_{r}(x_{j}))}}}`

## `parse_equations()`

The `parse_equations()` function then loads the `equations_*.txt` file written from the previous function and iterates through the equations where it parses their operators and functions and builds priors. Running this function still requires that you pass the same keywords as with the previous function because it uses these to determine which folder the data is saved into.

```
from equation_scraper import parse_equations

parse_equations(['Super:Cognitive_psychology', 'Neuroscience'])
```

The main file produced by this function is the `priors_*.pkl` file where `*` corresponds to the keywords you searched for (i.e., the name of the search's sub-folder), for example: `priors_SUPERCognitivePsychology_Neuroscience.pkl`. We look into this file in detail in the `Priors` section of our documentation. The other file that this function produces is the `parsed_equations_*.txt` file, which includes the parsing results per equation.

Additionally, there are three files within the debug folder: `debug_parsed_*.txt`, `skipped_equations_*.txt`, `wordsRemoved_equations_*.txt`.


- `debug_parsed_*.txt` presents the same information as `parsed_equations_*.txt` but with a different organization structure.

- `skipped_equations_*.txt` presents all equations discarded and not used for priors (these are most often discarded because they are not actual expressions, such as with a variable decleration in text, e.g., "`v` *is our first indepenent variable*").

- `wordsRemoved_equations_*.txt` is a list of words that were turned into variables---this occurs when equations contain words to represent a single variable, for example: `WEIGHT = HEIGHT * c` would be transformed to `y = x * c` and the words `WEIGHT` and `HEIGHT` would be added to this list.

# Other Functions

## `plot_prior()`

The `plot_prior()` function will produce a figure---`figure_*.png`--- that is a barplot of the frequencies of operators/functions. It uses the same keywords as the aforementioned functions. The `scrape_and_parse_equations()` function also automatically runs this function after it has scraped and parsed the equations from your keywords list.

```
from equation_scraper import plot_prior

plot_prior(['Super:Cognitive_psychology', 'Neuroscience'])
```

## `load_prior()`

The `load_prior()` function will allow you to load the pickle file containing the prior information either using the same keywords as all aforementioned functions:<br>
`es_priors = load_prior(['Super:Cognitive_psychology', 'Neuroscience'])`
<br><br>
or with a point-and-click interface if no inputs are given to the function: <br>
`es_priors = load_prior()`
<br><br>
This is the only function that returns a variable, and this variable will contain metadata and the priors. Again, see the Priors section of our documentation for an in depth look of this file.

```
from equation_scraper import load_prior

es_priors = load_prior(['Super:Cognitive_psychology', 'Neuroscience'])

#Print prior information
print('**********METADATA**********\n')
for key in es_priors['metadata'].keys():
    print(f"{key}: {es_priors['metadata'][key]}")

print('\n***********PRIORS***********\n')
for key in es_priors['priors'].keys():
    print(f"{key}: {es_priors['priors'][key]}")
```