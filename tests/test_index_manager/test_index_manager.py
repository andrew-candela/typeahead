"""
Do some tests to QA the index manager class
"""

from src.lib.typeahead import IndexManager, TypeaheadNode


class TestIndexManager:
    def test_e_is_indexed_correctly(self, duplicative_words_with_e):
        t = duplicative_words_with_e
        expected_node = (
            t.root.children["r"]
            .children["o"]
            .children["s"]
            .children["e"]
            .children["a"]
            .children["n"]
            .children["n"]
            .children["e"]
        )
        assert id(t.index.index["e"][0]) == id(expected_node)

    def test_compute_replacements(self, node_index):
        manager = IndexManager(node_index, "roseanne")
        manager._compute_replacements()
        assert manager.latest_letter_positions["e"] == 7
        assert manager.latest_letter_positions["r"] == 0
        assert manager.latest_letter_positions["n"] == 6
