import os
import matplotlib.pyplot as plt
import numpy as np 

os.chdir('C:/Users/cwill/Experiments/2022_WebScrapingPriors')
#eq = r"\sqrt{\frac{K+(4/3)\mu}{\rho}}"
operationsFilename = 'parsed_operationsNamed_Materials_science.txt'
with open(operationsFilename,'r') as f:
    parsedEqs = f.readlines()
    
allOps = {}
mx = []
for parsedEq in parsedEqs:
    if 'WIKIEQUATION' not in parsedEq:
        parsedOps = parsedEq.split('~')[1][1:-1].replace('\'','').split(',')
        if ('partial' in parsedEq.split('~')[3]) & ('DIV' in str(parsedOps)):
            for i, pO in enumerate(parsedOps):
                if 'DIV' in pO:
                    parsedOps[i] = 'DIV: '+str(int(pO.split(':')[1])-int(parsedEq.split('~')[3].count('partial')/2))
                    parsedOps.append('DERIVATIVE: ' + str(int(parsedEq.split('~')[3].count('partial')/2)))
                    break
        
        for parsedOp in parsedOps:
            if 'MUL' in parsedOp.split(':')[0]:
                mx.append(int((parsedOp.split(':')[1]).replace(' ','')))
            if ('FUNC' not in parsedOp.split(':')[0]) & ('NEG' not in parsedOp.split(':')[0]): #Skip functions
                try:
                    if parsedOp.split(':')[0].replace(' ','') in allOps.keys():
                        allOps[parsedOp.split(':')[0].replace(' ','')] += int((parsedOp.split(':')[1]).replace(' ',''))
                    else:
                        allOps[parsedOp.split(':')[0].replace(' ','')] = int((parsedOp.split(':')[1]).replace(' ',''))
                except:
                    pass

plotOps = {}
plotOps['Other'] = 0
otherKeys = []
for key in allOps.keys():
    if allOps[key] < 30:
        plotOps['Other'] += allOps[key]
        otherKeys.append(key)
    else:
        plotOps[key] = allOps[key]

if plotOps['MUL']:
    plotOps['Multiplication'] = plotOps['MUL']
    del plotOps['MUL']

if plotOps['DIV']:
    plotOps['Divide'] = plotOps['DIV']
    del plotOps['DIV']    
    
if plotOps['ADD']:
    plotOps['Addition'] = plotOps['ADD']
    del plotOps['ADD'] 
       
if plotOps['SUB']:
    plotOps['Subtraction'] = plotOps['SUB']
    del plotOps['SUB']  
      
if plotOps['POW']:
    plotOps['Power'] = plotOps['POW']
    del plotOps['POW']    
    
if plotOps['NEG']:
    plotOps['Negative'] = plotOps['NEG']
    del plotOps['NEG']    
  
if plotOps['COS']:
    plotOps['Cosine'] = plotOps['COS']
    del plotOps['COS']   

if plotOps['SIN']:
    plotOps['Sine'] = plotOps['SIN']
    del plotOps['SIN']   
    
if plotOps['DERIVATIVE']:
    plotOps['Derivative'] = plotOps['DERIVATIVE']
    del plotOps['DERIVATIVE']    
    
####PLOTTING    
fig, ax = plt.subplots(figsize=(14, 8), subplot_kw=dict(aspect="equal"))
wedges, texts = ax.pie(plotOps.values(), startangle=-40, colors = plt.get_cmap("Pastel1")(np.linspace(0.0, 1, len(plotOps.keys()))))
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
kw = dict(arrowprops=dict(arrowstyle="-"),
          bbox=bbox_props, zorder=0, va="center")

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    if (list(plotOps.keys())[i] == 'Derivative') | (list(plotOps.keys())[i] == 'Cosine'):
        ax.annotate(list(plotOps.keys())[i], xy=(x, y), xytext=(1.8*np.sign(x), 1.4*y), fontsize=18,
            horizontalalignment=horizontalalignment, **kw) 
    else:
        ax.annotate(list(plotOps.keys())[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), fontsize=18,
            horizontalalignment=horizontalalignment, **kw)

plt.savefig('Prior Parsing Pie Chart.png')
plt.show()