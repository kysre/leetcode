class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if len(nums) < 3:
            return len(nums)
        i, j, k, n = 0, 0, 0, len(nums)
        while j < n:
            if j < n - 1 and nums[j] != nums[j + 1]:
                nums[i] = nums[j]
                i += 1
                j += 1
                k += 1
                continue
            nums[i] = nums[j]
            i += 1
            j += 1
            k += 1
            if j == n:
                break
            while j < n - 1 and nums[j] == nums[j + 1]:
                j += 1
            nums[i] = nums[j]
            i += 1
            j += 1
            k += 1
        return k
