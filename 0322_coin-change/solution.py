from typing import List


class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        if amount == 0:
            return 0
        # Truncate coins larger than amount
        coins.sort()
        n = len(coins)
        for i in range(len(coins)):
            if coins[i] > amount:
                n = i
                break
        # Build DP Base case
        DP = [-1] * (amount + 1)
        DP[0] = 0
        for i in range(n):
            DP[coins[i]] = 1
        # Calculate DP
        for i in range(1, amount + 1):
            if i in coins:
                continue
            changes = []
            for j in range(n):
                index = i - coins[j]
                if index > 0 and DP[index] > -1:
                    changes.append(1 + DP[index])
            if len(changes) == 0:
                DP[i] = -1
            else:
                DP[i] = min(changes)
        # Return answer
        return DP[amount]
