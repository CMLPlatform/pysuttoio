import numpy as np
import os.path
import pySUTtoIO.sut as st
import pySUTtoIO.transformation_model_b as mb


def main(data_dir, model):

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
    model_b = md_b.io_coefficient_matrix()


    # CHECK IO TABLE
    if not md_b.check_io_transaction_matrix():
        print('Model B transaction matrix not correct')
    if not md_b.check_io_coefficients_matrix():
        print('Model B coefficients matrix not correct')
    if not md_b.check_ext_transaction_matrix():
        print('Model B extension matrix not correct')
    if not md_b.check_ext_coefficient_matrix():
        print('Model B extension coefficients matrix not correct')

years = range(2010, 2012)
clean_data_dir = "data\\clean\\msut"
for yr in years:
    yr_string = str(yr)
    data_dir = os.path.join(clean_data_dir, yr_string)
    main(data_dir, model=None)
