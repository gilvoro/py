import numpy as np
import matplotlib.pyplot as plt


#make a scatter plot
def graph(residualdict, consdict, pointsdict, analyte, filename):
    eqlist = sorted(residualdict.keys())
#setup the figure ( #rows, #cols, size in inchs)        
    fig, axes = plt.subplots(nrows=4,ncols=3, figsize =(16,10))    
    row = 0
#for each curve do stuff
    for equation in eqlist:
        col = 0
        title = analyte + ' ' + equation
        xdata = np.asarray(residualdict[equation]['xdata'])
        ydata = np.asarray(residualdict[equation]['ydata'])
        xmean = np.asarray(residualdict[equation]['xmean'])
        ymean = np.asarray(residualdict[equation]['ymean'])
        sdydata = np.asarray(residualdict[equation]['sdydata'])
        sdymean = np.asarray(residualdict[equation]['sdymean'])
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
#------------------------------------------------------------------------------
#for the sd-residuals
#find the max and min of y values
        ymaxtest = abs(np.amax(np.nan_to_num(sdydata)))
        ymintest = abs(np.amin(np.nan_to_num(sdydata)))

#choose the one with the largest magnitude
        if ymaxtest > ymintest:
            testcase = ymaxtest
        else:
            testcase = ymintest

        ymin = -(np.ceil(testcase)+0.5)
        ymax = np.ceil(testcase)+0.5
        yticks = range(int(-np.ceil(testcase)),int(np.ceil(testcase)+1),1)

#I want lines at 1sd, 2sd, 3sd if they exist, if not the highest in that range
        if np.ceil(testcase)>3:
            lineslist = range(-3,4,1)
        else:
            lineslist = yticks
        
#plot the raw data as blue circles
        axes[row,col].plot(xdata,sdydata, 'bo')
#plot the averaged data as red squares
        axes[row,col].plot(xmean,sdymean, 'rd')
        axes[row,col].set_title((title + ' standard residuals'),fontsize=8)
        axes[row,col].axis([xmin,xmax,ymin,ymax])
#change the axis to only display on the left and bottom
        axes[row,col].yaxis.set_ticks_position('left')
        axes[row,col].xaxis.set_ticks_position('bottom')
#add a line at zero
        axes[row,col].axhline(0,0,1, color='r', linestyle = '-', lw=1)
        axes[row,col].axhline(np.amax(sdydata),0,1, color='g', linestyle = ':', lw=1)
        axes[row,col].axhline(np.amin(sdydata),0,1, color='g', linestyle = ':', lw=1)
        for item in lineslist:
            if item == 0:
                pass
            else:
                axes[row,col].axhline(item,0,1, color='k', linestyle = '--', lw=0.5)
#set the scale of x to log
        axes[row,col].set_xscale('log')
        axes[row,col].set_xticks(xticks)
        axes[row,col].set_yticks(yticks)
        axes[row,col].set_xticklabels(xticks, fontsize = 'xx-small')
        axes[row,col].set_yticklabels(yticks, fontsize = 'x-small')
        col += 1
#------------------------------------------------------------------------------
#for the percent residuals
#find the max and min of y values
        ymaxtest = abs(np.amax(np.nan_to_num(ydata)))
        ymintest = abs(np.nan_to_num(np.amin(ydata)))

#choose the one with the largest magnitude
        if ymaxtest > ymintest:
            testcase = ymaxtest
        else:
            testcase = ymintest

#set the y-bondaries and ticks based on above (min, max(not included), interval)
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
        elif 100 < testcase <=250:
            ymin = -300
            ymax = 300
            yticks = range(-250, 300, 50)
        elif 250 < testcase <=500:
            ymin = -600
            ymax = 600
            yticks = range(-500, 550, 100)
        else:
            ymin = -1200
            ymax = 1200
            yticks = range(-1000, 1100, 200)

#plot the raw data as blue circles
        axes[row,col].plot(xdata,ydata, 'bo')
#plot the averaged data as red squares
        axes[row,col].plot(xmean,ymean, 'rd')
        axes[row,col].set_title((title + ' percent residuals'),fontsize=8)
        axes[row,col].axis([xmin,xmax,ymin,ymax])
#change the axis to only display on the left and bottom
        axes[row,col].yaxis.set_ticks_position('left')
        axes[row,col].xaxis.set_ticks_position('bottom')
#add a line at zero
        axes[row,col].axhline(0,0,1, color='r', linestyle = '--', lw=1)
        axes[row,col].axhline(np.amax(ydata),0,1, color='g', linestyle = ':', lw=1)
        axes[row,col].axhline(np.amin(ydata),0,1, color='g', linestyle = ':', lw=1)
#set the scale of x to log
        axes[row,col].set_xscale('log')
        axes[row,col].set_xticks(xticks)
        axes[row,col].set_yticks(yticks)
        axes[row,col].set_xticklabels(xticks, fontsize = 'xx-small')
        axes[row,col].set_yticklabels(yticks, fontsize = 'x-small')
        col += 1
#-----------------------------------------------------------------------------------------------------
#for backcalcs
                       
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
            axes[row,col].plot(xpoints,ypoints,'rx')
            
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
        row +=1

        
    fig.tight_layout() 
    plt.savefig(filename, dpi=200)
        
        
                

        
