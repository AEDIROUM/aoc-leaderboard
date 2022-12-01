from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import shutil
import os
from datetime import datetime
from babel.dates import format_datetime
from .data import get_registration, get_leaderboard


DATETIME_FORMAT = "dd MMMM yyyy 'à' HH 'h' mm"


def generate_leaderboard(users, leaderboard):
    environment = Environment(loader=FileSystemLoader("./aoc/templates"))
    template = environment.get_template("index.html")

    data = defaultdict(list)

    for key, member in leaderboard["members"].items():
        if member["name"] in users:
            category = users[member["name"]]
            data[category].append({
                "name": member["name"],
                "stars": member["stars"],
                "local_score": member["local_score"],
            })

    for category, entries in data.items():
        entries.sort(key=lambda entry: -entry["local_score"])

    return template.render({
        "leaderboards": sorted(data.items()),
        "now": format_datetime(datetime.now(), DATETIME_FORMAT, locale='fr_CA'),
    })


def make_static(src, dest):
    shutil.copytree(src + "/static", dest + "/static")


def make_all(src, dest):
    shutil.rmtree(dest, ignore_errors=True)
    os.mkdir(dest)

    users = get_registration()
    leaderboard = get_leaderboard()

    with open(dest + "/index.html", "w") as file:
        file.write(generate_leaderboard(users, leaderboard))

    make_static(src, dest)
