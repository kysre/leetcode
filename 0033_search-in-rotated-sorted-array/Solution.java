
class Solution {

    public static void main(String[] args) {
        int[] nums = new int[]{10, 0, 1, 3, 4, 5, 6};
        int target = 4;
        System.out.println(new Solution().search(nums, target));
    }

    public int search(int[] nums, int target) {
        int k = this.findK(nums);
        int n = nums.length;
        int left = 0;
        int right = n;
        while (left < right) {
            int mid = (left + right) / 2;
            int midRotatedIndex = this.getRotatedIndex(mid, k, n);
            if (nums[midRotatedIndex] == target) {
                return midRotatedIndex;
            } else if (nums[midRotatedIndex] > target) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return -1;
    }

    private int getRotatedIndex(int index, int k, int n) {
        return (index + k) % n;
    }

    private int findK(int[] nums) {
        int lo = 0, hi = nums.length - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (nums[mid] > nums[hi]) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}
