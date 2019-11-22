import numpy as np
import matplotlib.pyplot as plt

def is_plot(analyte,filename,xvalues, yvalues, stats, length):
        #setup figures
        fig, ax = plt.subplots(figsize = (11,8))
        fig.suptitle(analyte.upper())

        ax.axis([0,length+1,-5.2*stats[1]+stats[0],5.2*stats[1]+stats[0]])
        ax.axhline(stats[0],0,length+1,color = 'K', lw = 1)
        ax.text(0.01,stats[0],'mean',fontsize = 'small')

        ax.xaxis.set_ticks_position('bottom')
        ax.set_xticks(range(0,length+1,int(round(length*0.2))))
        ax.set_xticklabels(['','~20%','~40%','~60%','~80%','~100%'], fontsize = 'small' )
                
        SDticks = (-5,-4,-3,-2,-1,1,2,3,4,5)
        ax.yaxis.set_ticks_position('none')
        for tick in SDticks:
                ax.axhline(tick*stats[1]+stats[0],0,length+1,color = 'r',
                           linestyle = '--', lw = 0.5)
                ax.text(0.01,tick*stats[1]+stats[0],str(tick)+'sd',fontsize = 'small')
        ax.set_yticklabels([])
        
        ax.scatter(xvalues,yvalues,color = 'k', marker = 's',s=25)
        
        xlength = np.linspace(0,length,length*2)
        yline = stats[2]*xlength + stats[3]
        ax.text(round(length-(length*0.3),0),round(4.5*stats[1]+stats[0],0),'R-squared = '+ str(round(stats[4],3)), color = 'r', fontsize = 'large')
	plt.plot(xlength,yline,color = 'green')

	plt.savefig(filename)

