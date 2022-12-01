import requests
import json
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions, UsernamePasswordCredential
from .config import read_config


leaderboard_cache = "cache/leaderboard.json"
registration_cache = "cache/registration.json"


def fetch_leaderboard(id, year, session):
    endpoint = f"https://adventofcode.com/{year}/leaderboard/private/view/{id}.json"
    cookies = {"session": session}
    req = requests.get(endpoint, cookies=cookies)
    return req.json()


def get_leaderboard():
    try:
        with open(leaderboard_cache, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"members": {}}


def update_leaderboard():
    config = read_config("./config.ini")
    data = fetch_leaderboard(
        id=config["leaderboard"]["id"],
        year=config["leaderboard"]["year"],
        session=config["leaderboard"]["session"],
    )

    with open(leaderboard_cache, "w") as file:
        json.dump(data, file)


def fetch_registration(tenant, user, form, username, category):
    credential = InteractiveBrowserCredential()
    scope = "https://forms.office.com/.default"
    token = credential.get_token(scope).token

    endpoint = f"https://forms.office.com/formapi/api/{tenant}/users/{user}/light/forms('{form}')/responses?$expand=comments&$top=500&$skip=0"
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 200

    data = res.json()
    users = {}

    for response in data["value"]:
        answers = json.loads(response["answers"])
        res_username = answers[int(username)]["answer1"]
        res_category = answers[int(category)]["answer1"]
        users[res_username] = res_category

    return users


def get_registration():
    try:
        with open(registration_cache, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def update_registration():
    config = read_config("./config.ini")
    data = fetch_registration(
        tenant=config["registration"]["tenant"],
        user=config["registration"]["user"],
        form=config["registration"]["form"],
        username=config["registration"]["username"],
        category=config["registration"]["category"],
    )

    with open(registration_cache, "w") as file:
        json.dump(data, file)
