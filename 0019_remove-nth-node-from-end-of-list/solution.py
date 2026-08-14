# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next


class Solution(object):
    def removeNthFromEnd(self, head, n):
        stack = []
        node = head
        while node.next is not None:
            stack.append(node)
            node = node.next
        stack.append(node)
        if n == len(stack):
            return head.next
        if n == 1:
            stack[-n - 1].next = None
        else:
            stack[-n - 1].next = stack[-n + 1]
        return head
