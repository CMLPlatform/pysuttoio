import numpy as np


def inverse(matrix):
    assert type(matrix) is np.ndarray
    assert matrix.dtype == np.float64
    assert matrix.ndim == 2
    (row_cnt, col_cnt) = matrix.shape
    assert col_cnt == row_cnt
    (empty_row, empty_col) = _detect_empty(matrix)
    reduced_matrix = _remove_empty(matrix, empty_row, empty_col)
    inverse_reduced_matrix = np.linalg.inv(reduced_matrix)
    inverse_full_matrix = _insert_empty(inverse_reduced_matrix, empty_row, empty_col)
    return inverse_full_matrix


def _insert_empty(reduced_matrix, empty_row, empty_col):
    # setting columns in correct position
    (reduced_row_cnt, reduced_col_cnt) = reduced_matrix.shape
    row_reduced_matrix = np.zeros((reduced_row_cnt, empty_col.size))
    reduced_col_idx = 0
    full_col_idx = 0
    for empty in empty_col:
        if not empty:
            row_reduced_matrix[:, full_col_idx] = reduced_matrix[:, reduced_col_idx]
            reduced_col_idx = reduced_col_idx + 1
        full_col_idx = full_col_idx + 1

    # setting rows in correct position
    full_matrix = np.zeros((empty_row.size, empty_col.size))
    reduced_row_idx = 0
    full_row_idx = 0
    for empty in empty_row:
        if not empty:
            full_matrix[full_row_idx, :] = row_reduced_matrix[reduced_row_idx, :]
            reduced_row_idx = reduced_row_idx + 1
        full_row_idx = full_row_idx + 1

    return full_matrix


def _remove_empty(matrix, empty_row, empty_col):
    row_reduced_matrix = matrix[~np.array(empty_row)]
    reduced_matrix = row_reduced_matrix[:, ~np.array(empty_col)]
    return reduced_matrix


def _detect_empty(matrix):
    # detect rows and columns completely filled with zeros
    empty_cols = np.all(matrix == 0, axis=0)
    empty_rows = np.all(matrix == 0, axis=1)

    # check if number of empty rows matches number of empty colums
    empty_cols_cnt = np.count_nonzero(empty_cols)
    empty_rows_cnt = np.count_nonzero(empty_rows)
    assert empty_cols_cnt == empty_rows_cnt

    # return the boolean arrays
    return empty_rows, empty_cols
