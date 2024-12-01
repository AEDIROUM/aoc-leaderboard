from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
from dataclasses import dataclass
import shutil
import os
from datetime import datetime
from babel.dates import format_datetime, get_timezone, UTC
import plotly.express as px
import pandas as pd
import io
from typing import Optional
from .config import config
from .data import get_registration, get_leaderboard
from .rank import rank_entries


DATETIME_FORMAT = "d MMMM yyyy 'à' HH 'h' mm"
TIMEZONE = get_timezone("America/Montreal")


def format_timedelta(delta):
    parts = []
    hours = delta.seconds // (60 * 60)
    minutes = (delta.seconds % (60 * 60)) // 60
    seconds = delta.seconds % 60

    parts = [
        [delta.days, "j"],
        [hours, "h"],
        [minutes, "min"],
        [seconds, "s"],
    ]

    for left, (value, _) in enumerate(parts):
        if value != 0:
            break

    for right, (value, _) in reversed(list(enumerate(parts))):
        if value != 0:
            break

    return " ".join(
        f"{value} {name}"
        for value, name in parts[left:right + 1]
    )


def get_puzzle_start(year, day):
    return datetime(
        year=int(year), month=12, day=day,
        hour=5, minute=0, second=0,
        tzinfo=UTC,
    )


def get_live_puzzles(year):
    now = datetime.now(tz=UTC)
    return [day for day in range(1, 26) if now >= get_puzzle_start(year, day)]


@dataclass
class Star:
    start_date: datetime
    part1_date: Optional[datetime] = None
    part1_index: Optional[int] = None
    part2_date: Optional[datetime] = None
    part2_index: Optional[int] = None


def get_star_data(year, member):
    star_data = []

    for day in range(1, 26):
        start_date = get_puzzle_start(year, day)
        star = Star(start_date=start_date)

        if str(day) in member["completion_day_level"]:
            info = member["completion_day_level"][str(day)]

            if "1" in info:
                part1_timestamp = info["1"]["get_star_ts"]
                star.part1_date = datetime.fromtimestamp(part1_timestamp, tz=UTC)
                star.part1_index = info["1"]["star_index"]

            if "2" in info:
                part2_timestamp = info["2"]["get_star_ts"]
                star.part2_date = datetime.fromtimestamp(part2_timestamp, tz=UTC)
                star.part2_index = info["2"]["star_index"]

        star_data.append(star)

    return star_data


def generate_entry(year, member):
    stars = []
    star_data = get_star_data(year, member)

    for star in star_data:
        status = []
        level = 0

        if star.part1_date is not None or star.part2_date is not None:
            status.append(f"[Jour {star.start_date.day}]")

        if star.part1_date is not None:
            from_start = format_timedelta(star.part1_date - star.start_date)
            status.append(f"Première étoile: {from_start}")
            level = 1

        if star.part2_date is not None:
            from_start = format_timedelta(star.part2_date - star.start_date)
            from_first = format_timedelta(star.part2_date - star.part1_date)
            status.append(f"Seconde étoile: {from_start} (+ {from_first})")
            level = 2

        stars.append({
            "level": level,
            "status": "\n".join(status),
        })

    return {
        "name": member["name"],
        "stars": stars,
        "score": int(member["local_score"]),
    }


def generate_leaderboard(year, users, leaderboard):
    environment = Environment(loader=FileSystemLoader("./aoc/templates"))
    template = environment.get_template("index.html")

    plot = generate_plot(year, users, leaderboard)

    now = datetime.now(tz=UTC)
    live_days = get_live_puzzles(year)

    data = defaultdict(list)

    for key, member in leaderboard["members"].items():
        if member["name"] in users:
            category = users[member["name"]]
            data[category].append(generate_entry(year, member))

    for category, entries in data.items():
        rank_entries(entries)

    return template.render({
        "form_link": config.registration.link,
        "plot": plot,
        "leaderboards": sorted(data.items()),
        "year": year,
        "show_years": config.leaderboard.show_years,
        "live_days": live_days,
        "last_update": format_datetime(
            datetime.fromisoformat(leaderboard["last_update"]),
            DATETIME_FORMAT,
            tzinfo=TIMEZONE,
            locale='fr_CA',
        ),
    })


def generate_plot(year, users, leaderboard):
    data = []

    for member in list(leaderboard["members"].values()):
        if member["name"] in users:
            star_data = get_star_data(year, member)
            data.extend(
                {
                    "member": member["name"],
                    "day": star.start_date.day,
                    "time": (star.part2_date - star.start_date).seconds
                }
                for star in star_data
                if star.part2_date is not None
            )

    data = pd.DataFrame(data)
    
    fig = px.strip(
        data,
        x="day",
        y="time",
        log_y=True,
        color="member",
        labels={
            "day": "Jour",
            "time": "Temps de résolution (s)",
            "member": "Personne"
        },
        template="plotly_dark",
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=list(range(1, 26)),
        range=(-.5, 24.5),
        constrain="domain",
        showgrid=True,
        ticks="outside",
        tickson="boundaries",
        ticklen=20
    )

    fig.update_traces(
        marker={"size": 6},
        hovertemplate="%{y} s",
    )

    result_file = io.StringIO()
    fig.write_html(result_file, full_html=False, include_plotlyjs="cdn")
    result_string = result_file.getvalue()
    result_file.close()
    return result_string


def make_static(src, dest):
    shutil.copytree(src + "/static", dest + "/static")


def make_leaderboard(dest, year):
    users = get_registration(year)
    leaderboard = get_leaderboard(year)

    with open(dest + f"/{year}.html", "w") as file:
        file.write(generate_leaderboard(year, users, leaderboard))


def make_all(src, dest):
    shutil.rmtree(dest, ignore_errors=True)
    os.mkdir(dest)

    for year in config.leaderboard.show_years:
        make_leaderboard(dest, year)

    make_static(src, dest)
