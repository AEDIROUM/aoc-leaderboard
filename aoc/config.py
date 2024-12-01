from dataclasses import dataclass
from configparser import ConfigParser


@dataclass(frozen=True)
class Leaderboard:
    id: str
    year: str
    session: str
    show_years: list[str]


@dataclass(frozen=True)
class Registration:
    link: str
    form: str
    username: int
    category: int


@dataclass(frozen=True)
class Config:
    leaderboard: Leaderboard
    registration: Registration


def read_config(path):
    parser = ConfigParser()
    parser.read(path)
    return Config(
        leaderboard=Leaderboard(
            id=parser["leaderboard"]["id"],
            year=parser["leaderboard"]["year"],
            session=parser["leaderboard"]["session"],
            show_years=parser["leaderboard"]["show-years"].split(","),
        ),
        registration=Registration(
            link=parser["registration"]["link"],
            form=parser["registration"]["form"],
            username=parser["registration"]["username"],
            category=parser["registration"]["category"],
        ),
    )

config = read_config("./config.ini")
