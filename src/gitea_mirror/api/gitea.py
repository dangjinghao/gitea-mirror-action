
import httpx


class Gitea:
    url: str
    token: str
    headers: dict[str, str]

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }

    def get_org_repos(self, org: str) -> list[str]:
        """
        Get list of repositories in the specified Gitea organization.
        """
        repos = []
        page = 1
        per_page = 100
        base_url = f"{self.url}/api/v1/orgs/{org}/repos"

        while True:
            url = f"{base_url}?limit={per_page}&page={page}"

            response = httpx.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1
        return repos

    def ensure_org_exists(self, org: str):
        """
        Ensure that the specified Gitea organization exists.
        """
        gitea_org_api = f"{self.url}/api/v1/orgs/{org}"
        response = httpx.get(gitea_org_api, headers=self.headers)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            response.raise_for_status()

    def migrate_from_github(self, to_org: str, repo_name: str, clone_url: str, github_token: str, mirror_interval: str = "8h", clone_wiki: bool = True, private: bool = False):
        """
        Migrate a repository to Gitea.
        """
        gitea_migrate_api = f"{self.url}/api/v1/repos/migrate"
        data = {
            "clone_addr": clone_url,
            "repo_name": repo_name,
            "repo_owner": to_org,
            "mirror": True,
            "mirror_interval": mirror_interval,
            "auth_token": github_token,
            "wiki": clone_wiki,
            "private": private,
            "service": "github"
        }
        response = httpx.post(
            gitea_migrate_api, headers=self.headers, json=data)
        response.raise_for_status()
