import json
import requests
import os
import re


def scrape_scopus(query, n):
    '''
    get research papers for a query (n is not the number of papers, but the number of 'tries' to get a paper.)
    '''

    # make pretty name for entry in checkpoint
    regex = re.compile('[^a-zA-Z]')
    name = regex.sub('', query)
    # loads meta data for the query into a file, so already searched papers from previous sessions don't
    # get searched again

    with open('checkpoint.json', 'r') as file:
        stored = json.load(file)
    if name in stored:
        start = stored[name]['start']
        k = stored[name]['k']
    else:
        start = 0
        k = 0
    end = start + n

    # make a path to store the articles
    path = f'{os.path.dirname(__file__)}/articles/{name}'
    if not os.path.exists(path):
        os.mkdir(path)

    # start scraping
    print(f'scraping with query: {query}, starting: {start}, ending: {end}')
    for i in range(start, end, 25):
        # get meta data for the query
        print('.', end='')

        # one can create a api key on elsevier.com
        params = {
            "query": query,
            "apiKey": '001a83f828feb57ccaca2272a6921eca',
            'start': i
        }

        params_key = {
            "apiKey": '001a83f828feb57ccaca2272a6921eca'
        }

        response = requests.get("https://api.elsevier.com/content/search/scopus", params=params)

        for j in range(0, 25):
            try:
                # get the doi of the papers
                doi = response.json()['search-results']['entry'][j]['prism:doi']

                # get the paper
                url_2 = f"https://api.elsevier.com/content/article/doi/{doi}?view=FULL"

                response_2 = requests.get(url_2, params=params_key)
                text = response_2.text

                # if no error, store the paper in the directory
                if not text.startswith('<service-error>'):
                    with open(f'{path}/{k}.xml', 'w') as file:
                        file.write(text)
                        k += 1
            except:
                pass

    # store the new "start" and "k" in the meta file, so we start from there next time scraping
    stored[name] = {'start': end, 'k': k}

    with open('checkpoint.json', 'w') as file:
        json.dump(stored, file)


if __name__ == '__main__':
    scrape_scopus('psychology', 100)
