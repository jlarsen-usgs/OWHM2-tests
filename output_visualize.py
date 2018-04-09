import numpy as np
import matplotlib.pyplot as plt
import itertools


COLORS = itertools.cycle(["r", "y", "b", "g", "c", "m",
                          "silver", "orangered", "slateblue",
                          "palevioletred", "darkseagreen",
                          "brown", "indigo"])

class ListBudgetOutput(object):
    """
    Class object to manipulate a pair of List Budget Files
    for output comparison purposes. Developed for the MF-OWHM2
    unit test cases

    :param valid: <utilities.ListBudget> class object
    :param owhm2: <utilities.ListBudget> class object
    """
    def __init__(self, valid, owhm2):

        self.__valid = valid
        self.__owhm2 = owhm2

        self.__n = len(self.__valid["IN-OUT"])
        self.__keys = self.__valid.keys()
        self.__v_bar_x = "V {}"
        self.__o2_bar_x = "O2 {}"

    def __get_net(self, keys, model='valid'):
        """
        Internal method to calculate net flux for each budget item
        :return: dict of net fluxes
        """
        pairs = []
        nets = []
        for key in keys:
            if "_IN" in key:
                t = [key]
                k = key[:-3]

                for key2 in keys:
                    if k in key2 and "_IN" not in key2:
                        t.append(key2)
                        pairs.append(t)
                        nets.append(k)
                        break

        if model == 'valid':
            model = self.__valid

        else:
            model = self.__owhm2

        d = {}
        for ix, pair in enumerate(pairs):
            d[nets[ix]] = model[pair[0]] - model[pair[1]]

        return d

    def plot_budget_item(self, budget_item, *args, **kwargs):
        """
        Function to plot a single budget item from both
        simulations using matplotlib.

        :param budget_item: (str) budget item name
        :param args: matplotlib args
        :param kwargs: matplotlib keyword args

        :return: matplotlib axis object
        """
        pass

    def plot_bar_chart(self, *args, **kwargs):
        """
        Plotting function for creating a stacked bar chart comparing
        budget pieces.

        :param args: matplotlib args
        :param kwargs: matplotlib keyword args

        :return: matplotlib axis object
        """
        ignore = ('TOTAL_IN', 'TOTAL_OUT',
                  'IN-OUT', 'PERCENT_DISCREPANCY')

        keys = self.__keys
        for i in ignore:
            keys.pop(keys.index(i))

        ind = np.arange(self.__n * 2)
        vind = ind[::2]
        oind = ind[1::2]

        ticks = []
        for i in np.arange(self.__n):
            ticks += [self.__v_bar_x.format(i),
                      self.__o2_bar_x.format(i)]

        net_valid = self.__get_net(keys, 'valid')
        net_owhm2 = self.__get_net(keys, 'owhm2')
        keys = sorted(net_valid.keys())

        vp_bottom = np.zeros(vind.shape)
        vn_bottom = np.zeros(vind.shape)
        op_bottom = np.zeros(oind.shape)
        on_bottom = np.zeros(oind.shape)

        width = 0.2 # create a good metric to calculate this !

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for ix, key in enumerate(keys):
            v = net_valid[key]
            o = net_owhm2[key]
            obottom = np.zeros(oind.shape)
            vbottom = np.zeros(vind.shape)

            vbottom[v < 0] = vn_bottom[v < 0]
            obottom[o < 0] = on_bottom[o < 0]

            vbottom[vbottom == 0] = vp_bottom[vbottom == 0]
            obottom[obottom == 0] = op_bottom[obottom == 0]

            bar_color = next(COLORS)

            ax.bar(vind, net_valid[key], width, color=bar_color,
                   bottom=vbottom)
            ax.bar(oind, net_owhm2[key], width, color=bar_color,
                   hatch='\\', alpha=0.5, bottom=obottom)

            vp_bottom[v >= 0] += v[v >= 0]
            op_bottom[o >= 0] += o[o >= 0]
            # vp_bottom[vbottom >= 0] += vbottom[vbottom >= 0]
            # op_bottom[obottom >= 0] += obottom[obottom >= 0]
            vn_bottom[v < 0] += v[v < 0]
            on_bottom[o < 0] += o[o < 0]

        ax.set_xticks(ind, tuple(ticks))
        ax.set_xlim([min(ind), max(ind)])

        plt.show()


    def to_csv(self, ws="", name="test.csv"):
        """
        Function to dump budget items to a formatted csv file
        for manipulation in excel

        :param ws: (str) directory name to dump csv file to
        :param name: (str) csv file name
        """