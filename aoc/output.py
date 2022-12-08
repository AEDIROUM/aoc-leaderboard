from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import shutil
import os
from datetime import datetime
from babel.dates import format_datetime, get_timezone, UTC
from .config import config
from .data import get_registration, get_leaderboard
from .rank import rank_entries


DATETIME_FORMAT = "d MMMM yyyy 'à' HH 'h' mm"
TIMEZONE = get_timezone("America/Montreal")


def format_part(value, name):
    if value == 0:
        return []
    else:
        return [f"{value} {name}"]


def format_timedelta(delta):
    parts = []
    hours = delta.seconds // (60 * 60)
    minutes = (delta.seconds % (60 * 60)) // 60
    seconds = delta.seconds % 60

    parts.extend(format_part(delta.days, "j"))
    parts.extend(format_part(hours, "h"))
    parts.extend(format_part(minutes, "min"))
    parts.extend(format_part(seconds, "s"))

    return " ".join(parts)


def get_puzzle_start(day):
    return datetime(
        year=config.leaderboard.year, month=12, day=day,
        hour=5, minute=0, second=0,
        tzinfo=UTC,
    )


def get_live_puzzles():
    now = datetime.now(tz=UTC)
    return [day for day in range(1, 26) if now >= get_puzzle_start(day)]


def generate_entry(member):
    stars = []

    for day in range(1, 26):
        level = 0
        status = []
        start_time = get_puzzle_start(day)

        if str(day) in member["completion_day_level"]:
            info = member["completion_day_level"][str(day)]

            if "1" in info:
                level = 1
                part1_timestamp = info["1"]["get_star_ts"]
                part1_time = datetime.fromtimestamp(part1_timestamp, tz=UTC)
                from_start = format_timedelta(part1_time - start_time)
                status.append(f"Première étoile: {from_start}")

                if "2" in info:
                    level = 2
                    part2_timestamp = info["2"]["get_star_ts"]
                    part2_time = datetime.fromtimestamp(part2_timestamp, tz=UTC)
                    from_start = format_timedelta(part2_time - start_time)
                    from_first = format_timedelta(part2_time - part1_time)
                    status.append(f"Seconde étoile: {from_start} (+ {from_first})")

        if status:
            status = [f"[Jour {day}]"] + status

        stars.append({
            "level": level,
            "status": "\n".join(status),
        })

    return {
        "name": member["name"],
        "stars": stars,
        "score": int(member["local_score"]),
    }


def generate_leaderboard(users, leaderboard):
    environment = Environment(loader=FileSystemLoader("./aoc/templates"))
    template = environment.get_template("index.html")

    now = datetime.now(tz=UTC)
    live_days = get_live_puzzles()

    data = defaultdict(list)

    for key, member in leaderboard["members"].items():
        if member["name"] in users:
            category = users[member["name"]]
            data[category].append(generate_entry(member))

    for category, entries in data.items():
        rank_entries(entries)

    return template.render({
        "leaderboards": sorted(data.items()),
        "year": config.leaderboard.year,
        "live_days": live_days,
        "now": format_datetime(
            now,
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
