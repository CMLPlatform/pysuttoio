import csv
import pickle as pck
import numpy as np


def pickle_file_to_list(filename):
    """
    A function that opens a filename and read the contents and
    restuns the data as list of the picklefile contained a list

    :param filename : str
        Full qualified filename
    :return: list
        Contents of the picklefile
    """
    with open(filename, 'rb') as picklefile:
        return pck.load(picklefile)


def list_to_pickle_file(filename, list_data):
    """
    A function to save data in a (nested) list to a pickle file.

    :param filename : str
            Full qualified filename. Contents in an existing file
            will be overwritten without warning
    :param list_data : list
            The data in the form of a (nested) list to be saved
            in the pickle file
    """
    with open(filename, 'wb') as picklefile:
        pck.dump(list_data, picklefile)


def list_to_csv_file(filename, list_data, delimiter=','):
    """
    A function to save data in a two dimensional list (list of lists) to
    a csv file.

    :param filename : str
            Full qualified filename. Contents in an existing file
            will be overwritten without warning
    :param list_data : list
            The data in the form of a list of lists to be saved
            csv file
    :param delimiter : str, optional
            The string to be used as delimiter. Default
            value is ','.
    """
    file = open(filename, 'w')
    for row in list_data:
        for item in row[:-1]:
            file.write('{}'.format(item) + delimiter)
        file.write('{}\n'.format(row[-1]))
    file.close()


def invdiag(data):
    """
    A function that takes a vector of values. Calculates
    the reciprocal of each value and returns a diagonalised
    matrix of these reciprocals. Zero values remain zero.

    :param data : numpy array
            The vector of values to be converted into an
            inverse diagonalized matrix. Should have one dimension
            only.
    :return: numpy array
            The matrix containing the inverse diagonalized values.
    """
    result = np.zeros(data.shape)
    for index in np.ndindex(data.shape):
        if data[index] != 0:
            result[index] = 1 / data[index]
    return np.diag(result)


def list_to_numpy_array(list_data, row_header_cnt, col_header_cnt):
    """
    Takes a list of lists that contains a table with row and column headers
    and values, and extracts the numerical values and returns these values
    as two dimensional numpy array.

    :param list_data: list
            The table data, optional including row and column headers, in the form
            of a list of lists
    :param row_header_cnt: int
            The number of top rows occupied by the column header labels
    :param col_header_cnt: int
            The first number of columns occopied by the row header labels
    :return: numpy array
            Two dimensional numpy array containing double floating point values.
    """
    matrix = []
    row_idx = 0
    for list_row in list_data:
        if row_idx >= col_header_cnt:  # skip rows with column headers
            matrix.append(list_row[row_header_cnt:len(list_row)])
        row_idx += 1
    return np.asarray(matrix, dtype=np.double)


def csv_file_to_list(filename, delimiter=','):
    """
    This function reads a csv file and returns the contents as
    a list of lists.

    :param filename : str
            Full qualified filename.
    :param delimiter : str, optional
            The string to be used as delimiter. Default
            value is ','.
    :return: list
            The content of the csv file in a list of lists
    """
    with open(filename) as f:
        reader = csv.reader(f, delimiter=delimiter)
        d = list(reader)
    return d


def get_row_header(list_data, row_header_cnt, col_header_cnt):
    """
    Takes a list of lists that contains a table with row and column headers
    and values, and extracts the row header labels
    as a list of lists.

    :param list_data:  list
            The table data, including row and column headers, in the form
            of a list of lists
    :param row_header_cnt: int
            The number of top rows occupied by the column header labels
    :param col_header_cnt: int
            The first number of columns occopied by the row header labels
    :return: list
            The row headers. The original orientation is kept.
    """
    headers = list()
    row_idx = 0
    for list_row in list_data:
        if row_idx >= col_header_cnt:  # skip rows with column headers
            headers.append(list_row[0:row_header_cnt])
        row_idx += 1
    return headers


def get_column_header(list_data, row_header_cnt, col_header_cnt):
    """
    :param list_data:  list
            The table data, including row and column headers, in the form
            of a list of lists
    :param row_header_cnt: int
            The number of top rows occupied by the column header labels
    :param col_header_cnt: int
            The first number of columns occopied by the row header labels
    :returns: list
            The columns headers. The original orientation is kept.
    """
    headers = list()
    for row_idx in range(0, col_header_cnt):  # only read column headers
        temp_row = list_data[row_idx]
        temp_row = temp_row[row_header_cnt:len(temp_row)]  # skip row headers
        items = list()
        for item in temp_row:
            items.append(item)
        headers.append(items)
    headers = np.transpose(headers)
    return headers.tolist()


def remove_duplicates(labels):
    unique_list = []

    for elem in labels:
        if elem not in unique_list:
            unique_list.append(elem)

    return unique_list
