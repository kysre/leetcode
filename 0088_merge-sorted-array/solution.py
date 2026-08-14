from typing import List


class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        if n == 0:
            return
        if m == 0:
            for i in range(n):
                nums1[i] = nums2[i]
            return
        i = m - 1 if m > 0 else 0
        j = n - 1
        for k in range(m + n):
            if nums2[j] >= nums1[i]:
                nums1[m + n - k - 1] = nums2[j]
                j -= 1
            else:
                nums1[m + n - k - 1] = nums1[i]
                nums1[i] = -999999
                if i > 0:
                    i -= 1

            if j < 0:
                break
