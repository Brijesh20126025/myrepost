from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Investor:
    id: int
    name: str
    email: str
    tags: list[str] = field(default_factory=list)
    active: bool = True

    def display_name(self) -> str:
        return self.name.strip().title()

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
