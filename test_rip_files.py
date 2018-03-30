import pytest
import utilities as ut
import os

ut.ErrorFile(error_name="lgr_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true-rip")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-rip")

list_file_names =  ut.get_file_names(valid_output_ws, filter=".lst")

setup = [(lf, owhm2_output_ws, valid_output_ws) for lf in list_file_names]

head_file_names =  ut.get_file_names(valid_output_ws, filter=".hed")
head_file_names += ut.get_file_names(valid_output_ws, filter=".hds")
head_file_names += ut.get_file_names(valid_output_ws, filter=".ufh")

setup2 = [(hf, owhm2_output_ws, valid_output_ws) for hf in head_file_names]


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
