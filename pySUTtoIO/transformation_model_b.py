import math
import numpy as np
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

    def __init__(self, sut, make_secondary):
        assert type(sut) is st.Sut

        self._sut = sut

        if make_secondary is True:
            sut2 = ms(sut)
            self.V = sut2.supply
            self.U = sut2.use
            np.savetxt("use.csv", self.U)
            self.q = np.sum(self.V, axis=1)
            self.Y = sut2.final_use

        else:
            self.V = self._sut.supply
            self.U = self._sut.use
            self.q = self._sut.total_product_supply
            self.Y = self._sut.final_use

    def transformation_matrix(self):
        make = np.transpose(self.V)
        g_orig = self._sut.total_industry_output
        g1 = np.sum(self.V, axis=0)
        g2 = np.sum(self.U, axis=0) + np.sum(self._sut.value_added, axis=0)
        np.savetxt("g1.txt", g1)
        np.savetxt("g2.txt", g2)
        np.savetxt("g_orig.txt", g_orig)
        return np.dot(tl.invdiag(g_orig), make)

    def io_transaction_matrix(self):
        use = self.U
        return np.dot(use, self.transformation_matrix())

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
        q_orig = np.sum(self.V, axis=1)
        np.savetxt("q_orig.txt", q_orig)
        q1 = np.sum(self.io_transaction_matrix(), axis=1) + \
            np.sum(self.Y, axis=1)
        np.savetxt("q1.txt", q1)
        q2 = np.sum(self.U, axis=1) + \
            np.sum(self.Y, axis=1)
        np.savetxt("q2.txt", q2)
        it = np.nditer(q1, flags=['f_index'])
        while not it.finished and is_correct:
            if not math.isclose(q1[it.index], q2[it.index], rel_tol=rel_tol):
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
#                np.savetxt("e1", e1)
#                np.savetxt("e2", e2)
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
