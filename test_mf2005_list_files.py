import utilities as ut
import os

ut.ErrorFile(error_name="mf2005_list_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out")

list_file_names =  ut.get_file_names(valid_output_ws, filter=".lst")


for lf in list_file_names:
    ut.ErrorFile.write_model_name(lf)
    owhm2 = ut.ListBudget(ws=owhm2_output_ws, listname=lf)
    valid = ut.ListBudget(ws=valid_output_ws, listname=lf)

    if owhm2.success and valid.success:

        ut.budget_compare(sim_budget=owhm2, valid_budget=valid,
                                 incremental_tolerance=0.01,
                                 budget_tolerance=0.01)