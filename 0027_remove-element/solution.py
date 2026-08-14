from typing import List


class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        k = 0
        i = 0
        for num in nums:
            if num == val:
                k += 1
            else:
                nums[i - k] = num
            i += 1
        return i - k
