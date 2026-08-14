# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution(object):
    def reverseList(self, head):
        if head is None:
            return head
        previous_node = None
        while head.next is not None:
            next_node = head.next
            head.next = previous_node
            previous_node = head
            head = next_node
        head.next = previous_node
        return head
