from typing import List


class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        i_sets = [set(), set(), set(), set(), set(), set(), set(), set(), set()]
        j_sets = [set(), set(), set(), set(), set(), set(), set(), set(), set()]
        ij_sets = [set(), set(), set(), set(), set(), set(), set(), set(), set()]
        for i in range(9):
            for j in range(9):
                c = board[i][j]
                if c != ".":
                    if c in i_sets[i]:
                        return False
                    else:
                        i_sets[i].add(c)
                    if c in j_sets[j]:
                        return False
                    else:
                        j_sets[j].add(c)
                    ij_indice = i // 3 + (j // 3) * 3
                    if c in ij_sets[ij_indice]:
                        return False
                    else:
                        ij_sets[ij_indice].add(c)
        return True
