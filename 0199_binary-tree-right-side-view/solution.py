class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def rightSideView(self, root: TreeNode | None) -> list[int]:
        if root is None:
            return []
        stack = [(root, 0)]
        view = []
        while len(stack) > 0:
            node, lvl = stack.pop()
            if lvl >= len(view):
                view.append(node.val)
            if node.left is not None:
                stack.append((node.left, lvl + 1))
            if node.right is not None:
                stack.append((node.right, lvl + 1))
        return view
