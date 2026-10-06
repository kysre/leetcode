class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        last_word_len = 0
        last_whitespace_index = -1
        for i in range(len(s)):
            if s[i] == " ":
                last_whitespace_index = i
            else:
                last_word_len = i - last_whitespace_index
        return last_word_len
