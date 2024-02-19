import sys
from typing import Iterable
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer
from prompt_toolkit.completion.base import CompleteEvent, Completion
from prompt_toolkit.document import Document

from src.main import main, Typeahead


class TypeaheadCompleter(Completer):
    def __init__(self, typeahead: Typeahead) -> None:
        self.typeahead = typeahead

    def get_completions(self, document: Document, *args) -> Iterable[Completion]:
        for word in self.typeahead.suggest(
            document.text_before_cursor,
        ):
            yield Completion(
                text=word,
                start_position=-len(document.text_before_cursor),
                display=word,
            )


def run_demo():
    typeahead = main("words.txt")
    completer = TypeaheadCompleter(typeahead)
    print("Input something to test the typeahead")
    prompt(">>> ", completer=completer)


if __name__ == "__main__":
    run_demo()
