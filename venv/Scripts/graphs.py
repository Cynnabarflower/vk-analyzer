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
    dframe = dframe.dropna(subset=[qual1, quant1])
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
        ax.set_xticklabels(b, rotation=40)
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
    dframe = dframe.dropna(subset=[qual1, qual2, quant])
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
        fig = plt.figure(2, figsize=(lat, long))
        ax = fig.add_subplot(111)

        # setting the width and positions for the bars
        bar_width = 0.95 / len(a)
        index = np.arange(len(b))

        for i in range(len(a)):
            ax.bar(index + i * bar_width, lst[i], bar_width, label=a[i])

        # adding indexes for x-axis label
        plt.xticks(index + (len(a) * bar_width - bar_width) / 2, b, rotation=40)

        if not show_axes:
            plt.axis('off')
        else:
            plt.legend()
            ax.set_ylabel(quant)

        return fig

    # otherwise the function returns 'None'


def sweetie_pie(dframe, qual, size=5, show_labels=True):
    """
    Maidzhe Alexandra
    Createsa Pie Chart
    :param dframe: the dataframe
    :param qual: qualitative data
    :param size: size of the plot window
    :param show_labels: bool to allow labels' showing
    :return: figure/None
    """
    labels = sorted(list(set(dframe[qual])))
    values = list(dframe.pivot_table(index=[qual], aggfunc='size'))

    fig = plt.figure(3, figsize=(size, size))
    if show_labels:
        plt.pie(values, labels=labels, autopct='%.1f%%')
    else:
        plt.pie(values)
    return fig


def show_graph(figure):
    """
    Maidzhe Alexandra
    Closes all the other figures,
    to open just the passed one.
    :param figure: a graph
    """
    n = figure.number
    # closing all figures but the one needed
    for i in range(1, 10):
        if i != n:
            plt.close(i)
    plt.show()


def save_graph(figure):
    figure.savefig('figure.png', bbox_inches='tight')


# ****************************************************************
# dframe is the data frame
# qual is the qualitative data (kachestvenniye)
# quant is the quantitative data (kolichestvenniye)


"""
Mosolov Alexandr.
The function builds a scatter diagram for two quantitative and one qualitative attributes.
:param data:
:type data: pandas DataFrame
:param quan1:
:type quan1: string
:param quan2:
:type quan2: string
:param qual:
:type qual: string
:param wid:
:type wid: int
:param long:
:type long: int
:param show_axes:
:type show_axes: bool
:return fig:
"""


# ****************************************************************
# #dframe is the data frame
# qual is the qualitative data (kachestvenniye)
# quant is the quantitative data (kolichestvenniye)


def dispersion_diagram(data, p1, p2, qual, lat, long, show_axes):
    u = data[qual].unique()
    fig, ax = plt.subplots(figsize=(lat, long))
    for i in range(len(u)):
        x = data.loc[data[qual] == u[i]][p1]
        y = data.loc[data[qual] == u[i]][p2]
        ax.scatter(x, y)
        # ax.set_xlabel(p1)
        # ax.set_ylabel(p2)
        ax.axis(False)
        # ax.legend(u)
    return fig


def kat_hist(data, qual, par, lat, long, show_axes):
    c = data[qual].unique()
    fig, ax = plt.subplots(figsize=(lat, long), nrows=1, ncols=len(c))
    for i in range(len(c)):
        x = data.loc[data[qual] == c[i]][par]
        ax[i].hist(x)
        ax[i].set_xlabel(par)
        ax[i].set_title(c[i])
        ax[i].axis(show_axes)
    return fig


def stkach(dframe, qual):
    """
    Maidzhe Alexandra
    Creates a new data frame with frequencies and percentage
    of each element of a given data frame column.
    :param dframe: data frame
    :param qual: name of the column with the qualitative data;
    :return: data frame
    """
    # Creating new data frame with frequencies
    m = dframe[qual].value_counts().to_frame()
    m.columns = ['Частота']
    # Adding a column with percentages
    m['Процент(%)'] = dframe[qual].value_counts(normalize=True)*100
    return m


def stkol(dframe):
    """
    Maidzhe Alexandra
    Creates a data frame with quantitative data's statistics.
    :param dframe: data frame
    :return: data frame
    """
    # dropping columns that are numeric but do not have quantitative data
    dframe = dframe.drop(columns=['sex', 'id', 'bdate'])
    # Selecting all columns with numeric values left
    if not dframe.select_dtypes(include='number').empty:
        # and creating a new data frame with the statistics
        m = dframe.describe().transpose()
        m.columns = ['Amount of data', 'Arithmetic mean', 'Standard deviation',
                     'Minimum', 'Quartile 1', 'Quartile 2', 'Quartile 3', 'Maximum']
        return m


def piv(dframe, qual1, qual2, aggname):
    """
    Maidzhe Alexandra
    Creates pivot table of two
    data frame's columns(qualitative data)
    :param dframe: data frame
    :param qual1: name of the column with the qualitative data for index(str);
    :param qual2: name of the column with the qualitative data for columns(str);
    :param aggname: name of the aggregation function to apply(str);
    :return: data frame;
    """
    return dframe.pivot_table(index=qual1, columns=qual2, fill_value=0, aggfunc=aggname)
