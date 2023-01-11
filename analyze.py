#!/usr/bin/env python3

import json

from get_rbean_skills import Skill
from rbean_types import ProjectMap, Total, TotalMap
from utils import get_color, print_color


def calc_totals(data: ProjectMap, verbose: bool = True) -> TotalMap:
    totals: TotalMap = {}

    for unit_name, projects in data.items():
        if verbose:
            print_color("- Unit:", "magenta", attrs=["bold"], end=" ")
            print_color(unit_name, attrs=["bold"])

        if unit_name not in totals:
            totals[unit_name] = (Total.zero(), {})

        for project_name, skills in projects.items():
            if verbose:
                print_color("  - Project:", "blue", attrs=["bold"], end=" ")
                print_color(project_name, attrs=["bold"])
            for skill in skills:
                if verbose:
                    print(f"    - {skill.name}:", end=" ")
                    if skill.max_value == 0:
                        ratio = 0.0
                    else:
                        ratio = skill.value / skill.max_value
                    print_color(f"{skill.value} / {skill.max_value}", get_color(ratio))

            total = Total(sum(s.value for s in skills), sum(s.max_value for s in skills))
            totals[unit_name][0].accumulate(total)
            totals[unit_name][1][project_name] = total
            print()

    return totals


def main() -> None:
    with open("skills.json", "r") as f:
        data: ProjectMap = json.load(f, object_hook=lambda o: Skill(**o) if "value" in o else o)

    totals = calc_totals(data)

    print("=" * 50)
    print()

    for unit_name, (total_unit, project_totals) in totals.items():
        print_color(unit_name, "magenta", attrs=["bold"], end=" ")
        print_color("=>", attrs=["bold"], end=" ")
        total_unit.print_color(attrs=["bold"])

        for project_name, total in project_totals.items():
            print_color("  >", attrs=["bold"], end=" ")
            print_color(project_name, "blue", attrs=["bold"], end=" ")
            print_color("=>", attrs=["bold"], end=" ")
            total.print_color()
        print()


if __name__ == "__main__":
    main()
