
class Solution {

    private static final int[] VALUES = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
    private static final String[] SYMBOLS = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};

    public static void main(String[] args) {
        System.out.println(new Solution().intToRoman(Integer.parseInt(args[0])));
    }

    public String intToRoman(int num) {
        StringBuilder sb = new StringBuilder();
        int valIndex = 0;
        while (num > 0) {
            if (num >= VALUES[valIndex]) {
                num -= VALUES[valIndex];
                sb.append(SYMBOLS[valIndex]);
            } else {
                valIndex += 1;
            }
        }
        return sb.toString();
    }
}
