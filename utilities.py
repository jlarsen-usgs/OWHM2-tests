import numpy as np
import os


def array_compare(sim_array, valid_array, cell_tol=1e-04, array_tol=1e-03):
    """
    Utility similar to np.allclose to compare modflow output arrays for code
    validation.

    :param sim_array: (np.array) simulation array from new code base
    :param valid_array: (np.array) valid model solution
    :param cell_tol: (float) tolerance for failure when comparing cells
    :param array_tol: (float) tolerance for failure when comparing arrays
    :return: (bool) True == Pass, False == Fail
    """

    validate = np.abs(sim_array - valid_array)

    if np.sum(validate) > array_tol:
        return False

    failure = np.where(validate > cell_tol)

    if failure[0].size > 0:
        # todo: print cells where failure has occured!
        print("Failure")
        return False

    return True



def budget_compare():
    """
    Budget comparisons, will need to figure this one out.
    General to handle any budget object, but specific to match via
    numpy arrays.
    :return:
    """
    return True


if __name__ == "__main__":
    x = np.arange(25)
    y = np.arange(25)
    y[10] = 14
    x.shape = (5, 5)
    y.shape = (5, 5)
    print(array_compare(x, y))

