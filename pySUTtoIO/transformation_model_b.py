import math
import numpy as np
import os.path
import pySUTtoIO.tools as tl
import pySUTtoIO.sut as st
from pySUTtoIO.secondary_flows import make_secondary as ms


class TransformationModelB:
    """A supply-use table to input-output table transformation object.
    From the supply-use table a product-by-product input-output table
    based on industry technology assumption is created. In the 'Eurostat Manual
    of Supply, Use and Input-Output Tables' this transformation model is called
    model B. The resulting input-output table does not contain negative values.
    Onlythe domestic tables are taken into consideration"""

    default_rel_tol = 1E-3
    debug = False
    debug_data_dir = os.path.join('data', 'transformed', '2010', 'sut')

    def __init__(self, sut, make_secondary):
        assert type(sut) is st.Sut
        self._sut = sut
        if make_secondary:
            sut2 = ms(sut)
            self.V = sut2.supply
            self.U = sut2.use
            self.q = np.sum(self.V, axis=1)
            self.Y = sut2.final_use
        else:
            self.V = self._sut.supply
            self.U = self._sut.use
            self.q = self._sut.total_product_supply
            self.Y = self._sut.final_use

        if self.debug:
            product_out = np.sum(self.V, axis=1, keepdims=True)
            product_in = np.sum(self.U, axis=1, keepdims=True) + np.sum(self.Y, axis=1, keepdims=True)
            industry_out = np.sum(self.V, axis=0, keepdims=True)
            industry_in = np.sum(self.U, axis=0, keepdims=True) + np.sum(self._sut.value_added, axis=0, keepdims=True)

            full_supply_fn = os.path.join(self.debug_data_dir,'supply_transformed_new.txt')
            full_use_fn = os.path.join(self.debug_data_dir, 'use_transformed_new.txt')
            full_finaldemand_fn = os.path.join(self.debug_data_dir, 'finaldemand_transformed_new.txt')
            full_value_added_fn = os.path.join(self.debug_data_dir, 'value_added_transformed_new.txt')
            full_prd_supply_fn = os.path.join(self.debug_data_dir, 'product_supply_new.txt')
            full_prd_use_fn = os.path.join(self.debug_data_dir, 'product_use_new.txt')
            full_ind_input_fn = os.path.join(self.debug_data_dir, 'industry_input_new.txt')
            full_ind_output_fn = os.path.join(self.debug_data_dir, 'industry_output_new.txt')

            # tl.list_to_csv_file(full_supply_fn, self.V, '\t')
            tl.list_to_csv_file(full_use_fn, self.U, '\t')
            # tl.list_to_csv_file(full_finaldemand_fn, self.Y, '\t')
            # tl.list_to_csv_file(full_value_added_fn, self._sut.value_added, '\t') # notice value added not touched
            tl.list_to_csv_file(full_prd_supply_fn, product_out, '\t')
            tl.list_to_csv_file(full_prd_use_fn, product_in, '\t')
            tl.list_to_csv_file(full_ind_output_fn, np.transpose(industry_out), '\t')
            tl.list_to_csv_file(full_ind_input_fn, np.transpose(industry_in), '\t')

    def transformation_matrix(self):
        make = np.transpose(self.V)
        g = np.sum(self.V, axis=0)
        return np.dot(tl.invdiag(g), make)

    def io_transaction_matrix(self):
        use = self.U
        transaction_matrix = np.dot(use, self.transformation_matrix())

        if self.debug:
            full_transaction_output_fn = os.path.join(self.debug_data_dir, 'transaction_output_new.txt')
            tl.list_to_csv_file(full_transaction_output_fn, np.sum(transaction_matrix, axis=1, keepdims=True), '\t')
            print('transaction matrix ready and saved')
        print('transaction matrix ready')
        return transaction_matrix

    def io_coefficient_matrix(self):
        q = self.q
        return np.dot(self.io_transaction_matrix(), tl.invdiag(q))

    def ext_transaction_matrix(self):
        return np.dot(self._sut.extensions, self.transformation_matrix())

    def ext_coefficients_matrix(self):
        q = self.q
        return np.dot(self.ext_transaction_matrix(), tl.invdiag(q))

    def factor_inputs_transaction_matrix(self):
        return np.dot(self._sut.factor_inputs, self.transformation_matrix())

    def factor_inputs_coefficients_matrix(self):
        q = self.q
        return np.dot(self.factor_inputs_transaction_matrix(), tl.invdiag(q))

    def final_demand(self, fd=None):
        if fd is None:
            fd = self.Y
        return fd

    def io_total_requirement_matrix(self):
        A = self.io_coefficient_matrix()
        identity = np.identity(len(A))
        A = np.nan_to_num(A)
        return np.linalg.inv(identity - A)

    def check_io_transaction_matrix(self, rel_tol=default_rel_tol):
        is_correct = True
        q1 = np.sum(self.io_transaction_matrix(), axis=1) + \
            np.sum(self.Y, axis=1)
        q2 = np.sum(self.U, axis=1) + \
            np.sum(self.Y, axis=1)
        it = np.nditer(q1, flags=['f_index'])
        while not it.finished and is_correct:
            if not math.isclose(q1[it.index], q2[it.index], rel_tol=rel_tol):
                print(q1[it.index]- q2[it.index])
                is_correct = False
            it.iternext()
        return is_correct

    def check_io_coefficients_matrix(self, rel_tol=default_rel_tol):
        is_correct = True
        q1 = np.sum(self.io_transaction_matrix(), axis=1) + \
            np.sum(self.Y, axis=1)
        (row_cnt, col_cnt) = self.U.shape
        eye = np.diag(np.ones(row_cnt))
        l_inverse = np.linalg.inv(eye - self.io_coefficient_matrix())
        fd = np.sum(self.Y, axis=1)
        q2 = np.dot(l_inverse, fd)
        it = np.nditer(q1, flags=['f_index'])
        while not it.finished and is_correct:
            if not math.isclose(q1[it.index], q2[it.index], rel_tol=rel_tol):
                is_correct = False
            it.iternext()
        return is_correct

    def check_ext_transaction_matrix(self, rel_tol=default_rel_tol):
        is_correct = True
        e1 = np.sum(self._sut.extensions, axis=1)
        e2 = np.sum(self.ext_transaction_matrix(), axis=1)
        it = np.nditer(e1, flags=['f_index'])
        while not it.finished and is_correct:
            if not math.isclose(e1[it.index], e2[it.index], rel_tol=rel_tol):
                is_correct = False
            it.iternext()
        return is_correct

    def check_ext_coefficient_matrix(self, rel_tol=default_rel_tol):
        is_correct = True
        e1 = np.sum(self._sut.extensions, axis=1)
        ext = self.ext_coefficients_matrix()
        (row_cnt, col_cnt) = self.U.shape
        eye = np.diag(np.ones(row_cnt))
        l_inverse = np.linalg.inv(eye - self.io_coefficient_matrix())
        fd = np.sum(self.Y, axis=1)
        e2 = np.dot(ext, np.dot(l_inverse, fd))
        it = np.nditer(e1, flags=['f_index'])
        while not it.finished and is_correct:
            if not math.isclose(e1[it.index], e2[it.index], rel_tol=rel_tol):
                is_correct = False
            it.iternext()
        return is_correct
