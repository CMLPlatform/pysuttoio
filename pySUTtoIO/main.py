import numpy as np
import os.path
import glob
import pySUTtoIO.sut as st
import pySUTtoIO.transformation_model_b as mb
from os.path import isfile, join

def main(data_dir, model): # added model so that this module can be use as interface to call the specific model types

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

def launch(or_sut_data_dir, model, save_dir=None):
    years = glob.glob(os.join(os.path.abspath(or_sut_data_dir),"*/"))
    for data_dir_yr in years:
        yr_string = str(data_dir_yr[-5:-1]) # getting the name of the year
        IO_tables = main(data_dir, model=None)
    if save_dir != None:





or_sut_data_dir = "data\\clean\\msut"
