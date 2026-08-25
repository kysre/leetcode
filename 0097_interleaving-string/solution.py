class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        # Check edge cases
        if s3 == "":
            return s1 == "" and s2 == ""
        n, m = len(s1), len(s2)
        if n + m != len(s3):
            return False
        # Init DP
        DP = [[False] * (n + 1) for i in range(m + 1)]
        DP[m][n] = True
        # Calculate DP
        for i in range(m, -1, -1):
            for j in range(n, -1, -1):
                if i + j == n + m:
                    continue
                if i < m and DP[i + 1][j] and s3[i + j] == s2[i]:
                    DP[i][j] = True
                if j < n and DP[i][j + 1] and s3[i + j] == s1[j]:
                    DP[i][j] = True
        # Return answer case
        return DP[0][0]

    # Recursive implementation. Passes 106/107 testcases
    def isInterleaveRecursive(self, s1: str, s2: str, s3: str) -> bool:
        if len(s1) + len(s2) != len(s3):
            return False
        if len(s1) == 0 and len(s2) == 0 and len(s3) == 0:
            return True
        n = 0
        while len(s1) - n > 0 and len(s3) - n > 0 and s1[n] == s3[n]:
            n += 1
            if len(s1) > n and s1[n] != s1[n - 1]:
                break
        if n > 0 and self.isInterleave(s1[n:], s2, s3[n:]):
            return True
        n = 0
        while len(s2) - n > 0 and len(s3) - n > 0 and s2[n] == s3[n]:
            n += 1
            if len(s2) > n and s2[n] != s2[n - 1]:
                break
        if n > 0 and self.isInterleave(s1, s2[n:], s3[n:]):
            return True
        return False


if __name__ == "__main__":
    s1 = "abababababababababababababababababababababababababababababababababababababababababababababababababbb"
    s2 = "babababababababababababababababababababababababababababababababababababababababababababababababaaaba"
    s3 = "abababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababbb"
    print(Solution().isInterleave(s1, s2, s3))  # Output: True
