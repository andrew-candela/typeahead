"""
The typeahead will implement some rudimentary autocorrect

One potential improvment for the autocorrect would be to consider the
popularity of skills at each step.
This way a typo that is actually a valid skill won't correct to
the popular skill that the user intended.

Implement these:

- cache - cache the n most recent requests. 
Actually I should implement this outside of this module
- dict of nodes
key is a letter, value is a list where ith element is tuple of all nodes
with letter in the ith position. I'll have to find longest word in vocab
- if query result is 0 in trynode search, coerce the search to use the
most popular alternative letter. I'll have to add total freq counts
to each node after populating the trie

## Things to read about

See how theFuzz library does it
https://github.com/seatgeek/thefuzz

Check out fuzzy completer
https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/src/prompt_toolkit/completion/fuzzy_completer.py

"""
from src.lib.skills import Skill, SkillVocabulary
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class NodeIndex:
    """
    Stores the relative positions of all nodes.
    """

    def __init__(self):
        self.index: defaultdict[str, list[TypeaheadNode]] = defaultdict(list)

    def add_node(self, node: "TypeaheadNode"):
        """
        Adds given node to index.
        """
        self.index[node.value].append(node)

    def get_nodes(self, character: str) -> "list[TypeaheadNode]":
        if not character or len(character) > 1:
            raise ValueError(f"Illegal character provided: '{character}'")
        return self.index[character]


class TypeaheadNode:
    def __repr__(self) -> str:
        return f"TypeaheadNode(freq={self._freq}, children={self.children.keys()}, value={self.value}, index_position={self.index_position})"

    def __init__(self, value: str):
        self.value = value
        self.children: dict[str, TypeaheadNode] = {}
        self.parent: TypeaheadNode | None = None
        self.skill: Skill | None = None
        self._freq: int | None = None
        self.is_terminal = False
        self.index_position: int | None = None

    def add_child(self, letter: str, new_node: "TypeaheadNode"):
        self.children[letter] = new_node
        new_node.parent = self

    def most_popular_child(self) -> "TypeaheadNode | None":
        """
        Returns the most popular child node by total frequency
        """
        if not self.children:
            return None
        popular_node = TypeaheadNode(value="")
        popular_node._freq = 0
        for node in self.children.values():
            if node.total_frequency >= popular_node.total_frequency:
                popular_node = node
        return popular_node

    def suggest_on_missing_letter(self) -> "TypeaheadNode":
        """
        Finds the highest frequency child and returns it.
        The idea is if the user makes a mistake like a typo on a
        single letter, we can try to guess and coerce the input
        back to something in the typeahead, rather than returning nothing.
        """
        if not self.children:
            raise ValueError("Cannot suggest a node from a terminal node")
        max_freq = float("-inf")
        current_node = None
        for node in self.children.values():
            if node.total_frequency > max_freq:
                max_freq = node.total_frequency
                current_node = node
        if current_node is None:
            raise ValueError("Current node is None. This should be imposible.")
        return current_node

    def return_popular_skills(self, num_skills: int) -> list[Skill]:
        """
        Finds all terminal children of the current node.
        """
        out_skills = [self.skill] if self.skill else []
        next_nodes = list(self.children.values())
        while next_nodes:
            current_node = next_nodes.pop()
            next_nodes.extend(current_node.children.values())
            if current_node.skill:
                out_skills.append(current_node.skill)
        out_skills.sort(key=lambda skill: skill.frequency, reverse=True)
        return out_skills[:num_skills]

    @property
    def total_frequency(self) -> int:
        """
        If self._freq has been set, return it.
        Otherwise compute it with a DFS, summing up the frequency
        of all child nodes
        """
        if self._freq is not None:
            return self._freq

        self._freq = sum([node.total_frequency for node in self.children.values()])
        if self.skill:
            self._freq += self.skill.frequency
        return self._freq

    def is_non_contiguous_match(self, pattern: str) -> bool:
        """
        Walks up the graph and looks for non-contiguous matches
        """
        if len(pattern) == 0:
            return True
        if not self.parent:
            return False
        if pattern[-1] == self.parent.value:
            return self.parent.is_non_contiguous_match(pattern[:-1])
        return self.parent.is_non_contiguous_match(pattern)


class Typeahead:
    """
    Serve some suggestions
    """

    def __repr__(self) -> str:
        return f"Typeahead(root={str(self.root)})"

    def __init__(self):
        self.root = TypeaheadNode(value="")
        self.index = NodeIndex()

    @classmethod
    def from_vocab(cls, vocab: SkillVocabulary) -> "Typeahead":
        typeahead = cls()
        for skill in vocab.skills.values():
            typeahead.add_skill(skill)
        typeahead._populate_frequencies()
        return typeahead

    def _suggest(self, input: str) -> list[str]:
        current_node = self.root
        mistakes = 0
        for letter in input:
            if current_node.children == {}:
                raise ValueError(
                    f"Cannot proceed past character `{letter}` of input `{input}`. "
                    f"Arrived at terminal node {str(current_node)}"
                )
            if letter in current_node.children:
                current_node = current_node.children[letter]
            else:
                mistakes += 1
                if mistakes > 2:
                    raise ValueError("Too many mistakes")
                current_node = current_node.suggest_on_missing_letter()
        # At the end of the input. Return the 2 skills with the highest freq
        return [skill.id for skill in current_node.return_popular_skills(5)]

    # This doesn't quite work correctly.
    # It returns duplicative results if there are repeated letters in a
    # matching word.
    # This is because my index is duplicative. I can fix it by building
    # # the index after the taxonomy has been built, and just look at terminal
    # nodes.
    def _non_contiguous_suggestion(self, input: str) -> list[str]:
        """
        Returns matches from the vocabulary that satisfy a fairly

        'abc' -> '*a*b*c*'
        """
        if not input:
            return []
        suggestions = []
        for matching_node in self.index.get_nodes(input[-1]):
            if matching_node.is_non_contiguous_match(input[:-1]):
                suggestions.extend(
                    [skill.id for skill in matching_node.return_popular_skills(2)]
                )
        return suggestions

    def suggest(self, input: str) -> list[str]:
        try:
            return self._suggest(input)
        except ValueError:
            return self._non_contiguous_suggestion(input)

    def add_skill(self, skill: Skill):
        """
        Adds nodes for each character in the skill ID
        when at the terminal node set the frequency
        """
        current_node = self.root
        index_handler = IndexManager(self.index, skill.id)
        for position, letter in enumerate(skill.id):
            if letter not in current_node.children:
                new_node = TypeaheadNode(letter)
                current_node.add_child(letter, new_node)
            current_node = current_node.children[letter]
            index_handler.index_node(current_node, position)
        current_node._freq = skill.frequency
        current_node.skill = skill

    def _populate_frequencies(self):
        """
        Traverses the nodes of the typeahead to populate
        the total frequencies of each node.
        Uses DFS to add the total requencies of all of the
        child nodes to the current node
        """
        freq = self.root.total_frequency
        logger.debug(f"Total frequency of vocabulary is {freq}")


class IndexManager:
    """
    Use an IndexManager to help you keep an index up to date when
    adding nodes to a Typeahead.
    Basically this keeps track of nodes that need to be replaced in
    an index.

    The idea is that if I am adding a word to the typeahead,
    say "airtime", if I already have something like "airflow",
    then I want to replace the index for "i" in the 2nd position in
    "airflow" with the "i" in the 5th position in "airtime".

    The index manager will compute the replacements that must be made
    and the process adding the word can call it during the add loop.
    """

    def __init__(self, index: NodeIndex, word: str):
        self.index = index
        self.word = word
        self.index_positions: dict[str, int] = {}
        self._compute_replacements()

    def _compute_replacements(self):
        """
        Finds the latest occurrance of each letter in self.word
        """
        self.latest_letter_positions: dict[str, int] = {}
        for position, letter in enumerate(self.word):
            self.latest_letter_positions[letter] = position

    def index_node(self, node: TypeaheadNode, position: int):
        # If we are at a position that we must index, then do so.
        if position == self.latest_letter_positions.get(node.value, -1):
            # if the node is already indexed, then we can do nothing
            if node.index_position is not None:
                return
            if self.index_positions.get(node.value) is not None:
                node.index_position = self.index_positions[node.value]
                self.index.index[node.value][self.index_positions[node.value]] = node
            else:
                node.index_position = len(self.index.index[node.value])
                self.index.index[node.value].append(node)
        # If we have a letter that will be indexed later, let's save the
        # Node's index position in self, and unset it on the node
        elif position < self.latest_letter_positions.get(node.value, -1):
            if node.index_position is not None:
                self.index_positions[node.value] = node.index_position
                node.index_position = None
            # If the node is not indexed, then I can do nothing - we handle it later
