from dataclasses import dataclass
from typing import Iterable


@dataclass
class Skill:
    id: str
    frequency: int


@dataclass
class SkillVocabulary:
    skills: dict[str, Skill]
    max_length: int
    characters: set[str]

    @classmethod
    def build(cls, skills: Iterable[Skill]) -> "SkillVocabulary":
        skill_dict = {skill.id: skill for skill in skills}
        max_length = 0
        characters = set([])
        for skill in skills:
            max_length = max(max_length, len(skill.id))
            for char in skill.id:
                characters.add(char)
        return cls(skills=skill_dict, max_length=max_length, characters=characters)


skills = (
    Skill(id="ruby", frequency=1),
    Skill(id="rugby", frequency=2),
    Skill(id="rails", frequency=30),
    Skill(id="racheal", frequency=4),
    Skill(id="rutherford", frequency=2),
    Skill(id="ross", frequency=3),
    Skill(id="rust", frequency=6),
)
