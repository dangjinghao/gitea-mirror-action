# GITEA-MIRROR-ACTION

A Gitea Action to mirror GitHub repositories to Gitea.

## Usage

GitHub PAT(classic) access scopes:

- repo
- admin:org
- user

It could be more restricted, but I don't test it.

Gitea PAT access scopes:

- write:organization
- write:repository

Example Scheduled workflow:

```yaml
name: mirror my github repo
on:
  schedule:
    - cron: "0 */12 * * *"
jobs:
  github-mirror-dangjinghao:
    runs-on: ubuntu-latest
    steps:
      - uses: dangjinghao/gitea-mirror-action@v2
        with:
          mirror-github-owner: dangjinghao
          mirror-github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          mirror-gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          mirror-gitea-org: ${{ vars.MIRROR_GITEA_ORG }}
          mirror-gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          mirror-clone-wiki: "true"
          mirror-filter-repo-list: ${{ vars.MIRROR_EXCLUDE_REPOS }}

  github-mirror-myorg:
    runs-on: ubuntu-latest
    steps:
      - uses: dangjinghao/gitea-mirror-action@v2
        with:
          mirror-github-owner: myorg
          mirror-github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          mirror-gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          mirror-gitea-org: myorg
          mirror-gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          mirror-clone-wiki: "true"
          mirror-filter-repo-list: ${{ vars.MIRROR_EXCLUDE_REPOS }}
```
