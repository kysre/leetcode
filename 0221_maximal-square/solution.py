from typing import List


class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        m, n = len(matrix), len(matrix[0])
        DP = [[0] * n for i in range(m)]
        max_area = 0
        for i in range(m):
            for j in range(n):
                if matrix[i][j] == "1":
                    if i == 0 or j == 0:
                        DP[i][j] = 1
                    else:
                        DP[i][j] = min(DP[i - 1][j], DP[i][j - 1], DP[i - 1][j - 1]) + 1
                    max_area = max(max_area, DP[i][j] * DP[i][j])
        return max_area
