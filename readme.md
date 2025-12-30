# GITEA-MIRROR-ACTION

A Gitea Action to mirror GitHub repositories to Gitea.

Based on [gitea-github-mirror](https://github.com/filipnet/gitea-github-mirror).

## Usage

GitHub PAT(classic) access scopes:

- repo
- admin:org
- user

It could be more restricted, but I don't test it.

Gitea AT access scopes:

- write:organization
- write:repository

Example Scheduled workflow:

```yaml
name: mirror my github repo
on:
  schedule:
    - cron: "0 */12 * * *"
jobs:
  github-mirror:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Mirror all my GitHub repositories to Gitea
        uses: dangjinghao/gitea-mirror-action@v1
        with:
          mirror-github-owner: dangjinghao
          mirror-github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          mirror-gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          mirror-gitea-org: ${{ vars.MIRROR_GITEA_ORG }}
          mirror-gitea-user: ${{ vars.MIRROR_GITEA_USER }}
          mirror-gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          mirror-clone-wiki: true
          mirror-exclude-repos: "${{ vars.MIRROR_EXCLUDE_REPOS }}"
          mirror-debug: false
      - name: Mirror all my organization's repositories to Gitea
        uses: dangjinghao/gitea-mirror-action@v1
        with:
          mirror-github-owner: my-org
          mirror-github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          mirror-gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          mirror-gitea-org: ${{ vars.MIRROR_GITEA_ORG }}
          mirror-gitea-user: ${{ vars.MIRROR_GITEA_USER }}
          mirror-gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          mirror-clone-wiki: true
          mirror-exclude-repos: "${{ vars.MIRROR_EXCLUDE_REPOS }}"
          mirror-debug: false
```
