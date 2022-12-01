from dataclasses import dataclass
from configparser import ConfigParser


@dataclass(frozen=True)
class Leaderboard:
    id: str
    year: int
    session: str


@dataclass(frozen=True)
class Registration:
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
            year=int(parser["leaderboard"]["year"]),
            session=parser["leaderboard"]["session"],
        ),
        registration=Registration(
            tenant=parser["registration"]["tenant"],
            user=parser["registration"]["user"],
            form=parser["registration"]["form"],
            username=int(parser["registration"]["username"]),
            category=int(parser["registration"]["category"]),
        ),
    )


config = read_config("./config.ini")
