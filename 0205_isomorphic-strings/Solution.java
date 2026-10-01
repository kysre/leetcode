
import java.util.HashMap;

class Solution {

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java Solution <string1> <string2>");
            return;
        }

        System.out.println(new Solution().isIsomorphic(args[0], args[1]));
    }

    public boolean isIsomorphic(String s, String t) {
        if (s.length() != t.length()) {
            return false;
        }
        HashMap<Character, Character> smap = new HashMap<>();
        HashMap<Character, Character> tmap = new HashMap<>();
        for (int i = 0; i < s.length(); i++) {
            char sc = s.charAt(i);
            char tc = t.charAt(i);
            if (!smap.keySet().contains(sc) && !tmap.keySet().contains(tc)) {
                smap.put(sc, tc);
                tmap.put(tc, sc);
                continue;
            }
            if ((!smap.keySet().contains(sc) && tmap.keySet().contains(tc))
                    || (smap.keySet().contains(sc) && !tmap.keySet().contains(tc))) {
                return false;
            }
            char tcm = smap.get(sc);
            char scm = tmap.get(tc);
            if (tcm != tc || scm != sc) {
                return false;
            }
        }
        return true;
    }
}
