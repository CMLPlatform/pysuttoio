#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 6 15:00 2018
Description: Modifying SUT to ensure appearance of secondary material flows in
IOT

Scope: RaMa-SCENE - Raw Materials SCENario Efficiency improvements

@author:Franco Donati
@institution:Leiden University CML
"""
import numpy as np


def make_secondary(data):
    """
    This allows to allign secondary flow in such a way that they then
    appear in the IOT

    Primary Products' positions

    C_WOOD: 57
    C_PULP: 59
    C_PLAS: 85
    C_GLAS: 96
    C_CMNT: 100
    C_STEL: 103
    C_PREM: 105
    C_ALUM: 107
    C_LZTP: 109
    C_COPP: 111
    C_ONFM: 113
    C_CONS: 149

    Primary Sectors'positions:

    A_WOOD: 49
    A_PULP: 51
    A_PLAS: 58
    A_GLAS: 64
    A_CMNT: 68
    A_STEL: 71
    A_PREM: 73
    A_ALUM: 75
    A_LZTP: 77
    A_COPP: 79
    A_ONFM: 81
    A_CONS: 112

    """
    V = data.supply
    U = data.use
    Y = data.final_use

    products = np.array([57, 59, 85, 96, 100, 103,
                         105, 107, 109, 111, 113, 149])

    industries = np.array([49, 51, 58, 64, 68, 71, 73,
                           75, 77, 79, 81, 112])

    no_countries = int(len(Y)/200)

    prod_or = make_coord_array(products, no_countries, 200)
    ind_or = make_coord_array(industries, no_countries, 163)

    moved = allocate_sec_mat(V, U, Y, prod_or, ind_or)

    V = moved["V"]
    U = moved["U"]

    data.supply = V
    data.use = U

    return(data)


def make_coord_array(coordinates, no_countries, no_ind_or_prod):

    n = 0
    nn = 0
    while n in range(len(coordinates)):
        while nn in range(no_countries):
            g = coordinates + no_ind_or_prod*nn
            if "s" not in locals():
                s = g
            else:
                s = np.concatenate([s, g])
            nn = nn+1
        n = n+1

    return(s)


def allocate_sec_mat(V, U, Y, prod_or, ind_or):
    """
    This function allows to move the primary material output from the
    secondary material industries to the secondary material output.
    This allows for the presence of secondary materials in the IOT
    once they are transformed from SUTS.

    prod_or = row position of the primary supplied material
    ind_or = colum pos. of the primary industry supplying primary material
    """
    V = V.copy()
    U = U.copy()
    Y = Y.copy()

    # position of the secondary material
    des_prod_ix_pos = prod_or + 1
    des_ind_col_pos = ind_or + 1

    # getting the value of secondary material from the supply table
    # which is placed on the primary material row
    misplaced = V[np.ix_(prod_or, des_ind_col_pos)]

    # placing the misplaced value to the secondary material row
    V[np.ix_(des_prod_ix_pos, des_ind_col_pos)] = misplaced

    # collecting how much of the primary material is consumed by final demand
    # to be subtracted from the supply value

    prim_sec_supply_trans = V[np.ix_(prod_or)]

    prim_sec_tot_output = np.sum(prim_sec_supply_trans)

    sec_supply_trans = V[np.ix_(des_prod_ix_pos, des_ind_col_pos)]

    sec_output = np.sum(sec_supply_trans, axis=1)

    ratio_prim_sec = np.diag(np.divide(sec_output, prim_sec_tot_output))

    ratio_prim_sec[ratio_prim_sec == [np.nan, np.inf]] = 0

    prim_sec_use_trans = U[np.ix_(prod_or)]

    prim_sec_fin_dem_trans = Y[np.ix_(prod_or)]

    eye = np.identity(len(ratio_prim_sec))

    U[np.ix_(prod_or)] = (eye - ratio_prim_sec) @ prim_sec_use_trans

    U[np.ix_(des_prod_ix_pos)] = ratio_prim_sec @ prim_sec_use_trans

    Y[np.ix_(prod_or)] = ( eye - ratio_prim_sec) @ prim_sec_fin_dem_trans

    Y[np.ix_(des_prod_ix_pos)] = ratio_prim_sec @ prim_sec_fin_dem_trans

# =============================================================================
#     # how the supply to intraindustry transactions is distributed in its use
#     V_values = np.diag(1/(np.sum(V[np.ix_(prod_or)], axis=1)-Y_values))
#     print(V_values[V_values == np.inf])
#     V_values[V_values == [np.inf, np.nan]] = 0
#     dist = np.dot(V_values, U[np.ix_(prod_or)])
#     dist[dist == [np.inf, np.nan]] = 0
#     print(dist[dist == np.inf])
#
#     # mapping the use of the secondary material according to the distribution
#     # of use of the primary material
#     print("misplace ", misplaced)
#     print("dist ", dist)
#     U[np.ix_(des_prod_ix_pos)] = np.diag(misplaced.sum(axis=1)) @ dist
#
#     # subtracting the use of secondary material from the primary
#     U[np.ix_(prod_or)] = np.subtract(U[np.ix_(prod_or)],
#                                      np.array(U[np.ix_(des_prod_ix_pos)]))
#     print(U[U == np.inf])
#
#     # zeroing the misplaced value of secondary materials
#     V[np.ix_(prod_or, des_ind_col_pos)] = 0
#     print(V[V == [np.inf, np.nan]])
#
#     print(U[np.ix_(des_prod_ix_pos)])
#
#     # print(U[np.ix_(des_prod_ix_pos)])
#
#     # verifying balance
# =============================================================================
    g1_over_g2 = np.nan_to_num((np.sum(V, axis=1) / (np.sum(U, axis=1) + np.sum(Y, axis=1))) * 100)

    print(g1_over_g2[g1_over_g2 != [0,100]])

    output = {"V": V,
              "U": U,
              "Y": Y,
              "balance": g1_over_g2}

    return(output)
