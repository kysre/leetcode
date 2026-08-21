from typing import List


class Solution:
    # DP solution / O(m*n)
    def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
        n, m = len(obstacleGrid), len(obstacleGrid[0])
        # Handle corner cases
        if obstacleGrid[0][0] == 1 or obstacleGrid[n - 1][m - 1] == 1:
            return 0
        # Create DP memory & set base case
        DP = [[0] * m for i in range(n)]
        for i in range(n):
            if obstacleGrid[i][0] == 1:
                break
            DP[i][0] = 1
        for j in range(m):
            if obstacleGrid[0][j] == 1:
                break
            DP[0][j] = 1
        # Calculate DP
        for i in range(1, n):
            for j in range(1, m):
                if obstacleGrid[i][j] == 1:
                    DP[i][j] = 0
                else:
                    DP[i][j] = DP[i - 1][j] + DP[i][j - 1]
        # Return answer
        return DP[n - 1][m - 1]

    # DFS solution / exceeds time limit / O(2^(m+n))
    def dfs_solution(self, obstacleGrid: List[List[int]]) -> int:
        n, m = len(obstacleGrid), len(obstacleGrid[0])

        def is_goal(i, j) -> bool:
            return i == n - 1 and j == m - 1

        if obstacleGrid[0][0] == 1 or obstacleGrid[n - 1][m - 1] == 1:
            return 0

        stack = [(0, 0)]
        cnt = 0
        while len(stack) > 0:
            x, y = stack.pop()
            if is_goal(x, y):
                cnt += 1
            if x + 1 < n and obstacleGrid[x + 1][y] == 0:
                stack.append((x + 1, y))
            if y + 1 < m and obstacleGrid[x][y + 1] == 0:
                stack.append((x, y + 1))

        return cnt
