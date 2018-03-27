import numpy as np
import flopy as fp
import os


class ErrorFile(object):
    """
    Class object to create and store unit testing failure information
    for MODFLOW-OWHM version 2

    :param error_name: (str) error file name
    """
    name = "errors.txt"

    header = """MODFLOW-OWHM2 unit testing error file created by python unit testing
    utilities. Unit testing code base is located @ https://github.com/jlarsen-usgs/OWHM2-tests.
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    """

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
            f.write('\n')


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
        self.success = True
        self.head = np.array([])
        self.fail_list = []

        super(HeadFile, self).__init__()
        self.__get_heads()

    def __get_heads(self):
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


class CellByCellBudget(dict):
    """
    Class to grab cell budget information out of flopy structure and
    use it for budget comparisons. Sets budget items to an over-ridden
    dictionary object

    :param ws: (str) output directory workspace
    :param budname: (str) budget file name
    :param precision: (str) single or double are only valid params
    """
    def __init__(self, ws, budname, precision='single'):
        self.__ws = ws
        self.__name = budname
        self.__precision = precision
        self.__file = os.path.join(ws, budname)
        self.__ignore = ('totim', 'time_step', 'stress_period')
        self.success = True
        self.fail_list = []

        super(CellByCellBudget, self).__init__()
        self.__get_budget()

    def __get_budget(self):
        try:
            bud = fp.utils.CellBudgetFile(self.__file,
                                          precision=self.__precision)
            records = bud.get_unique_record_names()

        except:
            self.success = False
            self.fail_list.append('no_file')
            return

        for name in records:
            try:
                if name.strip().lower() in self.__ignore:
                    pass
                else:
                    self[name.strip().upper()] = bud.get_data(text=name,
                                                              full3D=True)
            except:
                self.sucess = False
                self.fail_list.append(name)

    def keys(self):
        return [key for key in sorted(self.keys())]


class ListBudget(dict):
    """
    Class to grab cell budget information out of flopy structure and
    use it for budget comparisons. Sets budget items to an over-ridden
    dictionary object

    :param ws: (str) output directory workspace
    :param listname: (str) listing file name
    """
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
            budget = mflist.get_budget()
        except:
            self.success = False
            self.fail_list.append('no_file')
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

    def keys(self):
        return [key for key in sorted(self.keys())]


def array_compare(sim_array, valid_array, cell_tol=0.01, array_tol=0.03):
    """
    Utility similar to np.allclose to compare modflow output arrays for code
    validation.

    :param sim_array: (np.array) simulation array from new code base
    :param valid_array: (np.array) valid model solution
    :param cell_tol: (float) tolerance fraction for failure when comparing cells
    :param array_tol: (float) tolerance fraction for failure when comparing arrays
    :return: (bool) True == Pass, False == Fail
    """

    validate = (sim_array - valid_array) / sim_array

    if np.abs(np.sum(validate)) > array_tol:
        return False

    failure = np.where(np.abs(validate) > cell_tol)

    if failure[0].size > 0:
        # todo: print cells where failure has occured!
        print("Failure")
        return False

    return True


def budget_compare(sim_budget, valid_budget,
                   incermental_tolerance=0.01,
                   budget_tolerance=0.01):
    """
    Budget comparisons, will need to figure this one out.
    General to handle any budget object, but specific to match via
    numpy arrays.
    :param sim_budget:
    :param valid_budget:
    :param incremental_tolerance:
    :param budget_tolerance:
    :return: (bool) True == Pass, False == Fail
    """
    if sim_budget.keys() != valid_budget.keys():
        return False

    for key in valid_budget.keys():
        sim_array = sim_budget[key]
        valid_array = valid_budget[key]

        validate = (sim_array - valid_array) /  sim_array

        if np.abs(np.sum(validate)) > budget_tolerance:
            return False

        failure = np.where(np.abs(validate) > incermental_tolerance)

        if failure[0].size > 0:
            # todo: extract the cells where failure has occured
            print("Failure")
            return False

    return True


if __name__ == "__main__":
    x = np.arange(25)
    y = np.arange(25)
    y[10] = 14
    x.shape = (5, 5)
    y.shape = (5, 5)
    print(array_compare(x, y))
