import pytest
import utilities as ut
import os

ut.ErrorFile(error_name="fmp_list_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true-fmp")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-fmp")

list_file_names =  ut.get_file_names(valid_output_ws, filter=".lst")

setup = [(lf, owhm2_output_ws, valid_output_ws) for lf in list_file_names]

@pytest.mark.parametrize("name,owhm2_ws,valid_ws", setup)
def test_mf2005_simulations(name, owhm2_ws, valid_ws):
    ut.ErrorFile.write_model_name(name)
    owhm2 = ut.ListBudget(ws=owhm2_ws, listname=name)
    valid = ut.ListBudget(ws=valid_ws, listname=name)

    if owhm2.success and valid.success:
        assert ut.budget_compare(sim_budget=owhm2, valid_budget=valid,
                                 incremental_tolerance=0.05,
                                 budget_tolerance=0.05)

    else:
        ut.ErrorFile.write_error("Unkown loading error\n")
        assert owhm2.success
        assert valid.success