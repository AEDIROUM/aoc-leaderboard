from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import shutil
import os
from datetime import datetime
from babel.dates import format_datetime, get_timezone, UTC
from .data import get_registration, get_leaderboard
from .rank import rank_entries


DATETIME_FORMAT = "d MMMM yyyy 'à' HH 'h' mm"
TIMEZONE = get_timezone("America/Montreal")


def generate_leaderboard(users, leaderboard):
    environment = Environment(loader=FileSystemLoader("./aoc/templates"))
    template = environment.get_template("index.html")

    data = defaultdict(list)

    for key, member in leaderboard["members"].items():
        if member["name"] in users:
            category = users[member["name"]]
            stars = [0] * 25

            for index in range(26):
                if str(index + 1) in member["completion_day_level"]:
                    status = member["completion_day_level"][str(index + 1)]

                    if "2" in status:
                        stars[index] = 2
                    elif "1" in status:
                        stars[index] = 1

            data[category].append({
                "name": member["name"],
                "stars": stars,
                "score": int(member["local_score"]),
            })

    for category, entries in data.items():
        rank_entries(entries)

    live_days = list(range(1, datetime.now(tz=TIMEZONE).day + 1))

    return template.render({
        "leaderboards": sorted(data.items()),
        "live_days": live_days,
        "now": format_datetime(
            datetime.now(tz=UTC),
            DATETIME_FORMAT,
            tzinfo=TIMEZONE,
            locale='fr_CA',
        ),
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
