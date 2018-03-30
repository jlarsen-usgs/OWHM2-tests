import pytest
import utilities as ut
import os


ut.ErrorFile(error_name="nwt_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true-nwt")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-nwt")

# setup for listing files
list_file_names =  ut.get_file_names(valid_output_ws, filter=".lst")

setup = [(lf, owhm2_output_ws, valid_output_ws) for lf in list_file_names]

# setup for budget files
budget_file_names =  ut.get_file_names(valid_output_ws, filter=".cbc")
budget_file_names += ut.get_file_names(valid_output_ws, filter=".bud")

setup2 = [(bud, owhm2_output_ws, valid_output_ws) for bud in budget_file_names]

# setup for head files
head_file_names =  ut.get_file_names(valid_output_ws, filter=".hed")
head_file_names += ut.get_file_names(valid_output_ws, filter=".hds")
head_file_names += ut.get_file_names(valid_output_ws, filter=".ufh")

setup3 = [(hf, owhm2_output_ws, valid_output_ws) for hf in head_file_names]


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


@pytest.mark.parametrize("name,owhm2_ws,valid_ws", setup2)
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


@pytest.mark.parametrize("name,owhm2_ws,valid_ws", setup3)
def test_mf2005_head(name, owhm2_ws, valid_ws):
    ut.ErrorFile.write_model_name(name)
    owhm2 = ut.HeadFile(ws=owhm2_ws, headname=name)
    valid = ut.HeadFile(ws=valid_ws, headname=name)

    if owhm2.success and valid.success:
        assert ut.array_compare(sim_array=owhm2.head, valid_array=valid.head,
                                cell_tol=0.05,
                                array_tol=0.05)

    else:
        owhm2 = ut.HeadFile(ws=owhm2_ws, headname=name, precision="double")
        valid = ut.HeadFile(ws=valid_ws, headname=name, precision="double")

        if owhm2.success and valid.success:
            assert ut.array_compare(sim_array=owhm2.head,
                                    valid_array=valid.head,
                                    cell_tol=0.05,
                                    array_tol=0.05)
        else:
            ut.ErrorFile.write_error("Unkown loading error\n")
            assert owhm2.success
            assert valid.success

