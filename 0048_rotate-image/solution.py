import math
from typing import List


class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        n = len(matrix)
        for i in range(math.ceil(n / 2)):
            for j in range(math.floor(n / 2)):
                matrix[j][n - 1 - i], temp = matrix[i][j], matrix[j][n - 1 - i]
                matrix[n - 1 - i][n - 1 - j], temp = temp, matrix[n - 1 - i][n - 1 - j]
                matrix[n - 1 - j][i], temp = temp, matrix[n - 1 - j][i]
                matrix[i][j] = temp
