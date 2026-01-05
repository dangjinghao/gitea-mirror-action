import os
import logging
import sys
import contextlib

from gitea_mirror.mirror_repo import PublicRepoMirror, PATRepoMirror


@contextlib.contextmanager
def actions_group(title: str):
    """Group logs in Actions UIs (GitHub/Gitea) using workflow commands."""
    print(f"::group::{title}", flush=True)
    try:
        yield
    finally:
        print("::endgroup::", flush=True)


def pat_repo_mirror_main(GITHUB_TOKEN, GITEA_URL,
                         GITEA_TOKEN, DRY_RUN, MIRROR_INTERVAL, CLONE_WIKI, FILTER_MODE):
    """specific envs:
    ORG_MAP: Comma-separated list of GitHub org to Gitea org mappings. E.g., "github_org1:gitea_org1,github_org2:gitea_org2,*:default_gitea_org"
    MIRROR_INTERVAL: Gitea mirror interval (default: "8h")
    CLONE_WIKI: Whether to clone wikis (default: "true")
    FILTER_MODE: "include" or "exclude" (default: "exclude")
    FILTER_SHELL_PATTERNS: Comma-separated list of shell patterns to filter repository names (default: "*"). E.g. "owner/repo1,owner/repo2"
    """
    mirror = PATRepoMirror(GITHUB_TOKEN, GITEA_URL,
                           GITEA_TOKEN, DRY_RUN)
    ORG_MAP_ENV = os.getenv("ORG_MAP", "")
    org_map = {}
    if ORG_MAP_ENV != "":
        for mapping in ORG_MAP_ENV.split(","):
            github_org, gitea_org = mapping.split(":")
            if github_org == "" or gitea_org == "":
                raise ValueError(
                    "Invalid ORG_MAP format. Each mapping must be in the format 'github_org:gitea_org'.")
            org_map[github_org.strip()] = gitea_org.strip()

    FILTER_SHELL_PATTERNS_ENV = os.getenv("FILTER_SHELL_PATTERNS", "*")
    FILTER_SHELL_PATTERNS = [
        pattern.strip() for pattern in FILTER_SHELL_PATTERNS_ENV.split(",")]

    mirror.mirror_repo(
        org_map,
        MIRROR_INTERVAL,
        CLONE_WIKI,
        FILTER_SHELL_PATTERNS,
        FILTER_MODE,
    )


def public_repo_mirror_main(GITHUB_TOKEN, GITEA_TOKEN,
                            GITEA_URL, DRY_RUN, MIRROR_INTERVAL, CLONE_WIKI, FILTER_MODE):
    mirror = PublicRepoMirror(GITHUB_TOKEN, GITEA_TOKEN,
                              GITEA_URL, DRY_RUN)
    GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")
    if GITHUB_OWNER == "":
        raise ValueError("GITHUB_OWNER environment variable is not set.")
    GITEA_ORG = os.getenv("GITEA_ORG", "")
    if GITEA_ORG == "":
        raise ValueError("TARGET_ORG environment variable is not set.")

    FILTER_REPO_LIST_ENV = os.getenv("FILTER_REPO_LIST", "")
    FILTER_REPO_LIST = []
    if FILTER_REPO_LIST_ENV != "":
        FILTER_REPO_LIST = [
            pattern.strip() for pattern in FILTER_REPO_LIST_ENV.split(",")]

    mirror.mirror_repo(
        GITHUB_OWNER,
        GITEA_ORG,
        MIRROR_INTERVAL,
        CLONE_WIKI,
        FILTER_REPO_LIST,
        FILTER_MODE,
    )


def main():

    FETCH_FROM_PAT = os.getenv("FETCH_FROM_PAT", "false").lower() == "true"
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

    GITEA_URL = os.getenv("GITEA_URL", "")
    if GITEA_URL == "":
        raise ValueError("GITEA_URL environment variable is not set.")

    GITEA_TOKEN = os.getenv("GITEA_TOKEN", "")
    if GITEA_TOKEN == "":
        raise ValueError("GITEA_TOKEN environment variable is not set.")

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    if GITHUB_TOKEN == "":
        raise ValueError("GITHUB_TOKEN environment variable is not set.")

    MIRROR_INTERVAL = os.getenv("MIRROR_INTERVAL", "8h")
    CLONE_WIKI = os.getenv("CLONE_WIKI", "true").lower() == "true"
    FILTER_MODE = os.getenv("FILTER_MODE", "exclude")

    DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, force=True)
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)

    for noisy_logger in ("httpx", "httpcore"):
        logging.getLogger(noisy_logger).setLevel(logging.CRITICAL)
    
    if FETCH_FROM_PAT:
        with actions_group("Mirror repositories (PAT mode)"):
            pat_repo_mirror_main(
                GITHUB_TOKEN,
                GITEA_URL,
                GITEA_TOKEN,
                DRY_RUN,
                MIRROR_INTERVAL,
                CLONE_WIKI,
                FILTER_MODE,
            )
    else:
        with actions_group("Mirror repositories (public mode)"):
            public_repo_mirror_main(
                GITHUB_TOKEN,
                GITEA_TOKEN,
                GITEA_URL,
                DRY_RUN,
                MIRROR_INTERVAL,
                CLONE_WIKI,
                FILTER_MODE,
            )


if __name__ == "__main__":
    main()
