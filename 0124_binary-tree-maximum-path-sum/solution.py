class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def maxPathSum(self, root: TreeNode | None) -> int:
        _, m = self.find_max(root, root.val)
        return m

    def find_max(self, node: TreeNode | None, maxx: int) -> int:
        if node is None:
            return 0
        returnable, possible_max = 0, maxx
        if node.left is not None and node.right is not None:
            l, maxl = self.find_max(node.left, maxx)
            r, maxr = self.find_max(node.right, maxx)
            returnable = max(node.val, node.val + l, node.val + r)
            possible_max = max(returnable, l + node.val + r, maxl, maxr)
        elif node.left is not None:
            l, maxl = self.find_max(node.left, maxx)
            returnable = max(node.val, node.val + l)
            possible_max = max(returnable, maxl)
        elif node.right is not None:
            r, maxr = self.find_max(node.right, maxx)
            returnable = max(node.val, node.val + r)
            possible_max = max(returnable, maxr)
        else:
            returnable = node.val
            possible_max = returnable
        return returnable, max(maxx, possible_max)
