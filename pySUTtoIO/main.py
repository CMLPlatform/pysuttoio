import numpy as np
import os.path
import glob
import pySUTtoIO.sut as st
import pySUTtoIO.transformation_model_b as mb


def main(data_dir, model, make_secondary):
    """"
    added model so that this module can be use as interface to call the
    specific model types
    """

    # SETTINGS
    use_filename = "U.npy"
    supply_filename = "V.npy"
    finaldemands_filename = "Y.npy"
    factorinputs_filename = "W.npy"
    extensions_filename = "Me.npy"

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

    # CREATE PXP-ITA IOT
    md_b = mb.TransformationModelB(sut, True)
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


def launch(or_sut_data_dir, model, save_dir, make_secondary):

    if save_dir != "":
        directory = save_dir
    else:
        directory = os.path.expanduser("~\\Documents\\pySUTtoIO\\")

    if not os.path.exists(directory):
        os.makedirs(directory)

    years = glob.glob(os.path.join(os.path.abspath(or_sut_data_dir), "*/"))

    for data_dir_yr in years:
        yr_string = str(data_dir_yr[-5: -1])  # getting the name of the year
        IO_tables = main(data_dir_yr, model, make_secondary)
        os.makedirs(os.path.join(directory, yr_string))

        # This is a quick fix. This is data only needed for RaMa-SCENE
        # please update script to output everything
        A_file_name = os.path.join(directory, yr_string, 'A.npy')
        L_file_name = os.path.join(directory, yr_string, 'L.npy')
        Y_file_name = os.path.join(directory, yr_string, 'Y.npy')
        B_file_name = os.path.join(directory, yr_string, 'B.npy')

        # 11. SAVING MULTIREGIONAL DATA AS BINARY NUMPY ARRAY OBJECTS
        np.save(A_file_name, IO_tables.io_coefficient_matrix)
        np.save(L_file_name, IO_tables.io_total_requirement_matrix)
        np.save(Y_file_name, IO_tables.final_demand)
        np.save(B_file_name, IO_tables.ext_coefficients_matrix)


if __name__ == "__main__":
    # or_sut_data_dir = input("Dataset location:\n")
    or_sut_data_dir = "data\\clean\\msut"
    model = input("Transformation model:\n")
    save_dir = input("Saving directory:\n")
    launch(or_sut_data_dir, model, save_dir, make_secondary)
