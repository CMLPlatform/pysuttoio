import numpy as np
import os.path
import glob
import pySUTtoIO.sut as st
import pySUTtoIO.transformation_model_b as mb
import pySUTtoIO.make_ramascene_data as rama


def main(data_dir, model, make_secondary, project):
    """"
    added model so that this module can be use as interface to call the
    specific model types
    """

    # SETTINGS
    use_filename = "U.npy"
    supply_filename = "V.npy"
    finaldemands_filename = "Y.npy"
    factorinputs_filename = "W.npy"
    extensions_filename = "M.npy"

    # CREATE CANONICAL FILENAMES
    full_use_fn = os.path.join(data_dir, use_filename)
    full_supply_fn = os.path.join(data_dir, supply_filename)
    full_finaldemands_fn = os.path.join(data_dir, finaldemands_filename)
    full_factor_inputs_fn = os.path.join(data_dir, factorinputs_filename)
    full_extensions_fn = os.path.join(data_dir, extensions_filename)

    # LOAD FILES AND CREATE SUT DATA TRANSFER OBJECT
    sut = st.Sut()
    sut.use = np.load(full_use_fn)
    sut.supply = np.load(full_supply_fn)
    sut.final_use = np.load(full_finaldemands_fn)
    sut.factor_inputs = np.load(full_factor_inputs_fn)
    sut.extensions = np.load(full_extensions_fn)
    # should add one for final demand emissions

    # CREATE PXP-ITA IOT
    md_b = mb.TransformationModelB(sut, make_secondary)
    # model_b = md_b.io_coefficient_matrix()

    # CHECK IO TABLE
    if not md_b.check_io_transaction_matrix():
        print('Model B transaction matrix not correct')
    if not md_b.check_io_coefficients_matrix():
        print('Model B coefficients matrix not correct')
    if not md_b.check_ext_transaction_matrix():
        print('Model B extension matrix not correct')
    if not md_b.check_ext_coefficient_matrix():
        print('Model B extension coefficients matrix not correct')

    return(md_b)


def launch(or_sut_data_dir, model, save_dir, make_secondary, project=0):
    """
    project = 0 (EXIOBASE), 1 (RaMa-SCENE)

    """
    if save_dir == "":
        save_dir = os.path.expanduser("~\\Documents\\pySUTtoIO\\")

    years = glob.glob(os.path.join(os.path.abspath(or_sut_data_dir), "*/"))

    for data_dir_yr in years:
        yr_string = str(data_dir_yr[-5: -1])  # getting the name of the year

        if project == 0:
            directory = os.path.join(save_dir, yr_string)
        elif project == 1:
            directory = os.path.join(save_dir, "ramascene", yr_string)

        if not os.path.exists(directory):
            os.makedirs(directory)

        # This is a quick fix. This is data only needed for RaMa-SCENE
        # please update script to output everything
        A_file_name = os.path.join(directory, 'A.npy')
        L_file_name = os.path.join(directory, 'L.npy')
        Y_file_name = os.path.join(directory, 'Y.npy')
        B_file_name = os.path.join(directory, 'B.npy')
        W_file_name = os.path.join(directory, 'W.npy')
        
        print('Reading multi-regional supply-use tables for year {} '.format(yr_string))
        IO_tables = main(data_dir_yr, model, make_secondary, project)
        # 11. SAVING MULTIREGIONAL DATA AS BINARY NUMPY ARRAY OBJECT
        if project == 0:
            np.save(A_file_name, IO_tables.io_coefficient_matrix())
            np.save(L_file_name, IO_tables.io_total_requirement_matrix())
            np.save(Y_file_name, IO_tables.final_demand())
            np.save(B_file_name, IO_tables.ext_coefficients_matrix())
            np.save(W_file_name, IO_tables.factor_inputs_coefficients_matrix())

        elif project == 1:
            rama.main(directory, IO_tables)
