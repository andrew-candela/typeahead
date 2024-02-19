import os
import logging
from src.lib.typeahead import Typeahead
from src.lib.skills import SkillVocabulary, skills, Skill


logging.basicConfig(level=os.getenv("LOG_LEVEL", logging.WARNING))


def use_big_vocab(vocab_file: str) -> SkillVocabulary:
    with open(vocab_file, "r") as words:
        word_list = [Skill(id=word.strip(), frequency=1) for word in words.readlines()]
    return SkillVocabulary.build(tuple(word_list))


def main(vocab_file: str):
    # vocab = SkillVocabulary.build(skills)
    vocab = use_big_vocab(vocab_file)
    typeahead = Typeahead.from_vocab(vocab)
    logging.info(f"{typeahead=}")
    return typeahead
