from typing import Optional, Tuple


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        if root is not None:
            self.flatten_subtree(root)

    # O(n) memory usage
    def flatten_subtree_with_memory(self, root: Optional[TreeNode]):
        preorder = self.preorder_dfs(root)
        for i in range(len(preorder) - 1):
            preorder[i].right = preorder[i + 1]
            preorder[i].left = None

    def preorder_dfs(self, root):
        preorder = []
        stack = [root]
        while len(stack) > 0:
            node = stack.pop()
            preorder.append(node)
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
        return preorder

    # O(1) memory usage
    def flatten_subtree(
        self, root: Optional[TreeNode]
    ) -> Optional[Tuple[TreeNode, TreeNode]]:
        left_subtree = root.left
        right_subtree = root.right
        if left_subtree is None and right_subtree is None:
            return root, root
        elif left_subtree is None:
            right_subtree_start, right_subtree_end = self.flatten_subtree(right_subtree)
        elif right_subtree is None:
            right_subtree_start, right_subtree_end = self.flatten_subtree(left_subtree)
            root.right = right_subtree_start
        else:
            left_subtree_start, left_subtree_end = self.flatten_subtree(left_subtree)
            right_subtree_start, right_subtree_end = self.flatten_subtree(right_subtree)
            root.right = left_subtree_start
            left_subtree_end.right = right_subtree_start
        root.left = None
        return root, right_subtree_end
