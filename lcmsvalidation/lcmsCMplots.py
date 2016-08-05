import numpy as np
import matplotlib.pyplot as plt


#make a scatter plot
def graph(residualdict, consdict, pointsdict, analyte, filename):
    eqlist = sorted(residualdict.keys())
#setup the figure ( #rows, #cols, size in inchs)        
    fig, axes = plt.subplots(nrows=3,ncols=4, figsize =(15,8))    
    col = 0
#for each curve do stuff
    for equation in eqlist:
        row = 0
        
        title = analyte + ' ' + equation + '\n'
        xdata = np.asarray(residualdict[equation]['xdata'])
        ydata = np.asarray(residualdict[equation]['ydata'])
        xmean = np.asarray(residualdict[equation]['xmean'])
        ymean = np.asarray(residualdict[equation]['ymean'])
        ynorm = np.asarray(residualdict[equation]['ynorm'])
        ymeannorm = np.asarray(residualdict[equation]['ymeannorm'])
#get the unique x-values to use as ticks
        xticks = xdata.astype(int)
            
#get the x-bondaries of the graph               
        xmax = np.amax(xdata)
        if xmax < 0:
            xmax = xmax*0.75
        else:
            xmax = xmax*1.25          
        xmin = np.amin(xdata)
        if xmin < 0:
            xmin = xmin*1.25
        else:
            xmin = xmin*0.75

#find the max and min of y values for precent residuals
        ymaxtest = abs(np.amax(ydata))
        ymintest = abs(np.amin(ydata))

#choose the one with the largest magnitude for precent residuals
        if ymaxtest > ymintest:
            testcase = ymaxtest
        else:
            testcase = ymintest

#set the y-bondaries and ticks based on above (min, max(not included), interval) for precent residuals
        if 0 <= testcase <= 10:
            ymin = -12
            ymax = 12
            yticks = [-10, -5, 0, 5, 10]
        elif 10 < testcase <= 25:
            ymin = -30
            ymax = 30
            yticks = range(-30, 35, 5)
        elif 25 < testcase <= 50:
            ymin = -60
            ymax = 60
            yticks = range(-50, 60, 10)
        elif 50 < testcase <= 100:
            ymin = -120
            ymax = 120
            yticks = range(-100, 110, 20)
        elif 100 < testcase <=500:
            ymin = -600
            ymax = 600
            yticks = range(-500, 550, 100)
        else:
            ymin = -1200
            ymax = 1200
            yticks = range(-1000, 1100, 200)

#the normalized residuals will use simple -5 to 5 range
        ynormticks = range(-5,6,1)        
#plot the normalized residuals
#plot the raw data as blue circles
        axes[row,col].plot(xdata,ynorm, 'o')
#plot the averaged data as red squares
        axes[row,col].plot(xmean,ymeannorm, 'rs')
        axes[row,col].set_title((title + ' normalized residuals'),fontsize=8)
#set the boundaries of the graph
        axes[row,col].axis([xmin,xmax,-6,6])
#change the axis to only display on the left and bottom
        axes[row,col].yaxis.set_ticks_position('left')
        axes[row,col].xaxis.set_ticks_position('bottom')
#add a line at zero
        axes[row,col].axhline(0,0,1, color='r', linestyle = '--', lw=1)
#set a line at the max and min of the ydata
        axes[row,col].axhline(np.amax(ynorm),0,1, color='m', linestyle = ':', lw=1)
        axes[row,col].axhline(np.amin(ynorm),0,1, color='m', linestyle = ':', lw=1)
#set the scale of x to log
        axes[row,col].set_xscale('log')
        axes[row,col].set_xticks(xticks)
        axes[row,col].set_yticks(ynormticks)
        axes[row,col].set_xticklabels(xticks, fontsize = 'xx-small')
        axes[row,col].set_yticklabels(ynormticks, fontsize = 'x-small')
        row += 1
        
        
#plot the precent residuals
#plot the raw data as blue circles
        axes[row,col].plot(xdata,ydata, 'o')
#plot the averaged data as red squares
        axes[row,col].plot(xmean,ymean, 'rs')
        axes[row,col].set_title((title + ' percent residuals'),fontsize=8)
#set the boundaries of the graph
        axes[row,col].axis([xmin,xmax,ymin,ymax])
#change the axis to only display on the left and bottom
        axes[row,col].yaxis.set_ticks_position('left')
        axes[row,col].xaxis.set_ticks_position('bottom')
#add a line at zero
        axes[row,col].axhline(0,0,1, color='r', linestyle = '--', lw=1)
#set a line at the max and min of the ydata
        axes[row,col].axhline(np.amax(ydata),0,1, color='m', linestyle = ':', lw=1)
        axes[row,col].axhline(np.amin(ydata),0,1, color='m', linestyle = ':', lw=1)
#set the scale of x to log
        axes[row,col].set_xscale('log')
        axes[row,col].set_xticks(xticks)
        axes[row,col].set_yticks(yticks)
        axes[row,col].set_xticklabels(xticks, fontsize = 'xx-small')
        axes[row,col].set_yticklabels(yticks, fontsize = 'x-small')
        row += 1
        
        
        numcons = len(consdict[equation])
        a = consdict[equation][0]
        b = consdict[equation][1]
        
        xspace = np.linspace(xmin,xmax,200)

        xpticks = np.asarray(range(0,int(xmax),int(np.amax(np.asarray(pointsdict.keys()))/10)))
        if numcons == 2:
            yspace = (b*xspace+a)
        if numcons == 3:
            c = consdict[equation][2]
            yspace = (c*xspace**2+b*xspace+a)

        ypmax = 0
        axes[row,col].plot(xspace,yspace)
        for conc in pointsdict:
            ypoints = np.asarray(pointsdict[conc]['all'])
            ypmaxtest = np.amax(ypoints)
            if ypmax < ypmaxtest:
                ypmax = ypmaxtest
            xpoints = np.asarray([conc]*len(ypoints))
            axes[row,col].plot(xpoints,ypoints,'ro')
            
        if ypmax <= 5:
            ytickincrement = 1
        else:
            ytickincrement = int(ypmax/5)
            
        ypticks = np.asarray(range(0,int(ypmax*1.5),ytickincrement))
#change the axis to only display on the left and bottom
        axes[row,col].yaxis.set_ticks_position('left')
        axes[row,col].xaxis.set_ticks_position('bottom')
        axes[row,col].set_title((title + ' response by concnetration'),fontsize=8)
        axes[row,col].set_xticks(xpticks)
        axes[row,col].set_yticks(ypticks)
        axes[row,col].set_yticklabels(ypticks, fontsize = 'x-small')
        axes[row,col].set_xticklabels(xpticks, fontsize = 'xx-small')    
        col +=1
        
        
    fig.tight_layout() 
    plt.savefig(filename, dpi=200)
        
        
                

        
