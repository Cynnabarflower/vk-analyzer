import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


#def check_dframe:

def moustache(dframe, qual1, quant1, lat = 12, long = 7, show_axes = True):
    """
    Maidzhe Alexandra
    Creates a dictionary with qualitative data as keys
    and quantitative as values out of the given data frame,
    with no repeating keys.
    Creates boxplot using matplotlib.pyplot.boxplot.
    :param dframe: the data frame
    :param qual: qualitative data
    :param quant: quantitative data
    :return: figure
    """
    if not dframe.empty:
        dframe.rename(columns={quant1: 'rainbow'}, inplace=True)
        a = dframe.groupby(qual1).rainbow.apply(list)
        b = list(a.keys())
    else:
        return None

    # dimensions of figure:
    # figure instance
    fig = plt.figure(1, figsize=(lat, long))
    # axes instance
    ax = fig.add_subplot(111)

    # finding maximum and minimum of qualitative data to personalize the y-thicklabel
    maxi = max([max(t) for t in a])
    mini = min([min(t) for t in a])
    plt.ylim(bottom=mini - 0.1 * (maxi - mini), top=maxi + 0.1 * (maxi - mini))

    # creating and designing the boxplot:
    # to allow fill colour
    bp = ax.boxplot(a, patch_artist=True)

    for box in bp['boxes']:
        # outline colour of the boxes
        box.set(color='k', linewidth=2)
        # fill colour of the boxes
        box.set(facecolor='C0')

    # colour and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='k', linewidth=2)

    # colour and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color='k', linewidth=2)

    # colour and linewidth of the medians
    for median in bp['medians']:
        median.set(color='k', linewidth=2)

    # style of fliers and their fill
    for flier in bp['fliers']:
        flier.set(marker='o', color='#e7298a', alpha=0.5)

    if not show_axes:
        plt.axis('off')

    # add the qualitative data as x-axis labels
    ax.set_xticklabels(b)
    return fig

def show_graph(figure):
    plt.show()


def save_graph(figure, name):
    figure.savefig('moustache21.png', bbox_inches='tight')

'''
def save_graph(graph_func, dframe, qual1='', qual2='', quant1='', quant2='', lat=12, long=7, show_axis=True):
    #agg backend is used to create plot as a .png file
    mpl.use('agg')
    figure = graph_func(dframe, qual1='', quant1='', lat=12, long=7, show_axes=True)
    # saving the figure
    figure.savefig('moustache27.png', bbox_inches='tight')

save_graph(moustache, dframe, qual1=qual1, quant1=quant, lat=12, long=7, show_axis=True)'''
#****************************************************************
#import this file and write:
    #-> show_moustache(dframe, qual, quant) <- to open the figure
    #-> save_moustache(dframe, qual, quant) <- to save the figure in png format

    #dframe is the data frame
    #qual is the qualitative data (kachestvenniye)
    #quant is the quantitative data (kolichestvenniye)

