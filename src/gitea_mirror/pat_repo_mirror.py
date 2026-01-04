import logging
from typing import Literal
from api import GitHub, Gitea
import fnmatch

from gitea_mirror.api.github import PATRepo


class PATRepoMirror:
    """
    Mirror public GitHub repositories to Gitea.
    """

    def __init__(self, github_token: str,  gitea_url: str, gitea_token: str):
        self.github = GitHub(github_token)
        self.gitea = Gitea(gitea_token, gitea_url)
        self.logger = logging.getLogger(__name__)

    def mirror_repo(self, org_map: dict[str, str], mirror_interval: str = "8h", clone_wiki: bool = True,
                    filter_shell_pattern: list[str] | None = None, filter_mode: Literal["include", "exclude"] = "exclude"):
        """mirror repo that could be accessed by the PAT, this API will keep the private status of the repo

        Args:
            org_map (dict[str, str]): organization map, default map key is '*'
            mirror_interval (str, optional): mirror interval. Defaults to "8h".
            clone_wiki (bool, optional): if clone wiki or not. Defaults to True.
            keep_private (bool, optional): if private or not. Defaults to True.
            filter_shell_pattern (list[str] | None, optional): shell patterns format to include or exclude full name repos. Defaults to None.
            filter_mode ("include" | "exclude", optional): filter_mode. Defaults to "exclude".

        """
        if filter_shell_pattern is None:
            filter_shell_pattern = []
        repos = self.github.list_pat_user_repos()
        self.logger.info(
            f"Found {len(repos)} repositories accessible by the PAT.")
        filtered_repos = PATRepoMirror.filter_repos(
            repos, filter_shell_pattern, filter_mode)
        self.logger.info(
            f"{len(filtered_repos)} repositories to be mirrored after applying filter.")
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Repositories to be mirrored: {filtered_repos}")
        default_org = org_map.get('*', )
        for repo in filtered_repos:
            github_owner, repo_name = repo.full_name.split("/")[1]
            target_org = org_map.get(
                github_owner, default_org)
            clone_url = GitHub.get_repo_clone_url(repo.full_name)
            logging.debug(f"Mirroring repository: {repo_name}")
            if target_org is None:
                self.logger.warning(
                    f"Skipping repository {repo} as no target organization is specified.")
                continue
            self.gitea.migrate_from_github(
                target_org, repo_name, clone_url, self.github.token, mirror_interval, clone_wiki, repo.private)

    @staticmethod
    def filter_repos(repos: list[PATRepo], filter_shell_patterns: list[str], mode: Literal["include", "exclude"]) -> list[PATRepo]:
        """
        Filter repositories based on inclusion or exclusion lists.
        """
        if mode == "include":
            filtered_repos = [
                repo for repo in repos if any(fnmatch.fnmatch(repo.full_name, pattern) for pattern in filter_shell_patterns)]
        elif mode == "exclude":
            filtered_repos = [
                repo for repo in repos if not any(fnmatch.fnmatch(repo.full_name, pattern) for pattern in filter_shell_patterns)]
        else:
            raise ValueError("Mode must be either 'include' or 'exclude'.")
        return filtered_repos
