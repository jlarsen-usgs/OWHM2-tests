import pytest
import utilities as ut
import os



ut.ErrorFile(error_name="fmp_head_error.txt")

script_ws = os.path.dirname(os.path.abspath(__file__))
valid_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-true-fmp")
owhm2_output_ws = os.path.join(script_ws, "OWHM_Example_Problems/test-out-fmp")

head_file_names =  ut.get_file_names(valid_output_ws, filter=".hed")
head_file_names += ut.get_file_names(valid_output_ws, filter=".hds")
# head_file_names += ut.get_file_names(valid_output_ws, filter=".out")
head_file_names += ut.get_file_names(valid_output_ws, filter=".ufh")

setup = [(hf, owhm2_output_ws, valid_output_ws) for hf in head_file_names]


@pytest.mark.parametrize("name,owhm2_ws,valid_ws", setup)
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
