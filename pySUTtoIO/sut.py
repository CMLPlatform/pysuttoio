import numpy as np


class Sut:
    """A data transfer object that contains data from one supply-use table."""

    __prd_cnt = 200
    __ind_cnt = 163
    __fd_cnt = 7
    __cntr_cnt = 49
    __value_added_index = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def __init__(self):
        self._year = None
        self._supply = None
        self._use = None
        self._final_use = None
        self._factor_inputs = None
        self._extensions = None
        self._direct_extensions = None
        self._product_categories = None
        self._industry_categories = None
        self._final_use_categories = None
        self._factor_input_categories = None
        self._extension_categories = None

    @property
    def product_categories(self):
        return self._product_categories

    @property
    def industry_categories(self):
        return self._industry_categories

    @property
    def finaluse_categories(self):
        return self._final_use_categories

    @property
    def factor_input_categories(self):
        return self._factor_input_categories

    @property
    def extension_categories(self):
        return self._extension_categories

    @product_categories.setter
    def product_categories(self, categories):
        assert type(categories) is list
        self._product_categories = categories

    @industry_categories.setter
    def industry_categories(self, categories):
        assert type(categories) is list
        self._industry_categories = categories

    @finaluse_categories.setter
    def finaluse_categories(self, categories):
        assert type(categories) is list
        self._final_use_categories = categories

    @factor_input_categories.setter
    def factor_input_categories(self, categories):
        assert type(categories) is list
        self._factor_input_categories = categories

    @extension_categories.setter
    def extension_categories(self, categories):
        assert type(categories) is list
        self._extension_categories = categories

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, yr):
        assert type(yr) is int
        self._year = yr

    @property
    def supply(self):
        return self._supply

    @supply.setter
    def supply(self, sup):
        assert type(sup) is np.ndarray
        assert sup.dtype == np.float64
        assert sup.shape == (self.__prd_cnt * self.__cntr_cnt, self.__ind_cnt * self.__cntr_cnt)
        self._supply = sup

    @property
    def use(self):
        return self._use

    @use.setter
    def use(self, use):
        assert type(use) is np.ndarray
        assert use.dtype == np.float64
        assert use.shape == (self.__prd_cnt * self.__cntr_cnt, self.__ind_cnt * self.__cntr_cnt)
        self._use = use

    @property
    def final_use(self):
        return self._final_use

    @final_use.setter
    def final_use(self, final_use):
        assert type(final_use) is np.ndarray
        assert final_use.dtype == np.float64
        assert final_use.shape == (self.__prd_cnt * self.__cntr_cnt,  self.__fd_cnt * self.__cntr_cnt)
        self._final_use = final_use

    @property
    def factor_inputs(self):
        return self._factor_inputs

    @factor_inputs.setter
    def factor_inputs(self, factor_inputs):
        assert type(factor_inputs) is np.ndarray
        assert factor_inputs.dtype == np.float64
        self._factor_inputs = factor_inputs

    @property
    def value_added(self):
        return self._factor_inputs[self.__value_added_index, :]

    @property
    def total_product_supply(self):
        return np.sum(self._supply, axis=1)

    @property
    def total_product_use(self):
        return np.sum(self._use, axis=1) + np.sum(self._final_use, axis=1)

    @property
    def total_industry_output(self):
        return np.sum(self._supply, axis=0)

    @property
    def total_industry_input(self):
        return np.sum(self._use, axis=0) + np.sum(self.value_added, axis=0)

    @property
    def extensions(self):
        return self._extensions

    @property
    def direct_extensions(self):
        return self._direct_extensions

    @extensions.setter
    def extensions(self, data):
        assert type(data) is np.ndarray
        assert data.dtype == np.float64
        self._extensions = data

    @direct_extensions.setter
    def direct_extensions(self, data):
        assert type(data) is np.ndarray
        assert data.dtype == np.float64
        self._direct_extensions = data
