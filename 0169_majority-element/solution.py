from typing import List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        cnt_dict = {}
        for num in nums:
            if num not in cnt_dict.keys():
                cnt_dict[num] = 0
            cnt_dict[num] = cnt_dict[num] + 1
        least_cnt = int(len(nums) / 2)
        chosen_num = 0
        chosen_cnt = 0
        for num in cnt_dict.keys():
            if cnt_dict[num] >= least_cnt and cnt_dict[num] > chosen_cnt:
                chosen_num = num
                chosen_cnt = cnt_dict[num]
        return chosen_num
