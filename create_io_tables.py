import os.path
import numpy as np
import tools as tl
import sut as st
import transformation_model_b as mb


def main():

    # 1. SETTINGS
    year = 2011
    clean_data_dir = os.path.join('..', 'data', 'clean')
    use_filename = 'U.npy'
    supply_filename = 'V.npy'
    finaldemands_filename = 'Y.npy'
    factorinputs_filename = 'W.npy'
    emissions_filename = 'Me.npy'
    direct_emissions_filename = 'Me_dir.npy'
    resources_filename = 'Mr.npy'
    direct_resources_filename = 'Mr_dir.npy'
    materials_filename = 'Mm.npy'
    direct_materials_filename = 'Mm_dir.npy'
    product_labels_filename = 'products.pck'
    industry_labels_filename = 'industries.pck'
    final_demand_labels_filename = 'finaluses.pck'
    factor_input_labels_filename = 'factorinputs.pck'
    emission_labels_filename = 'emissions.pck'
    resource_labels_filename = 'resources.pck'
    material_labels_filename = 'materials.pck'
    ghg_index = [0, 1, 2, 27, 28, 29, 52, 53, 54, 55, 56, 57, 58, 59, 77, 78, 403, 404, 405, 406, 407, 410]
    material_index = range(419, 439, 1)
    use_ramascene_extensions = True

    # 2. CREATE CANONICAL FILENAMES
    full_use_fn = os.path.join(clean_data_dir, str(year), use_filename)
    full_supply_fn = os.path.join(clean_data_dir, str(year), supply_filename)
    full_finaldemands_fn = os.path.join(clean_data_dir, str(year), finaldemands_filename)
    full_factor_inputs_fn = os.path.join(clean_data_dir, str(year), factorinputs_filename)
    full_emissions_fn = os.path.join(clean_data_dir, str(year), emissions_filename)
    full_direct_emissions_fn = os.path.join(clean_data_dir, str(year), direct_emissions_filename)
    full_resources_fn = os.path.join(clean_data_dir, str(year), resources_filename)
    full_direct_resources_fn = os.path.join(clean_data_dir, str(year), direct_resources_filename)
    full_materials_fn = os.path.join(clean_data_dir, str(year), materials_filename)
    full_direct_materials_fn = os.path.join(clean_data_dir, str(year), direct_materials_filename)

    full_product_labels_fn = os.path.join(clean_data_dir, str(year), product_labels_filename)
    full_industry_labels_fn = os.path.join(clean_data_dir, str(year), industry_labels_filename)
    full_final_demand_labels_fn = os.path.join(clean_data_dir, str(year), final_demand_labels_filename)
    full_factor_input_labels_fn = os.path.join(clean_data_dir, str(year), factor_input_labels_filename)
    full_emission_labels_fn = os.path.join(clean_data_dir, str(year), emission_labels_filename)
    full_resource_labels_fn = os.path.join(clean_data_dir, str(year), resource_labels_filename)
    full_material_labels_fn = os.path.join(clean_data_dir, str(year), material_labels_filename)

    # 3. LOAD FILES
    u = np.load(full_use_fn)
    v = np.load(full_supply_fn)
    y = np.load(full_finaldemands_fn)
    w = np.load(full_factor_inputs_fn)
    me = np.load(full_emissions_fn)
    me_dir = np.load(full_direct_emissions_fn)
    mr = np.load(full_resources_fn)
    mr_dir = np.load(full_direct_resources_fn)
    mm = np.load(full_materials_fn)
    mm_dir = np.load(full_direct_materials_fn)
    product_labels = tl.pickle_file_to_list(full_product_labels_fn)
    industry_labels = tl.pickle_file_to_list(full_industry_labels_fn)
    final_demand_labels = tl.pickle_file_to_list(full_final_demand_labels_fn)
    factor_input_labels = tl.pickle_file_to_list(full_factor_input_labels_fn)
    emission_labels = tl.pickle_file_to_list(full_emission_labels_fn)
    resource_labels = tl.pickle_file_to_list(full_resource_labels_fn)
    material_labels = tl.pickle_file_to_list(full_material_labels_fn)

    # 4. CREATE  EXTENSIONS OBJECTS
    if use_ramascene_extensions:

        w_ramascene = w  # select value added categories
        e_ramascene = me[ghg_index, :]  # select CO2, CH4 and N2O emissions
        m_ramescene = mm[material_index, :]  # select "domestic extraction used" metals and minerals
        extensions = np.vstack((w_ramascene, e_ramascene, m_ramescene))  # stack all extensions

        # have to create dummy direct value added extensions filled with zeros
        # direct value added does not exits
        w_direct_ramascene = np.zeros((np.size(w, axis=0), np.size(y, axis=1)))
        e_direct_ramascene = me_dir[ghg_index, :]         # select CO2, CH4 and N2O emissions
        m_direct_ramescene = mm_dir[material_index, :]    # select "domestic extraction used" metals and minerals
        direct_extensions = np.vstack((w_direct_ramascene,  e_direct_ramascene, m_direct_ramescene))

        e_ramascene_labels = [emission_labels[i] for i in ghg_index]
        m_ramascene_labels = [material_labels[i] for i in material_index]
        extension_labels = factor_input_labels
        extension_labels.extend(e_ramascene_labels)
        extension_labels.extend(m_ramascene_labels)

    else:

        extensions = np.vstack((me, mr, mm))
        direct_extensions = np.vstack((me_dir, mr_dir, mm_dir))
        extension_labels = emission_labels
        extension_labels.extend(resource_labels)
        extension_labels.extend(material_labels)

    # CREATE SUT DATA TRANSFER OBJECT
    sut = st.Sut()
    sut.use = u
    sut.supply = v
    sut.final_use = y
    sut.factor_inputs = w
    sut.extensions = extensions
    sut.direct_extensions = direct_extensions

    sut.product_categories = product_labels
    sut.industry_categories = industry_labels
    sut.finaluse_categories = final_demand_labels
    sut.factor_input_categories = factor_input_labels
    sut.extensions_categories = extension_labels

    # CREATE PXP-ITA IOT
    md_b = mb.TransformationModelB(sut)
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


main()
