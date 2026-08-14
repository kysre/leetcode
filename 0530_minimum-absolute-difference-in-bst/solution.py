# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
from typing import Optional


class Solution:
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        ordered_list = self.get_ordered_children_val(root)
        if len(ordered_list) == 1:
            return ordered_list[0]
        min_dif = abs(ordered_list[0] - ordered_list[1])
        for i in range(len(ordered_list) - 1):
            dif = abs(ordered_list[i] - ordered_list[i + 1])
            if dif < min_dif:
                min_dif = dif
        return min_dif

    def get_ordered_children_val(self, node):
        children = []
        if node.left is not None:
            children.extend(self.get_ordered_children_val(node.left))
        children.append(node.val)
        if node.right is not None:
            children.extend(self.get_ordered_children_val(node.right))
        return children
