# Functions

## Defined

The `equation-scraper` has a main function, `scrape_and_parse_equations()`, that sequentially runs two sub-functions, `scrape_equations()` and `parse_equations()`. The two sub-functions 1) scrapes equations from Wikipedia---`scrape_equations()`, and 2) parses the equations and builds the priors---`parse_equations()`. If running the sub-functions directly, they must be run sequentially because `parse_equations()` uses files produced from `scrape_equations()`.

## Keywords

All three of these functions take the same input: a list of keywords to search for. For example, `['Cognitive_psychology', 'Cognitive_science', 'Neuroscience']`, where the keywords are the Wikipedia topics you want scraped and parsed. These keywords must be Wikipedia [category pages](https://en.wikipedia.org/wiki/Help:Category). Further, the keywords you provide must be the end of the URL of the category you are looking to scrape (capitalization matters), i.e., everything following Wikipedia's `Category:` tag, such as https://<wbr>en.wikipedia.org/wiki/Category:**Cognitive_psychology**.

## Keyword Tags

You can use keyword tags to change the behaviour of the scraping function. Without using a tag---e.g., `Cognitive_psychology`--- the scraper will search for equations from all of the links from the corresponding wikipedia category page. Using the `Super:` tag---e.g.,
`Super:Cognitive_psychology`--- scrapes with a depth of two meaning that it will search all links within the corresponding category page, links within these links, and finally, links within these sublinks. For example, the first path of the `Cognitive_psychology` domain would be [Cognitive Psychology](https://en.wikipedia.org/wiki/Category:Cognitive_psychology) &rarr; [Cognitive Psychologists](https://en.wikipedia.org/wiki/Category:Cognitive_psychologists) &rarr; [American Cognitive Psychologists](https://en.wikipedia.org/wiki/Category:American_cognitive_psychologists). It then extracts equations from all levels of these links for parsing.
<br>
<br>
The final tag, `Direct:`, will search whichever URL you provide it, for example `Direct:https://en.wikipedia.org/wiki/Cognitive_psychology`, and does not assume a Wikipedia page. At this time, it only searches the first links in the same way as when not using a tag. The direct links do not need to be Wikipedia pages but the parsing was built around Wikipedia and direct links outside of Wikipedia has yet to be thoroughly tested.
<br>
<br>
You can mix these tags in your keywords, for example: `scrape_and_parse_equations(['Cognitive_psychology', 'Super:Cognitive_science', 'Direct:https://en.wikipedia.org/wiki/Neuroscience'])`
