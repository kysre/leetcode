# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Solution:
    def lowestCommonAncestor(
        self, root: "TreeNode", p: "TreeNode", q: "TreeNode"
    ) -> "TreeNode":
        if p.val == q.val:
            return p
        p_dfs, _ = self.dfs_path(root, p)
        q_dfs, _ = self.dfs_path(root, q)
        common_ancestor = None
        for i in range(max(len(p_dfs), len(q_dfs))):
            if i == len(p_dfs) or i == len(q_dfs):
                break
            if p_dfs[i].val == q_dfs[i].val:
                common_ancestor = p_dfs[i]
            else:
                break
        return common_ancestor

    def dfs_path(self, root, p):
        if root.val == p.val:
            return [root], True
        if root.left is not None:
            path, found = self.dfs_path(root.left, p)
            if found:
                path.insert(0, root)
                return path, True
        if root.right is not None:
            path, found = self.dfs_path(root.right, p)
            if found:
                path.insert(0, root)
                return path, True
        return None, False
