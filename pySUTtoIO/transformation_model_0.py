import numpy as np
import math
import sut as st
import matrix_inverter as mi
from secondary_flows import make_secondary

class TransformationModel0:

    default_rel_tol = 1E-3

    def __init__(self, sut, env_extensions, make_secondary=False):
        assert type(sut) is st.Sut
        self._sut = sut
        self._ext = env_extensions

    def V_U_with_secondary(self, supply, use, final_demand):
        sut = make_secondary(self._sut)
        return sut

    def io_matrix_model_0(self, make_secondary):
        if make_secondary is True:
            intermediate_use = self.V_U_with_secondary.use
            intermediate_supply = self.V_U_with_secondary.supply
        elif make_secondary is False:
            intermediate_use = self._sut.domestic_use
            intermediate_supply = self._sut.supply

        net_supply = self._sut.supply - intermediate_use

        return net_supply

    def ext_transaction_matrix(self):
        return self._ext

    def final_demand(self, fd=None):
        if fd is None:
            fd = self._sut.domestic_final_use
        return fd

    def check_io_matrix(self, rel_tol=default_rel_tol):
        is_correct = True
        # in this case a scaling vector is calculated. If the net-supply matrix is correct
        # it would contains 1s (or zero if product is absent)
        total_final_use = np.sum(self._sut.domestic_final_use, axis=1)
        s = np.dot(mi.inverse(self.io_matrix_model_0()), total_final_use)
        it = np.nditer(s, flags=['f_index'])
        while not it.finished and is_correct:
            if not (math.isclose(s[it.index], 1, rel_tol=rel_tol) or math.isclose(s[it.index], 0, rel_tol=rel_tol)):
                is_correct = False
            it.iternext()
        return is_correct

    def check_ext_matrix(self, rel_tol=default_rel_tol):
        is_correct = True
        e1 = np.sum(self._ext, axis=1)
        total_final_use = np.sum(self._sut.domestic_final_use, axis=1)
        q2 = np.dot(mi.inverse(self.io_matrix_model_0()), total_final_use)
        e2 = np.dot(self._ext, q2)
        it = np.nditer(e1, flags=['f_index'])
        while not it.finished and is_correct:
            if not math.isclose(e1[it.index], e2[it.index], rel_tol=rel_tol):
                is_correct = False
            it.iternext()
        return is_correct


def _invdiag(data):
    result = np.zeros(data.shape)
    for index in np.ndindex(data.shape):
        if data[index] != 0:
            result[index] = 1 / data[index]
    return np.diag(result)
