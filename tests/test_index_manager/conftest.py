import pytest

from src.lib.typeahead import Typeahead, TypeaheadNode, NodeIndex, IndexManager
from src.lib.skills import SkillVocabulary, Skill


@pytest.fixture
def duplicative_words_with_e() -> Typeahead:
    """
    Returns a typeahead you can use to test that the 'e'
    in the skill is correctly indexed
    """
    skills = (
        Skill(id="rose", frequency=3),
        Skill(id="roseanne", frequency=7),
    )
    vocab = SkillVocabulary.build(skills)
    return Typeahead.from_vocab(vocab)


@pytest.fixture
def node_index() -> NodeIndex:
    n = NodeIndex()
    return n


@pytest.fixture
def index_manager() -> IndexManager:
    n = NodeIndex()
    return IndexManager(n, "Roseanne")
