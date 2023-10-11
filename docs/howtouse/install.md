
# Installing equation-scraper

## <b>Pre-Requisites</b>

The only prerequisites for installing `equation-scraper` is [Python](https://www.python.org/downloads/).

---

## <b>Install With Pip</b>

To install using [pip](https://pip.pypa.io/en/stable/cli/pip_download/):<br>

&emsp;&emsp;```pip install equation-scraper```

You can then import the package functions directly:

- <i>Import functions:</i> ```from equation_scraper import scrape_and_parse_equations, scrape_equations, parse_equations, plot_prior, load_prior```<br>
- <i>Use function:</i> ```scrape_and_parse_equations(['Cognitive_psychology'])```

Or indirectly: 

- <i>Import package:</i> ```import equation_scraper as es```<br>
- <i>Use function:</i> ```es.scrape_and_parse_equations(['Cognitive_psychology'])```

<i>If you prefer, follow this [link](https://pypi.org/project/equation-scraper/){.new_tab} to our PyPI page to directly download wheels or source.</i>

---

## <b>Installing From the Source</b>
You can install the latest GitHub version of `equation-scraper` into your environment:<br>

&emsp;&emsp;```pip install git+https://github.com/AutoResearch/equation-scraper```

---

## <b>Obtaining the Source</b>
If you rather download the package via GitHub you can use the following command:<br>

&emsp;&emsp;```git clone https://github.com/AutoResearch/equation-scraper.git```

To update your local package:

&emsp;&emsp;```git pull```

---

## <b>Dependencies</b>
The following are the required dependencies for `equation-scraper`. If you install `equation-scraper` via pip, or installed `equation-scraper` from the source, these are automatically installed. If you have obtained the package from the source you can install these via the pyproject.toml file ```pip install .```


&emsp;&emsp;[Beautiful Soup 4](https://pypi.org/project/beautifulsoup4/){.new_tab}~=4.11.2<br>
&emsp;&emsp;[Requests](https://pypi.org/project/requests/){.new_tab}~=2.28.2<br>
&emsp;&emsp;[Sympy](https://pypi.org/project/sympy/){.new_tab}~=1.11.1<br>
&emsp;&emsp;[ANTLR](https://pypi.org/project/antlr4-python3-runtime/){.new_tab}==4.10<br>
&emsp;&emsp;[Equation-Tree](https://pypi.org/project/equation-tree/){.new_tab}~=0.0.25<br>
&emsp;&emsp;[Matplotlib](https://pypi.org/project/matplotlib/){.new_tab}~=3.6.3<br>
&emsp;&emsp;[Numpy](https://pypi.org/project/numpy/){.new_tab}~=1.24.2<br>
&emsp;&emsp;[tqdm](https://pypi.org/project/tqdm/){.new_tab}~=4.65.0<br>
