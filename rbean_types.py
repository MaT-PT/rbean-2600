from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from utils import get_color, print_color


@dataclass
class Unit:
    name: str
    url: str


@dataclass
class Project:
    name: str
    url: str


@dataclass
class Skill:
    name: str
    value: float
    max_value: int


@dataclass
class Total:
    total: float
    total_max: int

    @property
    def ratio(self) -> float:
        if self.total_max == 0:
            return 0.0
        return self.total / self.total_max

    @staticmethod
    def zero() -> "Total":
        return Total(0.0, 0)

    def accumulate(self, o: "Union[Total, int]") -> "Total":
        if isinstance(o, int):
            self.total += o
            self.total_max += o
            return self

        self.total += o.total
        self.total_max += o.total_max
        return self

    def print_color(self, *args: Any, **kwargs: Any) -> None:
        print_color(str(self), get_color(self.ratio), *args, **kwargs)

    def __add__(self, o: "Union[Total, int]") -> "Total":
        if isinstance(o, int):
            return Total(self.total + o, self.total_max + o)

        return Total(self.total + o.total, self.total_max + o.total_max)

    def __str__(self) -> str:
        return f"{self.total} / {self.total_max} ({self.ratio:.2%})"


ProjectMap = Dict[str, Dict[str, List[Skill]]]
TotalMap = Dict[str, Tuple[Total, Dict[str, Total]]]
SkillTotals = Dict[str, Total]
ProjectUnitCouple = Tuple[Project, Unit]
