
import httpx


class PATRepo:
    full_name: str
    private: bool

    def __init__(self, full_name: str, private: bool):
        self.full_name = full_name
        self.private = private


class GitHub:
    _BASE_URL = "https://api.github.com"
    token: str
    _headers: dict[str, str]

    def __init__(self, token: str):
        self.token = token
        self._headers = {
            "Authorization": f"token {token}",
            'X-GitHub-Api-Version': '2022-11-28',
            "Accept": "application/vnd.github+json"
        }

    @staticmethod
    def get_repo_clone_url(full_name: str) -> str:
        return f"https://github.com/{full_name}.git"

    def list_owner_public_repos(self, owner: str) -> list[str]:
        """
        List **PUBLIC** repositories for the specified owner.
        Args:
            owner (str): GitHub user or organization name.
        Returns:
            list[str]: A list of repository full names (e.g., "owner/repo").
        """
        repos = []
        page = 1
        per_page = 100
        url = f"{self._BASE_URL}/repos/{owner}/repos"

        while True:
            params = {
                "per_page": per_page,
                "page": page
            }
            response = httpx.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1

        return [r['full_name'] for r in repos]

    def list_pat_user_repos(self) -> list[PATRepo]:
        """
        List repositories accessible by the provided PAT.
        Returns:
            list[str]: A list of repository full names (e.g., "owner/repo").
        """
        repos = []
        page = 1
        per_page = 100
        url = f"{self._BASE_URL}/user/repos"

        while True:
            params = {
                "per_page": per_page,
                "page": page
            }
            response = httpx.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                break
            repos.extend(data)
            if len(data) < per_page:
                break
            page += 1

        return [PATRepo(r['full_name'], r['private']) for r in repos]
