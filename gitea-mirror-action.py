#!/usr/bin/env python3
import os
from urllib import request, error
import json


GITHUB_OWNER = os.getenv('GITHUB_OWNER')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITEA_ORG = os.getenv('GITEA_ORG')
GITEA_URL = os.getenv('GITEA_URL')
GITEA_TOKEN = os.getenv('GITEA_TOKEN')
CLONE_WIKI = os.getenv('CLONE_WIKI', 'false').lower() == 'true'
FILTER_MODE = os.getenv('FILTER_MODE', 'include')
FILTER_REPO_LIST = [r.strip() for r in os.getenv(
    'FILTER_REPO_LIST', '').split(',') if r.strip()]
MIRROR_INTERVAL = os.getenv('MIRROR_INTERVAL', '8h')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

if None in [GITHUB_OWNER, GITHUB_TOKEN, GITEA_ORG, GITEA_URL, GITEA_TOKEN]:
    raise ValueError("One or more required environment variables are missing.")
if FILTER_MODE not in ['include', 'exclude']:
    raise ValueError("FILTER_MODE must be either 'include' or 'exclude'.")


def debug_log(message: str):
    if DEBUG:
        print(f"[DEBUG] {message}")


def log(message: str):
    print(f"[INFO] {message}")


def error_log(message: str):
    print(f"[ERROR] {message}")


def dry_log(message: str):
    print(f"[DRY RUN] {message}")


def get_github_repo_list() -> list:
    repos = []
    page = 1
    per_page = 100
    base_url = f"https://api.github.com/users/{GITHUB_OWNER}/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    while True:
        url = f"{base_url}?per_page={per_page}&page={page}"
        debug_log(f"Fetching GitHub repos from URL: {url}")
        req = request.Request(url, headers=headers)
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if len(data) == 0:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1
    return repos


def get_gitea_repo_list() -> list:
    if DRY_RUN:
        dry_log("Skipping fetching Gitea repos in dry run mode.")
        return []

    repos = []
    page = 1
    per_page = 100
    base_url = f"{GITEA_URL}/api/v1/orgs/{GITEA_ORG}/repos"
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json"
    }
    while True:
        url = f"{base_url}?limit={per_page}&page={page}"
        debug_log(f"Fetching Gitea repos from URL: {url}")

        req = request.Request(url, headers=headers)
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if len(data) == 0:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1
    return repos


def filter_repos(repos: list) -> list:
    if FILTER_MODE == 'include':
        filtered = [repo for repo in repos if repo['name'] in FILTER_REPO_LIST]
    else:
        filtered = [repo for repo in repos if repo['name']
                    not in FILTER_REPO_LIST]
    return filtered


def ensure_gitea_org():
    gitea_org_api = f"{GITEA_URL}/api/v1/orgs/{GITEA_ORG}"
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json"
    }
    req = request.Request(gitea_org_api, headers=headers)
    try:
        with request.urlopen(req) as response:
            if response.status == 200:
                log(f"Gitea organization '{GITEA_ORG}' exists.")
                return
    except error.HTTPError as e:
        if e.code != 404:
            error_log(
                f"Error checking Gitea organization '{GITEA_ORG}': {e}")
            return

    # Create organization if it does not exist
    if DRY_RUN:
        dry_log(f"Would create Gitea organization '{GITEA_ORG}'")
        return
    create_org_api = f"{GITEA_URL}/api/v1/orgs"
    org_data = {"username": GITEA_ORG, "full_name": "GitHub Mirror Org"}
    req = request.Request(create_org_api, data=json.dumps(
        org_data).encode(), headers=headers, method='POST')
    try:
        with request.urlopen(req) as response:
            if response.status == 201:
                log(f"Gitea organization '{GITEA_ORG}' created.")
            else:
                error_log(
                    f"Failed to create Gitea organization '{GITEA_ORG}'. Status: {response.status}")
    except Exception as e:
        error_log(f"Error creating Gitea organization '{GITEA_ORG}': {e}")


def migrate_to_gitea(repo_name: str, clone_url: str):
    """
    clone_url: str - The clone URL of the GitHub repository to migrate, ends with .git
    """
    if DRY_RUN:
        dry_log(
            f"Would mirror '{clone_url}' to {GITEA_URL}/{GITEA_ORG}/{repo_name}'")
        return
    gitea_migrate_api = f"{GITEA_URL}/api/v1/repos/migrate"
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "clone_addr": clone_url,
        "repo_name": repo_name,
        "repo_owner": GITEA_ORG,
        "mirror": True,
        "mirror_interval": MIRROR_INTERVAL,
        "auth_token": GITHUB_TOKEN,
        "wiki": CLONE_WIKI,
        "service": "github"
    }
    json_data = json.dumps(data).encode()
    req = request.Request(gitea_migrate_api, data=json_data,
                          headers=headers, method='POST')
    try:
        with request.urlopen(req) as response:
            if response.status == 201:
                log(f"Repository '{repo_name}' mirrored to Gitea.")
            else:
                error_log(
                    f"Failed to mirror repository '{repo_name}'. Status: {response.status}")
    except Exception as e:
        error_log(f"Error occured when mirroring repository '{repo_name}': {e}")


def main():
    github_repos = get_github_repo_list()
    log(f"Fetched {len(github_repos)} repositories from GitHub.")
    github_repos = filter_repos(github_repos)
    log(f"{len(github_repos)} repositories after applying filter.")
    if DEBUG:
        debug_log("Filtered GitHub repositories:")
        for repo in github_repos:
            debug_log(f"\t{repo['name']}")

    ensure_gitea_org()

    exists_gitea_repos = get_gitea_repo_list()
    if DEBUG:
        log(f"Fetched {len(exists_gitea_repos)} repositories from Gitea.")
        for repo in exists_gitea_repos:
            debug_log(f"\t{repo['name']}")

    exists_gitea_repo_names = {repo['name'] for repo in exists_gitea_repos}

    for repo in github_repos:
        repo_name = repo['name']
        clone_url = repo['clone_url']
        if repo_name in exists_gitea_repo_names:
            debug_log(
                f"Repository '{repo_name}' already exists in Gitea. Skipping.")
            continue
        migrate_to_gitea(repo_name, clone_url)

    log("Mirror completed.")


if __name__ == "__main__":
    main()
