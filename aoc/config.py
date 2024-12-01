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
            year=parser["leaderboard"]["year"],
            session=parser["leaderboard"]["session"],
            show_years=parser["leaderboard"]["show-years"].split(","),
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
