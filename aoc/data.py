import requests
import json
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions, UsernamePasswordCredential
from .config import config


LEADERBOARD_CACHE = "cache/leaderboard.json"
REGISTRATION_CACHE = "cache/registration.json"
USER_AGENT = {
    "From": "git.matteo@delab.re",
    "User-Agent": "aoc-leaderboard (github.com/matteodelabre/aoc-leaderboard)",
}


def fetch_leaderboard(id, year, session):
    endpoint = f"https://adventofcode.com/{year}/leaderboard/private/view/{id}.json"
    cookies = {"session": session}
    headers = {**USER_AGENT}
    req = requests.get(endpoint, cookies=cookies, headers=headers)
    return req.json()


def get_leaderboard():
    try:
        with open(LEADERBOARD_CACHE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"members": {}}


def update_leaderboard():
    data = fetch_leaderboard(
        id=config.leaderboard.id,
        year=config.leaderboard.year,
        session=config.leaderboard.session,
    )

    with open(LEADERBOARD_CACHE, "w") as file:
        json.dump(data, file)


def fetch_registration(tenant, user, form, username, category):
    credential = InteractiveBrowserCredential()
    scope = "https://forms.office.com/.default"
    token = credential.get_token(scope).token

    endpoint = f"https://forms.office.com/formapi/api/{tenant}/users/{user}/light/forms('{form}')/responses?$expand=comments&$top=500&$skip=0"
    headers = {
        "Authorization": f"Bearer {token}",
        **USER_AGENT,
    }

    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 200

    data = res.json()
    users = {}

    for response in data["value"]:
        answers = json.loads(response["answers"])
        res_username = answers[username]["answer1"]
        res_category = answers[category]["answer1"]
        users[res_username] = res_category

    return users


def get_registration():
    try:
        with open(REGISTRATION_CACHE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def update_registration():
    data = fetch_registration(
        tenant=config.registration.tenant,
        user=config.registration.user,
        form=config.registration.form,
        username=config.registration.username,
        category=config.registration.category,
    )

    with open(REGISTRATION_CACHE, "w") as file:
        json.dump(data, file)
