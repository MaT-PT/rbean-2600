#!/usr/bin/env python3

import json
from os import getenv
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from dotenv import load_dotenv

from rbean_types import Project, ProjectMap, Skill, Unit

load_dotenv()

LOGIN = getenv("LOGIN")
PASSWORD = getenv("PASSWORD")
URL_BASE = getenv("URL_BASE", "https://2600.rbean.io")

URL_LOGIN = urljoin(URL_BASE, "/users/sign_in")
URL_UNITS = urljoin(URL_BASE, "/units")

HTML_PARSER = "html.parser"

session = requests.Session()


def do_login() -> None:
    html = session.get(URL_LOGIN).text
    soup = BeautifulSoup(html, HTML_PARSER)

    token_el = soup.find("input", {"name": "authenticity_token"})
    assert isinstance(token_el, Tag)
    token = token_el.attrs["value"]

    login_data = {
        "authenticity_token": token,
        "user[login]": LOGIN,
        "user[password]": PASSWORD,
    }

    res = session.post(URL_LOGIN, data=login_data)
    if res.url == URL_LOGIN:
        raise RuntimeError("Login failed")


def get_units() -> List[Unit]:
    if len(session.cookies) == 0:
        do_login()

    html = session.get(URL_UNITS).text
    soup = BeautifulSoup(html, HTML_PARSER)

    unit_menus = soup.find("div", id="unit-menus")
    assert isinstance(unit_menus, Tag)
    unit_links: ResultSet[Tag] = unit_menus.find_all("a")
    units = [Unit(a.text.strip(), urljoin(URL_BASE, a.attrs["href"])) for a in unit_links]

    return units


def parse_project(project_card: Tag) -> Project:
    project_link = project_card.find("a")
    assert isinstance(project_link, Tag)
    project_title = project_card.select_one("h5, h6")
    assert isinstance(project_title, Tag)

    project_url = urljoin(URL_BASE, project_link.attrs["href"])
    project_name = project_title.text.strip()

    return Project(project_name, project_url)


def get_projects(unit: Unit) -> List[Project]:
    html = session.get(unit.url).text
    soup = BeautifulSoup(html, HTML_PARSER)

    project_cards = soup.select("div[id$='_timeline'] .row div.flex-column")
    if len(project_cards) == 0:
        project_cards = soup.select("div[id$='_timeline'] .timeline-container .flex-column")

    projects = [parse_project(project_card) for project_card in project_cards]

    return projects


def get_latest_sentinel_url(project: Project) -> Optional[str]:
    html = session.get(project.url).text
    soup = BeautifulSoup(html, HTML_PARSER)

    sentinels: ResultSet[Tag] = soup.find_all("div", id="past-feedbacks")
    if len(sentinels) == 0:
        return None

    latest_sentinel = sentinels[0]
    assert isinstance(latest_sentinel, Tag)
    latest_link = latest_sentinel.find("a")
    assert isinstance(latest_link, Tag)

    return urljoin(URL_BASE, latest_link.attrs["href"])


def parse_skill(skill_card: Tag) -> Skill:
    skill_name = skill_card.find("div", class_="text-center")
    assert isinstance(skill_name, Tag)
    skill_value = skill_card.find("div", class_="circle-text")
    assert isinstance(skill_value, Tag)
    skill_max = skill_value.find("span")
    assert isinstance(skill_max, Tag)
    value = "".join(skill_value.find_all(text=True, recursive=False)).strip()

    return Skill(skill_name.text.strip(), float(value), int(skill_max.text.strip().lstrip("/")))


def get_sentinel_skills(sentinel_url: str) -> List[Skill]:
    html = session.get(sentinel_url).text
    soup = BeautifulSoup(html, HTML_PARSER)
    skills_container = soup.find("div", id="review-skills")
    assert isinstance(skills_container, Tag)
    skills_cards = skills_container.find_all("div", class_="flex-column")
    skills = [parse_skill(skill_card) for skill_card in skills_cards]
    return skills


def main() -> None:
    skills: ProjectMap = {}

    do_login()

    units = get_units()
    for unit in units:
        if unit.name not in skills:
            skills[unit.name] = {}
        print("- Unit:", unit.name)

        projects = get_projects(unit)
        for project in projects:
            if project.name not in skills[unit.name]:
                skills[unit.name][project.name] = []
            print("  - Project:", project.name)

            sentinel_url = get_latest_sentinel_url(project)
            if sentinel_url is None:
                print("    - No sentinel")
                continue

            sentinel_skills = get_sentinel_skills(sentinel_url)
            for skill in sentinel_skills:
                skills[unit.name][project.name].append(skill)
                print(f"    - {skill.name}: {skill.value} / {skill.max_value}")
            print()
        print("=" * 40)

    with open("skills.json", "w") as f:
        json.dump(skills, f, indent=2, default=lambda o: o.__dict__)


if __name__ == "__main__":
    main()
