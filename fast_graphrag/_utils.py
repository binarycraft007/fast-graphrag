import asyncio
import logging
from typing import List, Tuple, Union

import numpy as np
import numpy.typing as npt
from scipy.sparse import csr_matrix

from fast_graphrag._types import TIndex

logger = logging.getLogger("graphrag")
TOKEN_TO_CHAR_RATIO = 4


def get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        # If there is already an event loop, use it.
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If in a sub-thread, create a new event loop.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def extract_sorted_scores(row_vector: csr_matrix) -> Tuple[npt.NDArray[np.int64], npt.NDArray[np.float32]]:
    """Take a sparse row vector and return a list of non-zero (index, score) pairs sorted by score."""
    assert row_vector.shape[0] <= 1, "The input matrix must be a row vector."
    if row_vector.shape[0] == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.float32)

    # Step 1: Get the indices of non-zero elements
    non_zero_indices = row_vector.nonzero()[1]

    # Step 2: Extract the probabilities of these indices
    probabilities = row_vector.data

    # Step 3: Use NumPy to create arrays for indices and probabilities
    indices_array = np.array(non_zero_indices)
    probabilities_array = np.array(probabilities)

    # Step 4: Sort the probabilities and get the sorted indices
    sorted_indices = np.argsort(probabilities_array)[::-1]

    # Step 5: Create sorted arrays for indices and probabilities
    sorted_indices_array = indices_array[sorted_indices]
    sorted_probabilities_array = probabilities_array[sorted_indices]

    return sorted_indices_array, sorted_probabilities_array


def csr_from_indices_list(
    data: List[List[Union[int, TIndex]]], shape: Tuple[int, int]
) -> csr_matrix:
    """Create a CSR matrix from a list of lists."""
    num_rows = len(data)

    # Flatten the list of lists and create corresponding row indices
    row_indices = np.repeat(np.arange(num_rows), [len(row) for row in data])
    col_indices = np.concatenate(data) if num_rows > 0 else np.array([], dtype=np.int64)

    # Data values (all ones in this case)
    values = np.broadcast_to(1, len(row_indices))

    # Create the CSR matrix
    return csr_matrix((values, (row_indices, col_indices)), shape=shape)