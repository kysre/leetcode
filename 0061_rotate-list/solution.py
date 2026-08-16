from typing import Optional


# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if head is None or head.next is None:
            return head
        n = 1
        tail = head
        while True:
            if tail.next is None:
                break
            else:
                n += 1
                tail = tail.next
        rotations = k % n
        if rotations == 0:
            return head
        new_tail = head
        new_head = None
        for i in range(n - rotations - 1):
            new_tail = new_tail.next
        new_head = new_tail.next
        new_tail.next = None
        tail.next = head
        return new_head


if __name__ == "__main__":
    solution = Solution()
    head = ListNode(0)
    head.next = ListNode(1)
    head.next.next = ListNode(2)
    k = 4
    new_head = solution.rotateRight(head, k)
    print_str = ""
    while new_head is not None:
        print_str += str(new_head.val) + " "
        new_head = new_head.next
    print(print_str)
