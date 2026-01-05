import logging
from gitea_mirror.http_api.gitea import Gitea
from gitea_mirror.http_api.github import GitHub


class MirrorBase:
    def __init__(self, github_token: str, gitea_token: str, gitea_url: str, dry_run: bool = False):
        self._github = GitHub(github_token)
        self._gitea = Gitea(gitea_url, gitea_token)
        self._logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._dry_run = dry_run
