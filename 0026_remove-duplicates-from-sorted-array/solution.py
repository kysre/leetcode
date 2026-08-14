from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        n = len(nums)
        i, j, k = 0, 1, 1
        while j < n:
            if nums[i] != nums[j]:
                nums[k] = nums[j]
                k += 1
                i = j
                j += 1
            else:
                while j < n:
                    if nums[i] == nums[j]:
                        j += 1
                    else:
                        break
        return k
