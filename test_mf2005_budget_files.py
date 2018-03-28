import pytest
import utilities as ut
import os

ut.ErrorFile(error_name="mf2005_budget_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out")

budget_file_names =  ut.get_file_names(valid_output_ws, filter=".cbc")
budget_file_names += ut.get_file_names(valid_output_ws, filter=".bud")

setup = [(bud, owhm2_output_ws, valid_output_ws) for bud in budget_file_names]


@pytest.mark.parametrize("name,owhm2_ws,valid_ws", setup)
def test_mf2005_budgets(name, owhm2_ws, valid_ws):
    ut.ErrorFile.write_model_name(name)
    owhm2 = ut.CellByCellBudget(ws=owhm2_ws, budgetname=name)
    valid = ut.CellByCellBudget(ws=valid_ws, budgetname=name)

    if owhm2.success and valid.success:

        assert ut.budget_compare(sim_budget=owhm2, valid_budget=valid,
                                 incremental_tolerance=0.05,
                                 budget_tolerance=0.05)
    else:
        assert owhm2.success
        assert valid.success

"""
for name in budget_file_names:
    ut.ErrorFile.write_model_name(name)
    owhm2 = ut.CellByCellBudget(ws=owhm2_output_ws, budgetname=name)
    valid = ut.CellByCellBudget(ws=valid_output_ws, budgetname=name)

    if owhm2.success and valid.success:

        ut.budget_compare(sim_budget=owhm2, valid_budget=valid,
                          incremental_tolerance=0.05,
                          budget_tolerance=0.05)
    else:
        print('break')
"""