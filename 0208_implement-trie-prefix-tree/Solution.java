
class Trie {

    private Trie[] children = new Trie[26];
    private boolean isWord;

    public Trie() {
    }

    public void insert(String word) {
        Trie node = this;
        for (char ch : word.toCharArray()) {
            int c = ch - 'a';
            if (node.children[c] == null) {
                node.children[c] = new Trie();
            }
            node = node.children[c];
        }
        node.isWord = true;
    }

    public boolean search(String word) {
        Trie node = this.getNodeWithPrefix(word);
        return node != null && node.isWord;
    }

    public boolean startsWith(String prefix) {
        Trie node = this.getNodeWithPrefix(prefix);
        return node != null;
    }

    private Trie getNodeWithPrefix(String prefix) {
        Trie node = this;
        for (Character ch : prefix.toCharArray()) {
            int c = ch - 'a';
            if (node.children[c] == null) {
                return null;
            }
            node = node.children[c];
        }
        return node;
    }
}
