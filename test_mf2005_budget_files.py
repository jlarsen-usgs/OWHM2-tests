import utilities as ut
import os


script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out")

budget_file_names =  ut.get_file_names(valid_output_ws, filter=".lst")