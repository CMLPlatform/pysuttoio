###############################################################################
#                                                                             #
# A python script that reads EXIOBASE v3.3 product by product tables          #
# (according industry technology assumption) in transaction form for the      #
# the year 2011. Subsequently these data are transformed into numpy objects   #
# that will be used in the ExioVisuals version 2. The matrices made are:      #
# - final demand matrix (Y.npy),                                              #
# - leontief inverse matrix (L.npy),                                          #
# - indicators matrix (B.npy).                                                #
#                                                                             #
# The final demand matrix contains the total final demand of each             #
# country/region and has dimensions 9800 products x 49 countries. The unit of #
# expression of each number is million Euros.                                 #
# The Leontief inverse matrix has dimensions 9800 x 9800 products. The unit   #
# of expression of each number is million Euro of output needed of a          #
# particular  to create a million of Euro of a particular product.            #
# The B-matrix is a rather heterogeneous matrix. Partly it contains           #
# 'classic' extensions: factor inputs, GHG emissions and resources use.       #
# These 'classic' extensions are available at the lowest level of detail      #
# such as CO2, CH4, N2O but also at aggregated level such as GHG emission     #
# indicator. The second part of the B-matrix are total product output and     #
# product input coefficients. They are duplications of the information that   #
# actually is available in the A-matrix in transaction form. The values in    #
# B-matrix are expressed in different unit but always as coefficient i.e.     #
# per million Euro output.                                                    #
#                                                                             #
# Author: Institute of Environmental Sciences (CML), Leiden University        #
#                                                                             #
# Version 2: Include total product output and product input coefficients      #
#                                                                             #
# Version 3: Exclude product input coefficients                               #
#                                                                             #
###############################################################################
import numpy as np
import os.path
import copy
import pySUTtoIO.tools as tools


def main(directory, IO_tables):

    # SETTINGS
    ghg_index = [0, 1, 2, 27, 28, 29, 52, 53, 54, 55, 56, 57, 58, 59, 77, 78,
                 403, 404, 405, 406, 407, 410]
    va_index = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    material_index = range(419, 439, 1)
    tolerance = 1E-3
    prd_cnt = 200
    fd_cnt = 7
    cntr_cnt = 49

    Z = IO_tables.io_transaction_matrix()
    Y = IO_tables.final_demand()
    W = IO_tables.factor_inputs_transaction_matrix()
    extensions = IO_tables.ext_transaction_matrix()
    indicators_dir = "data/auxiliary/indicators_v3.txt"
    indicators = tools.csv_file_to_list(indicators_dir, delimiter='\t')
    H = tools.list_to_numpy_array(indicators, 0, 0)

    va = np.sum(W[va_index, :], axis=0, keepdims=True)
    E = extensions[:417, :]
    E = E[ghg_index, :]  # select CO2, CH4 and N2O emissions
    M = extensions[417:, :]

    M = M[material_index, :]  # "domestic extraction used" metals and minerals
    o_coeff = np.zeros((1, prd_cnt * cntr_cnt))  # dummy place holder
    M = np.vstack((o_coeff, W, E, M))  # stack all extensions
    M = np.dot(np.transpose(H), M)

    # CALCULATE TOTALS
    to = np.sum(Z, axis=1, keepdims=True) + np.sum(Y, axis=1, keepdims=True)  # total output ($)
    ti = np.transpose(np.sum(Z, axis=0, keepdims=True) + va)  # total outlays ($)

    # CALCULATE COEFFICIENTS
    A = np.dot(Z, tools.invdiag(to[:, 0]))  # input-output coefficients matrix ($/$)
    B = np.dot(M, tools.invdiag(to[:, 0]))  # extension coefficients (xx/$)

    # FILL IN TOTAL OUTPUT COEFFICIENTS IN B MATRIX AND REPLACE DUMMY
    o_coeff = copy.deepcopy(to)
    o_coeff[o_coeff > 0] = 1
    B[0, :] = np.transpose(o_coeff)

    # LEONTIEF INVERSE
    I = np.eye(prd_cnt * cntr_cnt)     # unity matrix ($)
    L = np.linalg.inv(I - A)           # Leontief inverse matrix ($/$)

    # CHECK
    # balanced to start with ?
    diff = np.abs(to - ti)
    for index in np.ndindex(diff.shape):
        if diff[index] > tolerance:
            print('difference to and ti larger than {} million Euro. Difference is {} at index {}.'
                  .format(tolerance, diff[index], index))

    # calculated total output equal to to initial total output
    x = np.dot(L, np.sum(Y, axis=1, keepdims=True))
    diff = np.abs(x - to)
    for index in np.ndindex(diff.shape):
        if diff[index] > tolerance:
            print('difference x and to larger than {} million Euro. Difference is {} at index {}.'
                  .format(tolerance, diff[index], index))

    # AGGREGATE FINALDEMAND
    Y_new = np.zeros([9800, 49])
    for cntr_idx in range(0, cntr_cnt):
        for fd_idx in range(0, fd_cnt):
            old_idx = cntr_idx * fd_cnt + fd_idx
            new_idx = cntr_idx
            Y_new[:, new_idx] = Y_new[:, new_idx] + Y[:, old_idx]
    Y = Y_new

    # SOME DELETING
    del Z
    del W
    del va
    del E
    del IO_tables
    del extensions

    # CREATE CANONICAL FILENAMES
    full_io_fn = os.path.join(directory, 'A_v4.npy')
    full_leontief_fn = os.path.join(directory, 'L_v4.npy')
    full_finaldemand_fn = os.path.join(directory, 'Y_v4.npy')
    full_extensions_fn = os.path.join(directory, 'B_v4.npy')

    # SAVING MULTIREGIONAL DATA AS BINARY NUMPY ARRAY OBJECTS
    np.save(full_io_fn, A)
    np.save(full_leontief_fn, L)
    np.save(full_finaldemand_fn, Y)
    np.save(full_extensions_fn, B)
