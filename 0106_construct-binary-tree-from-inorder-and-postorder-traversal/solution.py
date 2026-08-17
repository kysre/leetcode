from typing import List, Optional


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        if len(inorder) == 0:
            return None
        parent = postorder[-1]
        parent_index = inorder.index(parent)
        subtree_left_inorder = inorder[:parent_index]
        subtree_left_postorder = postorder[: len(subtree_left_inorder)]
        subtree_right_inorder = inorder[parent_index + 1 :]
        subtree_right_postorder = postorder[len(subtree_left_inorder) : -1]
        left = self.buildTree(subtree_left_inorder, subtree_left_postorder)
        right = self.buildTree(subtree_right_inorder, subtree_right_postorder)
        return TreeNode(parent, left, right)
