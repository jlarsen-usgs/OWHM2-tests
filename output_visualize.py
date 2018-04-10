import numpy as np
import matplotlib.pyplot as plt
import itertools
import os


COLORS = itertools.cycle(["r", "y", "b", "g", "c", "m",
                          "silver", "orangered", "slateblue",
                          "palevioletred", "darkseagreen",
                          "brown", "indigo"])

# todo: create the budget item dump to csv file method.
# todo: create a line graph method

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
        self.__net_valid = {}
        self.__net_owhm2 = {}

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

        if model == "valid":
            self.__net_valid = d

        else:
            self.__net_owhm2 = d

    def plot_budget_item(self, budget_item, *args, **kwargs):
        """
        Function to plot a single budget item from both
        simulations using matplotlib.

        :param budget_item: (str) budget item name
        :param args: matplotlib args
        :param kwargs: matplotlib keyword args

        :return: matplotlib axis object
        """
        budget_item = budget_item.upper()
        ind = np.arange(self.__n)

        if budget_item not in self.__keys:
            # this may be a net function
            ignore = ('TOTAL_IN', 'TOTAL_OUT', 'PERCENT_DISCREPANCY')
            keys = self.__keys

            for i in ignore:
                keys.pop(keys.index(i))

            self.__get_net(keys, 'valid')
            self.__get_net(keys, 'owhm2')

            if budget_item not in self.__net_owhm2:
                raise KeyError("Key: {} not found".format(budget_item))

            valid = self.__net_valid[budget_item]
            owhm2 = self.__net_owhm2[budget_item]

        else:
            valid = self.__valid[budget_item]
            owhm2 = self.__owhm2[budget_item]

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(ind, valid, '--k', label="Valid {}".format(budget_item))
        ax.plot(ind, owhm2, '.-r', label="OWHM2 {}".format(budget_item))

        return ax

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


        self.__get_net(keys, 'valid')
        self.__get_net(keys, 'owhm2')

        net_valid = self.__net_valid
        net_owhm2 = self.__net_owhm2
        keys = sorted(net_valid.keys())

        vp_bottom = np.zeros(vind.shape)
        vn_bottom = np.zeros(vind.shape)
        op_bottom = np.zeros(oind.shape)
        on_bottom = np.zeros(oind.shape)

        width = 0.25 # create a good metric to calculate this !

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

            vn_bottom[v < 0] += v[v < 0]
            on_bottom[o < 0] += o[o < 0]

        ax.set_xticks(ind, tuple(ticks))
        ax.set_xlim([min(ind), max(ind)])

        return ax


    def to_csv(self, sim="valid", ws="", name="test.csv"):
        """
        Function to dump budget items to a formatted csv file
        for manipulation in excel

        :param ws: (str) directory name to dump csv file to
        :param name: (str) csv file name
        """
        sim = sim.lower()
        if sim == "valid":
            data = self.__valid

        elif sim == "owhm2":
            data = self.__owhm2

        else:
            raise KeyError()

        header = [key for key in data.keys()]

        xlen = len(data)
        for key in header:
            ylen = len(data[key])
            break

        arr = np.zeros((xlen, ylen))

        for ix, key in enumerate(header):
            t = data[key]
            arr[ix, :] = t

        with open(os.path.join(ws, name), "w") as f:
            f.write(",".join(header))
            f.write("\n")
            np.savetxt(f, arr.T, fmt="%.4f", delimiter=",")




