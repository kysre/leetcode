from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseBetween(
        self, head: Optional[ListNode], left: int, right: int
    ) -> Optional[ListNode]:
        if left == right:
            return head
        # Put nodes to reverse in stack
        stack = []
        node, i = head, 1
        last_node_before_reversed = node
        while True:
            if i > right:
                break
            if i < left:
                last_node_before_reversed = node
            if i >= left:
                stack.append(node)
            if node.next is not None:
                node = node.next
            i += 1
        # Set after and before node reversing
        first_node, head_to_return, last_reversed = head, None, stack[-1]
        first_node_after_reversed = last_reversed.next
        if left == 1:
            head_to_return = last_reversed
            first_node.next = last_reversed.next
        else:
            head_to_return = first_node
            last_node_before_reversed.next = last_reversed
        # Reverse nodes
        top = stack.pop()
        while len(stack) > 0:
            next_node = stack.pop()
            top.next = next_node
            top = next_node
        top.next = first_node_after_reversed
        return head_to_return
