from dataclasses import dataclass
from configparser import ConfigParser


@dataclass(frozen=True)
class Leaderboard:
    id: str
    current_year: str
    session: str
    old_years: list[str]


@dataclass(frozen=True)
class Registration:
    link: str
    tenant: str
    user: str
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
            current_year=parser["leaderboard"]["current-year"],
            session=parser["leaderboard"]["session"],
            old_years=parser["leaderboard"]["old-years"].split(","),
        ),
        registration=Registration(
            link=parser["registration"]["link"],
            tenant=parser["registration"]["tenant"],
            user=parser["registration"]["user"],
            form=parser["registration"]["form"],
            username=int(parser["registration"]["username"]),
            category=int(parser["registration"]["category"]),
        ),
    )

config = read_config("./config.ini")
