'''
Environment info

pip install matplotlib
'''

import os
import matplotlib.pyplot as plt
import numpy as np 

operationsFilename = 'parsed_operationsNamed_Psychophysics.txt'
with open(operationsFilename,'r') as f:
    parsedEqs = f.readlines()
    
allOps = {}
mx = []
for parsedEq in parsedEqs:
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
    if allOps[key] < round(np.sum(list(allOps.values()))*.03):
        plotOps['Other'] += allOps[key]
        otherKeys.append(key)
    else:
        plotOps[key] = allOps[key]
if plotOps['Other'] == 0:
    del plotOps['Other']

if 'MUL' in plotOps:
    plotOps['Multiplication'] = plotOps['MUL']
    del plotOps['MUL']

if 'DIV' in plotOps:
    plotOps['Division'] = plotOps['DIV']
    del plotOps['DIV']    
    
if 'ADD' in plotOps:
    plotOps['Addition'] = plotOps['ADD']
    del plotOps['ADD'] 
       
if 'SUB' in plotOps:
    plotOps['Subtraction'] = plotOps['SUB']
    del plotOps['SUB']  
      
if 'POW' in plotOps:
    plotOps['Power'] = plotOps['POW']
    del plotOps['POW']    
    
if 'NEG' in plotOps:
    plotOps['Negative'] = plotOps['NEG']
    del plotOps['NEG']    
  
if 'COS' in plotOps:
    plotOps['Cosine'] = plotOps['COS']
    del plotOps['COS']   

if 'SIN' in plotOps:
    plotOps['Sine'] = plotOps['SIN']
    del plotOps['SIN']   
    
if 'DERIVATIVE' in plotOps:
    plotOps['Derivative'] = plotOps['DERIVATIVE']
    del plotOps['DERIVATIVE']    
    
if 'LOG' in plotOps:
    plotOps['Logarithm'] = plotOps['LOG']
    del plotOps['LOG']  
    del plotOps['EXP'] #We also remove EXP because a natural logarithm in sympy is represented as both LOG and EXP
    
####PLOTTING    
fig, ax = plt.subplots(figsize=(14, 8), subplot_kw=dict(aspect="equal"))
wedges, texts = ax.pie(plotOps.values(), startangle=-40, colors = plt.get_cmap("Pastel1")(np.linspace(0.0, 1, len(plotOps.keys()))))
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
kw = dict(arrowprops=dict(arrowstyle="-"),
          bbox=bbox_props, zorder=0, va="center")
plt.title('Category:\n' + operationsFilename.split('_')[-1].split('.')[0], loc='left', fontsize = 20)

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