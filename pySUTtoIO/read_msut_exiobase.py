###############################################################################
#                                                                             #
# A small python script that can read the EXIOBASE version 3.3 tab delimited  #
# supply-use text files into numpy arrays for further analysis.               #
#                                                                             #
# The row and column headers of each file are stored separately in pickle     #
# files.                                                                      #
#                                                                             #
# Before the multi-regional supply-use tables are stored as numy arrays, a    #
# check is made if product suppy & use and industry input & output are        #
# balanced. Any deviation larger than the defined tolerance are reported.     #
#                                                                             #
# Notice that the symbol v is used for the supply table which has a           #
# product by industry format.                                                 #
#                                                                             #
# November 2018                                                               #
#                                                                             #
###############################################################################
import os.path
import numpy as np
import pySUTtoIO.tools as tl


def main():

    # 1. SETUP
    years = range(2009, 2012)
    raw_data_dir = os.path.join("data", "raw")
    clean_data_dir = os.path.join("data", "clean", "msut")
    value_added_index = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    prd_cnt = 200
    ind_cnt = 163
    cntr_cnt = 49
    tolerance = 1E-4

    for yr in years:

        yr_string = str(yr)
        print('Reading multi-regional supply-use tables for year {} '.format(yr_string))

        # 2. CREATE FILENAMES
        supply_filename = 'mrSupply_3.3_' + yr_string + '.txt'
        use_filename = 'mrUse_3.3_' + yr_string + '.txt'
        finaldemand_filename = 'mrFinalDemand_3.3_' + yr_string + '.txt'
        factor_inputs_filename = 'mrFactorInputs_3.3_' + yr_string + '.txt'
        emissions_filename = 'mrEmissions_3.3_' + yr_string + '.txt'
        direct_emissions_filename = 'mrFDEmissions_3.3_' + yr_string + '.txt'
        materials_filename = 'mrMaterials_3.3_' + yr_string + '.txt'
        direct_materials_filename = 'mrFDMaterials_3.3_' + yr_string + '.txt'
        resources_filename = 'mrResources_3.3_' + yr_string + '.txt'
        direct_resources_filename = 'mrFDResources_3.3_' + yr_string + '.txt'

        # 3. CREATE CANONICAL FILENAMES
        full_supply_fn = os.path.join(raw_data_dir, yr_string, supply_filename)
        full_use_fn = os.path.join(raw_data_dir, yr_string, use_filename)
        full_finaldemand_fn = os.path.join(raw_data_dir, yr_string, finaldemand_filename)
        full_factor_inputs_fn = os.path.join(raw_data_dir, yr_string, factor_inputs_filename)
        full_emissions_fn = os.path.join(raw_data_dir, yr_string, emissions_filename)
        full_direct_emissions_fn = os.path.join(raw_data_dir, yr_string, direct_emissions_filename)
        full_materials_fn = os.path.join(raw_data_dir, yr_string, materials_filename)
        full_direct_materials_fn = os.path.join(raw_data_dir, yr_string, direct_materials_filename)
        full_resources_fn = os.path.join(raw_data_dir, yr_string, resources_filename)
        full_direct_resources_fn = os.path.join(raw_data_dir, yr_string, direct_resources_filename)

        # 4. READ FILES
        supply = tl.csv_file_to_list(full_supply_fn, delimiter='\t')
        use = tl.csv_file_to_list(full_use_fn, delimiter='\t')
        final_demands = tl.csv_file_to_list(full_finaldemand_fn, delimiter='\t')
        factor_inputs = tl.csv_file_to_list(full_factor_inputs_fn, delimiter='\t')
        emissions = tl.csv_file_to_list(full_emissions_fn, delimiter='\t')
        direct_emissions = tl.csv_file_to_list(full_direct_emissions_fn, delimiter='\t')
        materials = tl.csv_file_to_list(full_materials_fn, delimiter='\t')
        direct_materials = tl.csv_file_to_list(full_direct_materials_fn, delimiter='\t')
        resources = tl.csv_file_to_list(full_resources_fn, delimiter='\t')
        direct_resources = tl.csv_file_to_list(full_direct_resources_fn, delimiter='\t')

        # 5. CREATE NUMPY ARRAYS
        v = tl.list_to_numpy_array(supply, 3, 2)
        del supply
        u = tl.list_to_numpy_array(use, 3, 2)
        del use
        y = tl.list_to_numpy_array(final_demands, 3, 2)
        w = tl.list_to_numpy_array(factor_inputs, 2, 2)
        me = tl.list_to_numpy_array(emissions, 3, 2)
        me_dir = tl.list_to_numpy_array(direct_emissions, 3, 2)
        mm = tl.list_to_numpy_array(materials, 2, 2)
        mm_dir = tl.list_to_numpy_array(direct_materials, 2, 2)
        mr = tl.list_to_numpy_array(resources, 3, 2)
        mr_dir = tl.list_to_numpy_array(direct_resources, 3, 2)
        m = np.concatenate([me, mm, mr], axis=0)

        # 6. CREATE SEARCH LISTS
        product_labels = tl.get_row_header(final_demands, 3, 2)
        industry_labels = tl.get_column_header(factor_inputs, 2, 2)
        finaluse_labels = tl.get_column_header(final_demands, 3, 2)
        factor_input_labels = tl.get_row_header(factor_inputs, 2, 2)
        emission_labels = tl.get_row_header(direct_emissions, 3, 2)
        resource_labels = tl.get_row_header(direct_resources, 3, 2)
        material_labels = tl.get_row_header(direct_materials, 2, 2)
        extensions_labels = emission_labels + resource_labels + material_labels

        # 7. CALCULATE TOTALS
        # total value added
        va = np.sum(w[value_added_index, :], axis=0, keepdims=True)

        # total product supply and use
        prd_supply = np.sum(v, axis=1, keepdims=True)
        prd_use = np.sum(u, axis=1, keepdims=True) + np.sum(y, axis=1, keepdims=True)

        # total industry input and output
        ind_output = np.transpose(np.sum(v, axis=0, keepdims=True))
        ind_input = np.transpose(np.sum(u, axis=0, keepdims=True) + va)

        # 8. CHECK
        unbalanced_prd = list()
        unbalanced_prd.append(['index', 'country_code', 'product_name', 'absolute difference'])
        diff = np.abs(prd_supply - prd_use)
        cnt = 0
        for idx in range(0, prd_cnt * cntr_cnt):
            if diff[idx] > tolerance:
                cnt = cnt + 1
                row = [idx, product_labels[idx][0], product_labels[idx][1], diff[idx, 0]]
                unbalanced_prd.append(row)
        if cnt > 0:
            print('Warning: {0} unbalanced product supplies and uses found'.format(cnt))

        unbalanced_ind = list()
        unbalanced_ind.append(['index', 'country_code', 'industry_name', 'absolute difference'])
        diff = np.abs(ind_output - ind_input)
        cnt = 0
        for idx in range(0, ind_cnt * cntr_cnt):
            if diff[idx] > tolerance:
                cnt = cnt + 1
                row = [idx, industry_labels[idx][0], industry_labels[idx][1], diff[idx, 0]]
                unbalanced_ind.append(row)
        if cnt > 0:
            print('Warning: {0} unbalanced industry outputs and inputs found'.format(cnt))

        # 10. CREATE CANONICAL OUTPUT FILENAMES
        if not os.path.exists(os.path.join(clean_data_dir, yr_string)):
            os.makedirs(os.path.join(clean_data_dir, yr_string))

        full_supply_fn = os.path.join(clean_data_dir, yr_string, 'V.npy')
        full_use_fn = os.path.join(clean_data_dir, yr_string, 'U.npy')
        full_finaldemand_fn = os.path.join(clean_data_dir, yr_string, 'Y.npy')
        full_factor_inputs_fn = os.path.join(clean_data_dir, yr_string, 'W.npy')
        full_emissions_fn = os.path.join(clean_data_dir, yr_string, 'Me.npy')
        full_direct_emissions_fn = os.path.join(clean_data_dir, yr_string, 'Me_dir.npy')
        full_materials_fn = os.path.join(clean_data_dir, yr_string, 'Mm.npy')
        full_direct_materials_fn = os.path.join(clean_data_dir, yr_string, 'Mm_dir.npy')
        full_resources_fn = os.path.join(clean_data_dir, yr_string, 'Mr.npy')
        full_direct_resources_fn = os.path.join(clean_data_dir, yr_string, 'Mr_dir.npy')

        full_extensions_fn = os.path.join(clean_data_dir, yr_string, 'M.npy')

        full_product_labels_fn = os.path.join(clean_data_dir, yr_string, 'products.pck')
        full_industries_labels_fn = os.path.join(clean_data_dir, yr_string, 'industries.pck')
        full_finaluses_labels_fn = os.path.join(clean_data_dir, yr_string, 'finaluses.pck')
        full_factorinputs_labels_fn = os.path.join(clean_data_dir, yr_string, 'factorinputs.pck')
        full_emission_labels_fn = os.path.join(clean_data_dir, yr_string, 'emissions.pck')
        full_resource_labels_fn = os.path.join(clean_data_dir, yr_string, 'resources.pck')
        full_material_labels_fn = os.path.join(clean_data_dir, yr_string, 'materials.pck')

        full_extensions_labels_fn = os.path.join(clean_data_dir, yr_string, 'extensions.pck')

        full_prd_unbalance_fn = os.path.join(clean_data_dir, yr_string, 'prd_unbalances.txt')
        full_ind_unbalance_fn = os.path.join(clean_data_dir, yr_string, 'ind_unbalances.txt')

        # 11. SAVING MULTIREGIONAL DATA AS BINARY NUMPY ARRAY OBJECTS
        np.save(full_supply_fn, v)
        np.save(full_use_fn, u)
        np.save(full_finaldemand_fn, y)
        np.save(full_factor_inputs_fn, w)
        np.save(full_emissions_fn, me)
        np.save(full_direct_emissions_fn, me_dir)
        np.save(full_materials_fn, mm)
        np.save(full_direct_materials_fn, mm_dir)
        np.save(full_resources_fn, mr)
        np.save(full_direct_resources_fn, mr_dir)

        np.save(full_extensions_fn, m)

        tl.list_to_pickle_file(full_product_labels_fn, product_labels)
        tl.list_to_pickle_file(full_industries_labels_fn, industry_labels)
        tl.list_to_pickle_file(full_finaluses_labels_fn, finaluse_labels)
        tl.list_to_pickle_file(full_factorinputs_labels_fn, factor_input_labels)
        tl.list_to_pickle_file(full_emission_labels_fn, emission_labels)
        tl.list_to_pickle_file(full_resource_labels_fn, resource_labels)
        tl.list_to_pickle_file(full_material_labels_fn, material_labels)

        tl.list_to_pickle_file(full_extensions_labels_fn, extensions_labels)

        tl.list_to_csv_file(full_prd_unbalance_fn, unbalanced_prd, delimiter='\t')
        tl.list_to_csv_file(full_ind_unbalance_fn, unbalanced_ind, delimiter='\t')


main()
