"""
# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
"""

from typing import List


class Solution:
    def connect(self, root: "Node") -> "Node":
        if root is None:
            return
        old_list = [root]
        final_list = [root]
        while True:
            new_list = self.process_depth(old_list)
            final_list.append(None)
            if len(new_list) == 0:
                break
            old_list = new_list
            for x in old_list:
                final_list.append(x)
        return root

    def process_depth(self, node_list) -> List:
        new_list = []
        for i in range(len(node_list) - 1):
            node_list[i].next = node_list[i + 1]
        node_list[-1].next = None
        for i in range(len(node_list)):
            l, r = node_list[i].left, node_list[i].right
            if l is not None:
                new_list.append(l)
            if r is not None:
                new_list.append(r)
        return new_list
