import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
# assuming your timing data in a csv file you could import csv and read the data

def GetData(samplelen=20):
    """ As I don't wish to spend the time generating a csv file I will dummy!"""
    data = {'t':[], 's1':[], 's2':[], 's3':[],}
    vals = {'s1':0, 's2':0, 's3':0,}
    t_current = 0.0  #datetime.now()
    t_increment = 0.01  #timedelta(0, 100)
    for step in xrange(samplelen*10):
        data['t'].append(t_current)
        if step % 9 == 0:
            for s in ['s1', 's2']:
                vals[s] = random.choice([0, 1])
        vals['s3'] = random.choice([0, 1])
        for s in ['s1', 's2', 's3']:
            data[s].append(vals[s])
        t_current = t_current + t_increment
    return data

def PlotData(data, timename='t'):
    """
    Expects a dictionary of named items with a list of states in all but the
    time axis named in it.
    """
    plotlist = sorted([k for k in data.keys() if k < timename])
    print plotlist
    timeax = data.get(timename)
    print timeax
    f, axes = plt.subplots(len(plotlist), sharex=True, sharey=True)
    for k, ax in zip(plotlist, axes):
        #assert isinstance(ax, plt.axes.subplot)
        ax.set_title(k)
        ax.plot(timeax, data[k])
        ax.set_ybound(1.2, -0.2)
        #ax.set_xbound(timeax[0], timeax[-1])

    # Fine-tune figure; make subplots close to each other and hide x ticks for
    # all but bottom plot.
    f.subplots_adjust(hspace=0)
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    plt.show()

if __name__ == "__main__":
    DATA = GetData(50)
    print DATA
    PlotData(DATA)
