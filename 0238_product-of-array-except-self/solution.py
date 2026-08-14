# Date: 2022-06-08
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        nums_dic = {}
        for i in range(len(nums)):
            nums_dic[nums[i]] = i
        for i in range(len(nums)):
            look_for = target - nums[i]
            if look_for in nums_dic and nums_dic[look_for] != i:
                return [i, nums_dic[look_for]]
