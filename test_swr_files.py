import pytest
import utilities as ut
import os


ut.ErrorFile(error_name="swr_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true-swr")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-swr")

list_file_names = []
head_file_names = []
budget_file_names = []

for extension in ut.CommonExtentions.list_file:
    list_file_names += ut.get_file_names(valid_output_ws, filter=extension)

for extension in ut.CommonExtentions.budget_file:
    budget_file_names += ut.get_file_names(valid_output_ws, filter=extension)

for extension in ut.CommonExtentions.head_file:
    head_file_names += ut.get_file_names(valid_output_ws, filter=extension)

setup = [(lf, owhm2_output_ws, valid_output_ws) for lf in list_file_names]
setup2 = [(bf, owhm2_output_ws, valid_output_ws) for bf in budget_file_names]
setup3 = [(hf, owhm2_output_ws, valid_output_ws) for hf in head_file_names]


@pytest.mark.parametrize("name,owhm2_ws,valid_ws", setup)
def test_list_budgets(name, owhm2_ws, valid_ws):
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
def test_budget_files(name, owhm2_ws, valid_ws):
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
def test_head_files(name, owhm2_ws, valid_ws):
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
