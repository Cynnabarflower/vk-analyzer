import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def moustache(dframe, qual1, quant1, lat=12, long=7, show_axes=True):
    """
    Maidzhe Alexandra
    Creates boxplots from two columns of a dataframe
    (qualitative - quantintative)using matplotlib.pyplot.boxplot.
    :param dframe: the dataframe;
    :param qual1: name of the column with the qualitative data;
    :param quant1: name of the column with the quantitative data;
    :param lat: width of the plot window;
    :param long: length of the plot window;
    :param show_axes: bool to allow axes' showing;
    :return: figure/None.
    """
    # converting quantitative data to float and non-convertible elements to nan
    dframe[quant1] = dframe[quant1].apply(pd.to_numeric, errors='coerce')
    # deleting all rows with nan values
    dframe = dframe.dropna(subset=[qual1])
    if not dframe.empty:
        dframe.rename(columns={quant1: 'rainbow'}, inplace=True)
        # creating lists' series of the quantitative data grouped by the qualitative data
        a = dframe.groupby(qual1).rainbow.apply(list)
        # creating a list of qualitative data for x-axis label
        b = list(a.keys())

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

        # adding the qualitative data as x-axis labels
        ax.set_xticklabels(b)
        return fig

    # otherwise the function returns 'None'


def klaster(dframe, qual1, qual2, quant, lat=12, long=7, show_axes=True):
    """
    Maidzhe Alexandra
    Creates a grouped bar chart from three columns of a dataframe;
    (qualitative, qualitative, quantintative)using matplotlib.pyplot.bar.
    :param dframe: the dataframe;
    :param qual1: name of the column with the series;
    :param qual2: name of the column with the categories;
    :param quant: name of the column with the values;
    :param lat: width of the plot window;
    :param long: length of the plot window;
    :param show_axes: bool to allow axes' showing;
    :return: figure/None.
    """
    # converting quantitative data to float and non-convertible elements to nan
    dframe[quant] = dframe[quant].apply(pd.to_numeric, errors='coerce')
    # deleting all rows with nan values
    dframe = dframe.dropna(subset=[qual1, qual2])
    if not dframe.empty:
        # get lists of qualitative data to legend (with a) and index (with b) the graph
        a = sorted(list(set(dframe[qual1])))
        b = sorted(list(set(dframe[qual2])))

        dframe = dframe.pivot_table(values=quant, index=qual1, columns=qual2).fillna(0)

        # get list of lists of the means
        lst = []
        for i in range(len(a)):
            lst.append(list(dframe.T[a[i]]))

        # building the figure:
        # fig, ax = plt.subplots()
        fig = plt.figure(1, figsize=(lat, long))
        ax = fig.add_subplot(111)

        # setting the width and positions for the bars
        bar_width = 0.95/len(a)
        index = np.arange(len(b))

        for i in range(len(a)):
            ax.bar(index + i*bar_width, lst[i], bar_width, label=a[i])

        # adding indexes for x-axis label
        plt.xticks(index + (len(a)*bar_width-bar_width)/2, b)

        if not show_axes:
            plt.axis('off')
        else:
            plt.legend()
            ax.set_ylabel(quant)

        return fig

    # otherwise the function returns 'None'


def show_graph(figure):
    plt.show()


def save_graph(figure):
    figure.savefig('figure.png', bbox_inches='tight')


#****************************************************************
# #dframe is the data frame
#qual is the qualitative data (kachestvenniye)
#quant is the quantitative data (kolichestvenniye)

