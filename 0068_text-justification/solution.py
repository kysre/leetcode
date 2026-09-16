class Solution:
    def fullJustify(self, words: list[str], maxWidth: int) -> list[str]:
        out = []
        i = 0
        while i < len(words):
            words_to_add = []
            total_len = 0
            while True:
                if i >= len(words):
                    break
                if total_len + len(words[i]) <= maxWidth:
                    words_to_add.append(words[i])
                    total_len += len(words[i]) + 1
                    i += 1
                else:
                    break

            if i == len(words):
                s_out = ""
                for w in words_to_add:
                    s_out += w + " "
                s_out += " " * maxWidth
                out.append(s_out[:maxWidth])
                break

            word_cnt = len(words_to_add)
            if word_cnt == 1:
                w = words_to_add[0] + " " * maxWidth
                out.append(w[:maxWidth])
                continue

            space_count = (maxWidth - total_len + word_cnt) // (word_cnt - 1)
            space_remainder = (maxWidth - total_len + word_cnt) % (word_cnt - 1)
            s_out = words_to_add[0]
            for j in range(1, word_cnt):
                s_out += " " * space_count
                if space_remainder > 0:
                    s_out += " "
                    space_remainder -= 1
                s_out += words_to_add[j]
            out.append(s_out)
        return out
