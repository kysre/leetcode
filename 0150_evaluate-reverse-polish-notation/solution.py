from typing import List


class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []
        for tkn in tokens:
            if tkn == "+":
                b, a = stack.pop(), stack.pop()
                stack.append(a + b)
            elif tkn == "-":
                b, a = stack.pop(), stack.pop()
                stack.append(a - b)
            elif tkn == "*":
                b, a = stack.pop(), stack.pop()
                stack.append(a * b)
            elif tkn == "/":
                b, a = stack.pop(), stack.pop()
                stack.append(int(a / b))
            else:
                stack.append(int(tkn))
        return stack.pop()
