
class Solution {

    public static void main(String[] args) {
        System.out.println(
                new Solution().findMedianSortedArrays(
                        new int[]{1, 5},
                        new int[]{}
                )
        );
    }

    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        int n = nums1.length, m = nums2.length;
        int[] allNums = new int[n + m];
        int i = 0, j = 0;
        while (i < n || j < m) {
            if (i == n) {
                allNums[i + j] = nums2[j];
                j += 1;
            } else if (j == m) {
                allNums[i + j] = nums1[i];
                i += 1;
            } else if (nums1[i] < nums2[j]) {
                allNums[i + j] = nums1[i];
                i += 1;
            } else {
                allNums[i + j] = nums2[j];
                j += 1;
            }
        }
        int medianIndex = (n + m) / 2 - 1;
        if ((n + m) % 2 == 0) {
            return ((double) (allNums[medianIndex] + allNums[medianIndex + 1])) / 2;
        }
        return allNums[medianIndex + 1];
    }
}
