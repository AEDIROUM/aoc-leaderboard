import requests
import json
from datetime import datetime, timezone
from .config import config
from apiclient import discovery
import google_auth_oauthlib
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


LEADERBOARD_CACHE = "cache/{0}-leaderboard.json"
REGISTRATION_CACHE = "cache/{0}-registration.json"
GOOGLE_TOKENS_CACHE = "cache/google-tokens.json"
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


def get_leaderboard(year):
    try:
        with open(LEADERBOARD_CACHE.format(year), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"members": {}}


def update_leaderboard(year):
    try:
        data = fetch_leaderboard(
            id=config.leaderboard.id,
            year=year,
            session=config.leaderboard.session,
        )
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
            "Invalid server response. "
            "Check validity of the session cookie"
        )

    data["last_update"] = datetime.now(tz=timezone.utc).isoformat()

    with open(LEADERBOARD_CACHE.format(year), "w") as file:
        json.dump(data, file)


def get_google_credentials():
    try:
        with open(GOOGLE_TOKENS_CACHE, "r") as file:
            data = json.load(file)
            credentials = Credentials(**data)
            credentials.refresh(Request())
    except Exception as err:
        flow = Flow.from_client_secrets_file(
            "cache/google-client-secrets.json",
            scopes=["https://www.googleapis.com/auth/forms.responses.readonly"],
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        )

        auth_url, _ = flow.authorization_url(prompt="consent")

        print("Missing or invalid Google credentials")
        print("> " + str(err))
        print()
        print("Please go to this URL: {}".format(auth_url))
        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)
        credentials = flow.credentials

    save_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    with open(GOOGLE_TOKENS_CACHE, "w") as file:
        json.dump(save_data, file)

    return credentials


def fetch_registration(form_id, username_field, category_field):
    credentials = get_google_credentials()
    service = discovery.build(
        "forms", "v1",
        credentials=credentials,
        discoveryServiceUrl="https://forms.googleapis.com/$discovery/rest?version=v1",
        static_discovery=False,
    )

    data = service.forms().responses().list(formId=form_id).execute()
    results = {}

    for response in data["responses"]:
        username = response["answers"][username_field]["textAnswers"]["answers"][0]["value"]
        category = response["answers"][category_field]["textAnswers"]["answers"][0]["value"]
        results[username] = category

    return results


def get_registration(year):
    try:
        with open(REGISTRATION_CACHE.format(year), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def update_registration(year):
    data = fetch_registration(
        form_id=config.registration.form,
        username_field=config.registration.username,
        category_field=config.registration.category,
    )

    with open(REGISTRATION_CACHE.format(year), "w") as file:
        json.dump(data, file)
