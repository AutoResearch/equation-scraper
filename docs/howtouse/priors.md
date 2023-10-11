# Priors

The priors pickle file, `priors_*.pkl` is loaded as a dictionary with two sub-dictionaries, `metadata` and `priors`. The priors that are stored in the `priors` sub-dictionary are built using the [`equation-tree package`](https://pypi.org/project/equation-tree/0.0.1/). We will give brief definitions of the information stored in this sub-dictionary, but for a detailed look see the `equation-tree` package documentation. It is important to note that the `equation-tree` package uses binary expression trees where operators (e.g., `+`) have two inputs and functions  (e.g., `sin`) have one input. For example, the expression `m*x+b*sin(y)` could be represented as:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`+`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\ <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`*`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`*` <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;\ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;\ <br>
&nbsp;&nbsp;&nbsp;`m`&nbsp;&nbsp;&nbsp;&nbsp;`x`&nbsp;&nbsp;&nbsp;&nbsp;`b`&nbsp;&nbsp;`sin`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`y`<br>

<hr>

The full structure of the pickle file looks like this:

```
es_priors  
│  
└───metadata 
│   │   number_of_equations:  The number of parsed equations 
│   │   unparsed_equations: The number of equations that failed to parse 
│   │   list_of_operators:  The list of operators considered when parsing equations and building piors 
│   │   list_of_functions: The list of functions considered when parsing equations and building piors 
│   │   list_of_constants: The list of words/symbols representing constants when parsing equations and building piors 
│   │   list_of_equations: The list of each parsed equation 
│     
└───priors 
    │   max_depth: The frequency of number of nodes (operators, functions, constants, & variables) in the expression tree 
    │   depth:  The frequency of node layers in the expression tree 
    │   structures: The list of expression tree structures across equations 
    │   features:    The number of constants and variables across equations*  
    │   functions: Frequency count of each function across equations 
    │   operators:  Frequency count of each operator across equations 
    │   operator_and_functions: Frequency count of each function and operator across equations 
    │   function_conditionals: Frequency count of conditional functions across equations 
    │   operator_conditionals: Frequency count of conditional operators across equations 
```
\**Note that the constant and variable counts are difficult to extract when scraping Wikipedia and so these values are likely incorrect - use with caution*