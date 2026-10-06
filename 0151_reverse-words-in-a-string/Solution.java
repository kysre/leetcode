
import java.util.ArrayDeque;
import java.util.Deque;

class Solution {

    public String reverseWords(String s) {
        StringBuilder sb = new StringBuilder();
        Deque<String> stack = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (c != ' ') {
                sb.append(c);
            } else if (!sb.isEmpty()) {
                stack.push(sb.toString());
                sb.setLength(0);
            }
        }
        if (!sb.isEmpty()) {
            stack.push(sb.toString());
            sb.setLength(0);
        }
        while (!stack.isEmpty()) {
            if (!sb.isEmpty()) {
                sb.append(' ');
            }
            sb.append(stack.pop());
        }
        return sb.toString();
    }
}
