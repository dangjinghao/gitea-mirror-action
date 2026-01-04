import logging
from typing import Literal
from api import GitHub, Gitea


class PublicRepoMirror:
    """
    Mirror public GitHub repositories to Gitea.
    """

    def __init__(self, github_token: str,  gitea_url: str, gitea_token: str):
        self.github = GitHub(github_token)
        self.gitea = Gitea(gitea_token, gitea_url)
        self.logger = logging.getLogger(__name__)

    def mirror_repo(self, github_owner: str, target_org: str, mirror_interval: str = "8h", clone_wiki: bool = True,
                    filter_repo_list: list[str] | None = None, filter_mode: Literal["include", "exclude"] = "exclude"):
        if filter_repo_list is None:
            filter_repo_list = []

        repos = self.github.list_owner_public_repos(github_owner)
        self.logger.info(
            f"Found {len(repos)} public repositories for owner: {github_owner}")
        filtered_repos = PublicRepoMirror.filter_repos(
            repos, filter_repo_list, filter_mode)
        self.logger.info(
            f"{len(filtered_repos)} repositories to be mirrored after applying filter.")

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Repositories to be mirrored: {filtered_repos}")

        for repo in filtered_repos:
            repo_name = repo.split("/")[1]
            clone_url = GitHub.get_repo_clone_url(repo)
            logging.debug(f"Mirroring repository: {repo_name}")
            self.gitea.migrate_from_github(
                target_org, repo_name, clone_url, self.github.token, mirror_interval, clone_wiki)

    @staticmethod
    def filter_repos(repo_full_names: list[str], filter_repo_names: list[str], mode: Literal["include", "exclude"],):
        """
        Filter repositories based on inclusion or exclusion lists.
        """
        if mode == "include":
            filtered_repos = [
                repo for repo in repo_full_names if repo.split("/")[1] in filter_repo_names]
        elif mode == "exclude":
            filtered_repos = [
                repo for repo in repo_full_names if repo.split("/")[1] not in filter_repo_names]
        else:
            raise ValueError("Mode must be either 'include' or 'exclude'.")
        return filtered_repos
