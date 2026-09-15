from queue import PriorityQueue


class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        pq = PriorityQueue()
        for num in nums:
            pq.put(num)
            if pq.qsize() > k:
                pq.get()
        return pq.get()
