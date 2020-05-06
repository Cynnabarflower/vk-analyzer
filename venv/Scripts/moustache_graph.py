import matplotlib.pyplot as plt
import matplotlib as mpl


def build_moustache(dframe, qual, quant, show_axes = True):
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

    dc = {} #initialaizing the dictionary
    for i in range(0, len(dframe[qual])):
        k = [] #initializing the auxilary array to create the dictionary
        k.append(dframe[quant][i])
        if dframe[qual][i] not in dc: #checking if the qualitative attribute is not already in the dictionary as a key
            for j in range(i+1, len(dframe[qual])):
                if dframe[qual][i] == dframe[qual][j]: #comparing the qualitative attribute with all next ones
                    k.append(dframe[quant][j]) #adding quantitative data to the dictionary
            dc[dframe[qual][i]] = k #adding all quantitative attributes of the same qualitative attribute to it
    a = list(dc.values())
    b = list(dc.keys())

    #dimensions of figure:
    fig = plt.figure(1, figsize=(12, 7)) #figure instance
    ax = fig.add_subplot(111) #axes instance

    #creating and designing the boxplot:
    bp = ax.boxplot(a, patch_artist=True) # to allow fill color

    for box in bp['boxes']:
        box.set( color='k', linewidth=2) #outline colour of the boxes
        box.set( facecolor = 'C0' ) #fill colour of the boxes

    #colour and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='k', linewidth=2)

    #colour and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color='k', linewidth=2)

    #colour and linewidth of the medians
    for median in bp['medians']:
        median.set(color='k', linewidth=2)

    #style of fliers and their fill
    for flier in bp['fliers']:
        flier.set(marker='o', color='#e7298a', alpha=0.5)

    ax.set_xticklabels(b) #add the qualitative data as x-axis labels
    return fig


def show_moustache(dframe, qual, quant):
    """
    Maidzhe Alexandra
    Opens a window with the built boxplot.
    :param dframe:
    :param qual:
    :param quant:
    """
    build_moustache(dframe, qual, quant)
    plt.show()


def save_moustache(dframe, qual, quant):
    """
    Maidzhe Alexandra
    Saves the boxplot in a png format,
    :param dframe:
    :param qual:
    :param quant:
    """
    #agg backend is used to create plot as a .png file
    mpl.use('agg')
    figure = build_moustache(dframe, qual, quant)
    figure.savefig('moustache1.png', bbox_inches='tight') #saving the figure


#****************************************************************
#import this file and write:
    #-> show_moustache(dframe, qual, quant) <- to open the figure
    #-> save_moustache(dframe, qual, quant) <- to save the figure in png format

    #dframe is the data frame
    #qual is the qualitative data (kachestvenniye)
    #quant is the quantitative data (kolichestvenniye)