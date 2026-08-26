class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        self.rotate_3(nums, k)

    # Time: O(n), Memory: O(n)
    def rotate_1(self, nums, k):
        n = len(nums)
        k %= n
        nums_c = nums.copy()
        for i in range(n):
            nums[i] = nums_c[(n - k + i) % n]

    # Time: O(n), Memory: O(k)
    def rotate_2(self, nums, k):
        n = len(nums)
        k %= n
        knums = nums[n - k :]
        for i in range(k):
            j = 0
            temp = knums[i]
            while j * k + i < n:
                t = nums[j * k + i]
                nums[j * k + i] = temp
                temp = t
                j += 1

    # Time: O(n), Memory: O(1)
    def rotate_3(self, nums, k):
        n = len(nums)
        k %= n
        if k == 0:
            return
        if n % k == 0:
            for i in range(k):
                j = 0
                temp = nums[n - k + i]
                while j * k + i < n:
                    t = nums[j * k + i]
                    nums[j * k + i] = temp
                    temp = t
                    j += 1
        else:
            cnt, i, start_index = 0, 0, 0
            temp = nums[n - k]
            while cnt < n:
                t = nums[i]
                nums[i] = temp
                temp = t
                i += k
                i %= n
                if i == start_index:
                    i += 1
                    start_index = i
                    temp = nums[n - k + i]
                cnt += 1

    # Time Limit Exceeds, Time: O(nk), Memory: O(1)
    def rotate_wrong(self, nums, k):
        n = len(nums)
        k %= n
        for _ in range(k):
            temp = nums[0]
            for i in range(n - 1):
                t = nums[i + 1]
                nums[i + 1] = temp
                temp = t
            nums[0] = temp
