import numpy as np
import flopy as fp
import os


class CommonExtentions(object):
    list_file = [".lst", ".list"]
    head_file = [".hed", ".head", ".hds", ".ufh"]
    budget_file = [".cbc", ".bud"]
    out_file = [".out"]


class ErrorFile(object):
    """
    Class object to create and store unit testing failure information
    for MODFLOW-OWHM version 2

    :param error_name: (str) error file name
    """
    name = "errors.txt"

    header = "MODFLOW-OWHM2 unit testing error file created by python unit testing\n"\
    "utilities. Unit testing code base is located @ https://github.com/jlarsen-usgs/OWHM2-tests.\n"\
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n"

    def __init__(self, error_name='errors.txt'):
        ErrorFile.name = error_name

        with open(ErrorFile.name, "w") as f:
            f.write(ErrorFile.header)


    @staticmethod
    def write_error(s):
        """
        Method to append error information to the error file
        :param s: (str) sting describing unit test failure
        """
        with open(ErrorFile.name, 'a') as f:
            f.write(s)

    @staticmethod
    def write_model_name(s):
        """
        Method to append model name unit test to the error file
        :param s: (str) string that refers to model name
        """
        with open(ErrorFile.name, 'a') as f:
            f.write("@@@@@:  {}\n".format(s))


class HeadFile(dict):
    """
    Class to grab head file information out of the rigid flopy structure
    and use it for comparisons

    :param ws: (str)
    :param headname: (str) head file name
    :param precision: (str) single or double are only valid params
    """
    def __init__(self, ws, headname, precision='single'):
        self.__ws = ws
        self.__name = headname
        self.__precision = precision
        self.__file = os.path.join(ws, headname)
        self.__ignore = ('totim', 'time_step', 'stress_period')
        self.__binary = True
        self.success = True
        self.head = np.array([])
        self.fail_list = []

        self.__simple_binary()
        super(HeadFile, self).__init__()

        if self.success:
            if self.__binary:

                self.__get_binary_heads()
            else:
                # try reading it as a formatted head file
                self.__get_formatted_heads()

    def __simple_binary(self):
        """
        Extremely simple binary file checker! Works for head files, but
        not comprehensive by any nature!
        :return: bool
        """
        try:
            with open(self.__file) as bc:
                line = bc.readline()

            if b'\x00' in line:
                return

            self.__binary = False

        except:
            self.success = False

    def __get_binary_heads(self):
        try:
            head = fp.utils.HeadFile(self.__file, precision=self.__precision)

        except:
            self.success = False
            self.fail_list.append("no_file")
            return

        try:
            self.head = head.get_alldata()

        except:
            self.success = False
            self.fail_list.append('head')

    def __get_formatted_heads(self):
        try:
            head = fp.utils.FormattedHeadFile(self.__file,
                                              precision=self.__precision)
        except:
            return

        try:
            self.head = head.get_alldata()
            self.success = True
            self.fail_list = []
        except:
            self.fail_list = ['head']
            return


class CellByCellBudget(dict):
    """
    Class to grab cell budget information out of flopy structure and
    use it for budget comparisons. Sets budget items to an over-ridden
    dictionary object

    :param ws: (str) output directory workspace
    :param budgetname: (str) budget file name
    :param precision: (str) single or double are only valid params
    """

    adjust = {"MNW2_IN": "MNW_IN",
              "MNW2_OUT": "MNW_OUT"}

    def __init__(self, ws, budgetname, precision='single'):
        self.__ws = ws
        self.__name = budgetname
        self.__precision = precision
        self.__file = os.path.join(ws, budgetname)
        self.__ignore = ('totim', 'time_step', 'stress_period')
        self.success = True
        self.fail_list = []

        super(CellByCellBudget, self).__init__()
        self.__get_budget()

    def __get_budget(self):
        try:
            bud = fp.utils.CellBudgetFile(self.__file,
                                          precision=self.__precision)
            records = bud.unique_record_names()

        except:
            self.success = False
            self.fail_list.append('no_file')
            return

        for name in records:
            try:
                if name.strip().lower() in self.__ignore:
                    pass
                else:
                    self[name.strip().upper()] = np.array(bud.get_data(text=name,
                                                                       full3D=True))
            except:
                self.sucess = False
                self.fail_list.append(name)

        for key, new_key in CellByCellBudget.adjust.items():
            if key in self:
                self[new_key] = self[key]
                self.pop(key)

            else:
                pass

    def keys(self):
        return [key for key in sorted(self)]


class ListBudget(dict):
    """
    Class to grab cell budget information out of flopy structure and
    use it for budget comparisons. Sets budget items to an over-ridden
    dictionary object

    :param ws: (str) output directory workspace
    :param listname: (str) listing file name
    """

    adjust = {"MNW2_IN": "MNW_IN",
              "MNW2_OUT": "MNW_OUT"}

    def __init__(self, ws, listname, precision='single'):
        self.__ws = ws
        self.__name = listname
        self.__precision = precision
        self.__file = os.path.join(ws, listname)
        self.__ignore = ('totim', 'time_step', 'stress_period')
        self.success = True
        self.fail_list = []

        super(ListBudget, self).__init__()
        self.__get_budget()

    def __get_budget(self):
        try:
            mflist = fp.utils.MfListBudget(self.__file)
            budget = mflist.get_budget()[0]

        except:
            self.success = False
            self.fail_list.append('no_file')
            return

        if budget is None:
            self.success = False
            return

        for name in budget.dtype.names:
            try:
                if name.strip().lower() in self.__ignore:
                    pass
                else:
                    self[name.strip().upper()] = np.array([rec[name]
                                                           for rec in budget])

            except:
                self.success = False
                self.fail_list.append(name)

        for key, new_key in ListBudget.adjust.items():
            if key in self:
                self[new_key] = self[key]
                self.pop(key)

            else:
                pass

    def keys(self):
        return [key for key in sorted(self)]


class FarmOutputs(dict):
    """
    Reader for FBDetails and FDS.out for the farm process package.
    Can be extended to other farm process outputs.

    :param ws: (str) directory of output file
    :param outname: (str) name of the output file
    """
    ignore = ('active',
              'date_start',
              'def-flag',
              'drch',
              'fid',
              'q-discrepancy[%]',
              'q-drch-in',
              'q-in-out')

    isint = ('per', 'stp', 'fid')
    isstr = ()

    def __init__(self, ws, outname):
        self.__ws = ws
        self.__name = outname
        self.__file = os.path.join(ws, outname)
        self.__header = []
        self.success = True
        self.fail_list = []
        self.__timeunit = None

        super(FarmOutputs, self).__init__()

        try:
            self.__get_budget()
        except:
            self.success = False


    def __get_budget(self):
        """
        Reader definition for farm process output files, sets data
        to FarmOutput dictionary
        """
        with open(self.__file) as fout:
            self.__get_header(fout.readline())
            kper_idx = self.__header.index('per')
            fid_idx = self.__header.index('fid')

            while True:
                line = fout.readline()
                if not line:
                    break

                t = line.strip().split()
                fid = int(t[fid_idx])

                if fid not in self:
                    self[fid] = {}

                    for h in self.__header:
                        if h in FarmOutputs.ignore:
                            pass

                        elif h.startswith('v-'):
                            pass

                        else:
                            self[fid][h] = []

                    self.__set_data(fid, t)

                else:
                    self.__set_data(fid, t)

    def __set_data(self, fid, data):
        for ix, h in enumerate(self.__header):
            if h in FarmOutputs.ignore:
                pass

            else:
                if h.startswith('v-'):
                    pass

                elif h in FarmOutputs.isint:
                    self[fid][h].append(int(data[ix]))

                elif h in FarmOutputs.isstr:
                    self[fid][h].append(data[ix])

                else:
                    self[fid][h].append(float(data[ix]))

    def __get_header(self, line):
        self.__header = line.lower().strip().split()

    def __set_timestep_length(self):
        for k, v in self.items():
            if 'days' in v:
                self.__timeunit = 'days'
                cum_time = np.array(v['days'])
                break

            elif 'minutes' in v:
                self.__timeunit = 'minutes'
                cum_time = np.array(v['minutes'])
                break

            elif 'years' in v:
                self.__timeunit = 'years'
                cum_time = np.array(v['years'])
                break

            elif 'seconds' in v:
                self.__timeunit = 'seconds'
                cum_time = np.array(v['seconds'])
                break

            else:
                raise AssertionError("Cant discerne time step from data")

        ts_time = np.zeros(cum_time.shape)
        ts_time[0] = cum_time[0]

        ts_time[1:] = cum_time[1:] - cum_time[:-1]

        for k in self:
            self[k]['ts_time'] = ts_time

    def __calculate_harmonic_mean(self, data_dict):
        """
        Calculates a harmonic mean using the kper data and ts length
        :param data_dict: dictionary with data, tslen
        :return: np.ndarray
        """
        sp_data = []
        for per, data in sorted(data_dict.items()):
            numerator = 0
            for ix, v in enumerate(data['data']):
                numerator += (v * data['tslen'][ix])

            sp_data.append(numerator / np.sum(data['tslen']))

        return np.array(sp_data)

    def raw_to_stress_period(self):
        """
        Converts raw data to stress period based fluxes.
        """
        ignore = ('per', 'stp', 'ts_time', 'days')
        self.__set_timestep_length()

        for fid, datadict in self.items():
            per = datadict['per']
            ts_time = datadict['ts_time']

            for key, data in datadict.items():
                if key in ignore:
                    pass
                else:
                    temp = {}
                    for ix, point in enumerate(data):
                        kper = per[ix]
                        tslen = ts_time[ix]

                        if kper in temp:
                            temp[kper]['data'].append(point)
                            temp[kper]['tslen'].append(tslen)
                        else:
                            temp[kper] = {'data' :[point],
                                          'tslen':[tslen]}

                    sp_data = self.__calculate_harmonic_mean(temp)
                    self[fid][key] = sp_data

            datadict.pop('ts_time')
            datadict.pop('stp')
            time = datadict[self.__timeunit]

            new_time = []
            t = per[0]
            for ix, kper in enumerate(per):
                if kper > t:
                    t = kper
                    new_time.append(time[ix - 1])
                else:
                    pass

            new_time.append(time[-1])
            self[fid][self.__timeunit] = new_time
            self[fid]['per'] = np.arange(1, np.max(per) + 1, dtype=int)

    def keys(self):
        return [key for key in sorted(self)]


def array_compare(sim_array, valid_array, cell_tol=0.01, array_tol=0.01):
    """
    Utility similar to np.allclose to compare modflow output arrays for code
    validation. Used for head comparisons primarily but can be used for any other
    arrays of the same dimension.

    :param sim_array: (np.array) simulation array from new code base
    :param valid_array: (np.array) valid model solution
    :param cell_tol: (float) tolerance fraction for failure when comparing cells
    :param array_tol: (float) tolerance fraction for failure when comparing arrays
    :return: (bool) True == Pass, False == Fail
    """

    if sim_array.shape != valid_array.shape:
        err_msg = "Array shapes are not the same dimension\n"
        ErrorFile.write_error(err_msg)
        return False

    # use small number to ensure there are no divide by zero errors or nan values

    offset_sim_array = sim_array + 1.123456789
    offset_valid_array = valid_array + 1.123456789

    validate = (offset_sim_array - offset_valid_array) / offset_valid_array

    if np.abs(np.mean(validate)) > array_tol:
        err_msg = "Mean error: {:.2f} is greater than " \
                  "array tolerance: {:.2f}".format(np.abs(np.mean(validate)),
                                                   array_tol)
        ErrorFile.write_error(err_msg)
        return False

    failure = np.where(np.abs(validate) > cell_tol)

    if failure[0].size > 0:
        # finds and prints where failure has occured due to cell tolerance
        err_msg = ""
        if len(failure) == 4:
            # four dimensional np.array from cbc
            kper = failure[0]
            layer = failure[1]
            row = failure[2]
            col = failure[3]

            for failix, per in enumerate(kper):
                k = layer[failix]
                i = row[failix]
                j = col[failix]
                err_msg += "Array failure: kper: {}, layer: {}, " \
                           "row: {}, column {}, sim_val: {:.2f}, " \
                           "valid_val: {:.2f}, " \
                           "failure criteria : {:.3f}\n".format(per + 1,
                                                                 k + 1,
                                                                 i + 1,
                                                                 j + 1,
                                                                 sim_array[per, k, i, j],
                                                                 valid_array[per, k, i, j],
                                                                 validate[per, k, i, j])

        elif len(failure) == 3:
            # three dimensional np.array from cbc
            layer = failure[0]
            row = failure[1]
            col = failure[2]

            for failix, k in enumerate(layer):
                i = row[failix]
                j = col[failix]
                err_msg += "Array failure: layer: {}, " \
                           "row: {}, column {}, sim_val: {:.2f}, " \
                           "valid_val: {:.2f}, " \
                           "failure criteria : {:.3f}\n".format(k + 1,
                                                                 i + 1,
                                                                 j + 1,
                                                                 sim_array[k, i, j],
                                                                 valid_array[k, i, j],
                                                                 validate[k, i, j])

        elif len(failure) == 2:
            # this should not happen, but lets catch it anyway
            row = failure[0]
            col = failure[1]

            for failix, i in enumerate(row):
                j = col[failix]
                err_msg += "Array failure: layer: {}, " \
                           "column {}, sim_val: {:.2f}, " \
                           "valid_val: {:.2f}, " \
                           "failure criteria : {:.3f}\n".format(i + 1,
                                                                 j + 1,
                                                                 sim_array[i, j],
                                                                 valid_array[i, j],
                                                                 validate[i, j])

        elif len(failure) == 1:
            # budget items from listing file
            failed = failure[0]
            for cell in failed:
                err_msg += "Array failure: entry number: {}, " \
                           "sim_val: {:.2f}, valid_val: {:.2f}, " \
                           "failure criteria : {:.3f}\n".format(cell + 1,
                                                                 sim_array[cell],
                                                                 valid_array[cell],
                                                                 validate[cell])
        ErrorFile.write_error(err_msg)

        return False

    return True


def budget_compare(sim_budget, valid_budget,
                   incremental_tolerance=0.01,
                   budget_tolerance=0.01,
                   offset=100.):
    """
    Budget comparisons from either list file objects or cbc file objects

    :param sim_budget: <ListBudget> instance or <CellByCellBudget> instance
    :param valid_budget: <ListBudget> instance or <CellByCellBudget> instance
    :param incremental_tolerance: fraction tolerance for any individual comparison
    :param budget_tolerance: fraction total mean budget tolerance for comparison
    :param offset: (float) small number dampening offset.
    :return: (bool) True == Pass, False == Fail
    """
    if sim_budget.keys() != valid_budget.keys():
        return False

    for test_pass in range(2):
        # use a two pass approach, first pass is budget items,
        # second pass is storages and storage differences

        for key in valid_budget.keys():

            if test_pass == 0:
                if key in ("PERCENT_DISCREPANCY", "IN-OUT",
                           "STORAGE_IN", "STORAGE_OUT"):
                     continue

            else:
                if key not in ("IN-OUT", "STORAGE_IN", "STORAGE_OUT"):
                    continue

            sim_array = sim_budget[key]
            valid_array = valid_budget[key]

            if sim_array.size != valid_array.size:
                err_msg = "Budget arrays are not compatible: {}\n".format(key)
                ErrorFile.write_error(err_msg)
                return False

            # todo: continue thinking about this tolerance issue!
            # must use a larger offset ~100 to account for differences in small
            # budget values!

            # Not sure that absolute value is appropriate???
            #   Has the potential for false positives if sign is switched
            #   Maybe use -50 as an offset criteria cutoff? x < -50; x -= 100
            #                                               x >= -50; x += 100

            lsim_array = np.abs(sim_array) + offset
            lvalid_array = np.abs(valid_array) + offset

            validate = (lsim_array - lvalid_array) / lvalid_array

            if np.abs(np.mean(validate)) > budget_tolerance:
                err_msg = "Budget item {}: Budget error: {:.2f} " \
                          "is greater than budget " \
                          "tolerance: {:.2f}\n".format(key,
                                                       np.abs(np.mean(validate)),
                                                       budget_tolerance)

                ErrorFile.write_error(err_msg)

                return False

            failure = np.where(np.abs(validate) > incremental_tolerance)

            if failure[0].size > 0:
                err_msg = ""
                if len(failure) == 4:
                    # four dimensional np.array from cbc
                    kper = failure[0]
                    layer = failure[1]
                    row = failure[2]
                    col = failure[3]

                    for failix, per in enumerate(kper):
                        k = layer[failix]
                        i = row[failix]
                        j = col[failix]
                        err_msg += "Budget item: {}, kper: {}, layer: {}, " \
                                   "row: {}, column {}, sim_val: {:.2f}, " \
                                   "valid_val: {:.2f}, " \
                                   "failure criteria : {:.3f}\n".format(key,
                                                                        per + 1,
                                                                        k + 1,
                                                                        i + 1,
                                                                        j + 1,
                                                                        sim_array[per, k, i, j],
                                                                        valid_array[per, k, i, j],
                                                                        validate[per, k, i, j])

                elif len(failure) == 3:
                    # three dimensional np.array from cbc
                    layer = failure[0]
                    row = failure[1]
                    col = failure[2]

                    for failix, k in enumerate(layer):
                        i = row[failix]
                        j = col[failix]
                        err_msg += "Budget item: {}, layer: {}, " \
                                   "row: {}, column {}, sim_val: {:.2f}, " \
                                   "valid_val: {:.2f}, " \
                                   "failure criteria : {:.3f}\n".format(key,
                                                                        k + 1,
                                                                        i + 1,
                                                                        j + 1,
                                                                        sim_array[k, i, j],
                                                                        valid_array[k, i, j],
                                                                        validate[k, i, j])

                elif len(failure) == 2:
                    # this should not happen, but lets catch it anyway
                    row = failure[0]
                    col = failure[1]

                    for failix, i in enumerate(row):
                        j = col[failix]
                        err_msg += "Budget item: {}, layer: {}, " \
                                   "column {}, sim_val: {:.2f}, " \
                                   "valid_val: {:.2f}, " \
                                   "failure criteria : {:.3f}\n".format(key,
                                                                        i + 1,
                                                                        j + 1,
                                                                        sim_array[i, j],
                                                                        valid_array[i, j],
                                                                        validate[i, j])

                elif len(failure) == 1:
                    # budget items from listing file
                    failed = failure[0]
                    for cell in failed:
                        err_msg += "Budget item: {}, entry number: {}, " \
                                   "sim_val: {:.2f}, valid_val: {:.2f}, " \
                                   "failure criteria : {:.3f}\n".format(key,
                                                                        cell + 1,
                                                                        sim_array[cell],
                                                                        valid_array[cell],
                                                                        validate[cell])
                ErrorFile.write_error(err_msg)

                return False

    return True


def farm_outputs_compare(sim_budget, valid_budget,
                         incremental_tolerance=0.01,
                         budget_tolerance=0.01,
                         offset=100.):
    """
    Budget comparisions from farm process output files such as FBDETAILS and
    FDS.OUT
    :param sim_budget: <FarmOutputs> class object
    :param valid_budget: <FarmOutputs> class object
    :param incremental_tolerance: (float) fraction tolerance for each budget item
    :param budget_tolerance: (float) mean tolerance for full budget item
    :param offset: (float) small number dampening offset.
    :return: True == Pass, False == Fail
    """
    if sim_budget.keys() != valid_budget.keys():
        ErrorFile.write_error("Farm numbers do not match")
        return False


    for key in sim_budget.keys():
        t = budget_compare(sim_budget[key], valid_budget[key],
                           incremental_tolerance=incremental_tolerance,
                           budget_tolerance=budget_tolerance,
                           offset=offset)

        if not t:
            return t

    return True


def get_file_names(ws, filter=".lst"):
    return [f for f in os.listdir(ws)
            if os.path.isfile(os.path.join(ws, f))
            and f.lower().endswith(filter.lower())]


if __name__ == "__main__":
    x = np.arange(25)
    y = np.arange(25)
    y[10] = 14
    x.shape = (5, 5)
    y.shape = (5, 5)
    print(array_compare(x, y))
