import logging

from gitea_mirror.http_api import GitHub
from .mirror_base import MirrorBase


class PublicRepoMirror(MirrorBase):
    """
    Mirror public GitHub repositories to Gitea.
    """

    def __init__(self, github_token: str, gitea_token: str, gitea_url: str, dry_run: bool = False):
        super().__init__(github_token, gitea_token, gitea_url, dry_run)

    def mirror_repo(self, github_owner: str, target_org: str, mirror_interval: str = "8h", clone_wiki: bool = True,
                    filter_repo_list: list[str] | None = None, filter_mode: str = "exclude"):
        if filter_repo_list is None:
            filter_repo_list = []

        repos = self._github.list_owner_public_repos(github_owner)
        self._logger.info(
            f"Found {len(repos)} public repositories for owner: {github_owner}")
        filtered_repos = PublicRepoMirror.filter_repos(
            repos, filter_repo_list, filter_mode)
        self._logger.info(
            f"{len(filtered_repos)} repositories to be mirrored after applying filter.")

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                f"Repositories to be mirrored: {filtered_repos}")

        self._logger.info(f"Ensuring organization exists: {target_org}")
        self._gitea.ensure_org_exists(target_org)
        existing_repos = self._gitea.list_org_repos(target_org)
        existing_repos_with_raw_owner = [
            f"{github_owner}/{repo.split('/')[1]}" for repo in existing_repos]
        plan_to_mirror_repos = set(
            filtered_repos) - set(existing_repos_with_raw_owner)
        if len(plan_to_mirror_repos) == 0:
            self._logger.info("No repositories to mirror after filtering.")
            return
        for repo in plan_to_mirror_repos:
            repo_name = repo.split("/")[1]
            clone_url = GitHub.get_repo_clone_url(repo)
            self._logger.debug(f"Mirroring repository: {repo_name}")
            if self._dry_run:
                self._logger.info(
                    f"[Dry Run] Would mirror repository: {repo_name} to organization: {target_org}")
                continue
            self._gitea.migrate_from_github(
                target_org, repo_name, clone_url, self._github.token, mirror_interval, clone_wiki)
            self._logger.info(
                f"Mirrored public repository: {repo} to organization: {target_org}")

    @staticmethod
    def filter_repos(repo_full_names: list[str], filter_repo_names: list[str], mode: str):
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
