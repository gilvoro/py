import numpy as np
import matplotlib.pyplot as plt

def xmr_plot(datadict, tolerance, units, analyte, filename):
    #set the number of rows equal to the number of keys in datadict aka levels
    outputdict= {}
    n_rows = len(datadict.keys())

    #setup figure and subplots, with the number of rows equal to the number of control clevels
    fig, axes = plt.subplots(nrows=n_rows,ncols=2, figsize =(11,8))
    fig.suptitle(analyte.upper())

    #set the titles
    axes[0,0].set_title('Range Plot')
    axes[0,1].set_title('Mean Plot')
    row = 0

    #go through level by level
    for level in sorted(datadict.keys()):
        #label the rows at the control level
        axes[row,0].set_ylabel(level, fontsize = 'large')
        n_value = datadict[level]['n_value']
        xlabels = datadict[level]['xlabels']
        #the xdata is equal to the number of FQC
        xdata = range(1, len(xlabels)+1)     
        ydata = datadict[level]['ydata']
        #get the means for each fqc
        ymeans = np.mean(ydata, axis = 1)
        #get the grand mean
        m_mean = np.mean(ydata)
        #based on the nominal value get the ticks based on the tolerances
        yraw_labels = n_value*np.asarray(tolerance)
        #insert a tick at the nominal value
        yraw_labels = np.insert(yraw_labels,(len(yraw_labels)/2),n_value)
        #the labels are the tick points plus units
        y_labels = []
        for item in yraw_labels:
            y_labels.append(str(item)+ str(units))
                
        #range calculations
        #if we don't have initial data we get a number of ranges equal to fqc - 1
        if datadict[level]['i_mean'] == 'none':
            if len(ymeans) > 1:
                rd = np.zeros(len(ymeans)-1)
                for a in range(0, len(rd)):
                    rd[a] = abs(ymeans[a+1]-ymeans[a])
                r_mean = np.mean(rd)
            else:
            #speical case if there is a single fqc
                rd = np.zeros(1)
                r_mean = 0
            rxdata = xdata[:-1]
            rxlabels = []
            #setup labels so fqc - fqc
            for a in range(len(xlabels)-1):
                newlabel = xlabels[a+1].split('\n')[0] + '\n-' + xlabels[a].split('\n')[0]
                rxlabels.append(newlabel)
        #if we have initial data then we get a number of ranges equal to the number of fqc
        else:
            if len(ymeans) > 1:
                rd = np.zeros(len(ymeans))
                rd[0] = abs(ymeans[0]-datadict[level]['i_mean'])
                for a in range(0, len(rd)-1):
                    rd[a+1] = abs(ymeans[a+1]-ymeans[a])
                r_mean = np.mean(rd)
            #special case for a single fqc
            else:
                rd = np.asarray([abs(ymeans[0]-datadict[level]['i_mean'])])
                r_mean = abs(ymeans[0]-datadict[level]['i_mean'])
            rxdata=xdata
            rxlabels = [xlabels[0].split('\n')[0] + '\n-initial value']
            for a in range(len(xlabels)-1):
                newlabel = xlabels[a+1].split('\n')[0] + '\n-' + xlabels[a].split('\n')[0]
                rxlabels.append(newlabel)

        #calculate the range control limit and set the height of the range graph depending on whats highest
        r_ucl = 3.27*r_mean
        if r_ucl > rd[np.argmax(rd)]:
            rangeymax = r_ucl*1.1
        else:
            rangeymax = rd[np.argmax(rd)]*1.1

        #calculate the control limits for the mean graph
        x_ucl = m_mean+(2.66*r_mean)
        x_lcl = m_mean-(2.66*r_mean)

        #set up labels for the ratio so without the first and last ones
        ratiolabel = []
        for a in tolerance[1:-1]:
            ratiolabel.append((str(int(round((a-1)*100))))+'%')
        ratiolabel.insert((len(ratiolabel)/2),'nominal\nvalue')
                          
    #plot the range date
        axes[row,0].axis([0,len(xdata)+1,0,rangeymax])        
        axes[row,0].xaxis.set_ticks_position('bottom')
        #range x-axis setup
        axes[row,0].set_xticks(range(1,len(rxdata)+1,1))
        axes[row,0].set_xticklabels(rxlabels, fontsize = 'xx-small' )
        #if there range upper control limit isn't zero plot it
        if r_ucl != 0:
            axes[row,0].axhline(r_ucl,0,1,color = 'r', linestyle = '--', lw = 1)
            axes[row,0].text(0.1, ((r_ucl)+(r_ucl/500.0)), 'Upper Limit',fontsize='x-small')
        #range y-axis setup
        axes[row,0].yaxis.set_ticks_position('left')
        axes[row,0].set_yticks(np.around(rangeymax*np.array([0,0.25,0.5,0.75,1]),2))
        axes[row,0].set_yticklabels(np.around(rangeymax*np.array([0,0.25,0.5,0.75,1]),2), fontsize = 'x-small')
        axes[row,0].axhline(r_mean,0,1,color='k', lw = 0.5)
        axes[row,0].text(0.01,((r_mean)+(r_ucl/500.0)), 'Mean', fontsize='xx-small')
        axes[row,0].text(0.2,rangeymax*0.7, 'Mean: ' + str(round(r_mean,3))+units, fontsize = 'x-small', color = 'r')
        #plot the range data
        axes[row,0].plot(rxdata,rd,'ko--', markersize=5)
        
    #plot the measured data
        axes[row,1].axis([0,len(xdata)+1,n_value*tolerance[0],n_value*tolerance[-1]])
        #setup the yticks for the left axis
        axes[row,1].yaxis.set_ticks_position('left')
        axes[row,1].set_yticks(yraw_labels[1:-1])
        axes[row,1].set_yticklabels(ratiolabel, fontsize = 'x-small')
        #twin the x axis and setup the ticks on the right side of the graph
        ax2 = axes[row,1].twinx()
        ax2.axis([0,len(xdata)+1,n_value*tolerance[0],n_value*tolerance[-1]])
        ax2.yaxis.set_ticks_position('right')
        ax2.set_yticks(yraw_labels)
        ax2.set_yticklabels(y_labels,fontsize='x-small')
        #setup the x-axis
        axes[row,1].xaxis.set_ticks_position('bottom')
        axes[row,1].set_xticks(range(1,len(xdata)+1,1))
        axes[row,1].set_xticklabels(xlabels, fontsize = 'xx-small')
        #plot the data
        axes[row,1].plot(xdata,ydata,'ko',markersize=5)
        axes[row,1].plot(xdata,ymeans,'rs-',markersize=5)
        #put in a bunch of fixed lines and labels
        axes[row,1].axhline(m_mean,0,1,color='k', lw = 0.5)
        axes[row,1].text(0.01, ((m_mean)+(n_value/500.0)), 'Mean',fontsize='xx-small')
        axes[row,1].axhline(x_ucl, 0,1,color='r', linestyle = '--', lw = 0.5)
        axes[row,1].text(0.01, ((x_ucl)+(n_value/500.0)), 'Upper Limit',fontsize='xx-small')
        axes[row,1].axhline(x_lcl, 0,1,color='r', linestyle = '--', lw = 0.5)
        axes[row,1].text(0.01, ((x_lcl)+(n_value/500.0)), 'Lower Limit',fontsize='xx-small')
        axes[row,1].text(0.1, 1.03*(n_value*tolerance[0]), 'Mean: ' + str(round(m_mean,3))+units, fontsize = 'x-small', color = 'r')
        for item in yraw_labels[1:-1]:
            axes[row,1].axhline(item,0,1,color='k', linestyle=':',lw =0.5)

        rangeoutputlist = []
        for diff in rd:
            rangeoutputlist.append(str(round(diff,3))+units)
            
        
        row += 1
        outputdict[level] = {'agg':[str(round(m_mean,2))+units, str(round(np.std(ydata),3))+units, str(round((np.std(ydata)/float(m_mean))*100,3))+ "%", str(round(x_lcl,3))+units, str(round(x_ucl,3))+units],
                             'rdata':rangeoutputlist,
                             'ragg':[str(round(r_mean,2))+units, str(round(np.std(rd),3))+units, str(round((np.std(rd)/float(r_mean))*100,3))+'%', str(round(r_ucl,3))+units],'n_value':str(n_value)+units,
                             'i_mean':str(datadict[level]['i_mean'])+units}

    print 'making graph for ' + analyte
    plt.savefig(filename)
    return(outputdict)

