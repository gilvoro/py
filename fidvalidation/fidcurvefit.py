import numpy as np
from scipy.optimize import curve_fit
import scipy

#function list, can be modified as needed
functions= [(lambda x, a, b: a+b*x, 0,'linear unweighted'),
            (lambda x, a, b: a+b*x, 1,'linear weighted to 1/x'),
            (lambda x, a, b, c: a+b*x+c*x**2, 1,'quadradic weighted to 1/x'),
            #(lambda x, a, b, c: a+b*x+c*x**2, 2,'quadradic weighted to 1/x**2')]
            #(lambda x, a, b: a+b*np.sqrt(abs(x)), 1,'squareroot of x weighted to 1/x'),
            #(lambda x, a, b: a + b*np.log(x), 1,'natrual log of x weighted to 1/x')]

#back calcs for linear
def backlin(y,a,b):
    return (y-a)/b

#back calcs for quad
def backquad(y,a,b,c):
    cterm = (a-y)
    dis = (b**2)- 4*c*cterm
    try:
        root = dis**0.5
    except:
        print 'square root of ' + str(dis) + ' is not a real number'
        print 'the value ' + str(y) + ' does not fall on this curve'
        return NaN
        
    dom = -b+root
    neu = 2*c
    return dom/neu

def backroot(y,a,b):
    base = (y-a)/b
    return base**2

def backnatural(y,a,b):
    base = (y-a)/b
    return np.exp(base)

backfuncdict = {'linear':backlin,'quadradic':backquad, 'squareroot':backroot, 'natrual':backnatural}

#the function takes two sets of data and returns a dictionary with all the backcalcs
#keyed to concnetration, and 
def customcurvefit(xdata, ydata,analytedict):
#get into a np.array
    xarray = np.asarray(xdata)
    yarray = np.asarray(ydata).mean(1)

#and the constants dictionary
    consdict = {}

#go thru function list and find the curve                
    for item in functions:
#curve fit based on the curve given, concentration, mean of injections, and weighted to 1/X**item[1]
        popt, pcov = curve_fit(item[0], xarray, yarray, None, xarray**item[1])
#add the constants values to dictionary to report out
        consdict[item[2]] = popt
#assign constant values for backcalcs
        if len(popt)==3:
            a = popt[0]
            b = popt[1]
            c = popt[2]
        else:
            a = popt[0]
            b = popt[1]
            c = 0

        for conc in analytedict:
            analytedict[conc].setdefault('mean',{})
            for run in analytedict[conc]:
                if run == 'all':
                    pass
                elif run == 'mean':                    
                    yvalue = np.mean(analytedict[conc]['all'])
                    backcalc = analytedict[conc]['mean'].setdefault(item[2],[])

                    if item[2].split(' ')[0] == 'quadradic':
                        backcalc.append(backquad(yvalue,a,b,c))
                    else:
                        backcalc.append(backfuncdict[item[2].split(' ')[0]](yvalue,a,b))
                else:
                    yvalue = analytedict[conc][run]['raw'][0]
                    backcalc = analytedict[conc][run].setdefault(item[2],[])

                    if item[2].split(' ')[0] == 'quadradic':
                        backcalc.append(backquad(yvalue,a,b,c))
                    else:
                        backcalc.append(backfuncdict[item[2].split(' ')[0]](yvalue,a,b))
                    
#return data based on concentration
    return consdict
