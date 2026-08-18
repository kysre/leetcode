class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        n = len(nums)
        nums.sort()
        nums_dict = {}
        for i in range(n):
            if nums[i] not in nums_dict:
                nums_dict[nums[i]] = i
        ans = set()
        for i in range(n):
            for j in range(i):
                to_3sum = 0 - (nums[i] + nums[j])
                if to_3sum in nums_dict and nums_dict[to_3sum] < j:
                    ans.add((to_3sum, nums[j], nums[i]))
        ans_final = []
        for a in ans:
            ans_final.append(list(a))
        return ans_final
