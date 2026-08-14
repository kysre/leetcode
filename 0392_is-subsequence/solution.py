class Solution:
    def isSubsequence(self, s: str, t: str) -> bool:
        if s == "":
            return True
        n = len(s)
        i = 0
        for x in t:
            if x == s[i]:
                i += 1
            if i == n:
                return True
        return False
