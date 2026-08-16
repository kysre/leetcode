class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        # Return edge cases
        if not word1:
            return len(word2)
        if not word2:
            return len(word1)
        # Setup memory
        n = len(word1)
        m = len(word2)
        mem = [[0] * (m + 1) for i in range(n + 1)]
        # Setup boundry conditions
        for i in range(n, -1, -1):
            mem[i][m] = n - i
        for j in range(m, -1, -1):
            mem[n][j] = m - j
        # Solve DP
        for i in range(n - 1, -1, -1):
            for j in range(m - 1, -1, -1):
                # Calculate cost
                if word1[i] == word2[j]:
                    mem[i][j] = mem[i + 1][j + 1]
                else:
                    mem[i][j] = min(mem[i][j + 1], mem[i + 1][j], mem[i + 1][j + 1]) + 1
        # Return answer
        return mem[0][0]
