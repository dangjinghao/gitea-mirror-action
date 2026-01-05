# gitea-mirror-action

A composite Action that mirrors GitHub repositories into Gitea organizations.

This project is primarily tested on **Gitea Actions**. It may also work on GitHub Actions, but that is not the main target.

## Modes

- **Public mode** (`fetch-from-pat: "false"`): mirror **public** repositories for one GitHub owner(user/organization) into one Gitea organization.
- **PAT mode** (`fetch-from-pat: "true"`): mirror repositories accessible by a GitHub token (public + private, if the token has access) and map GitHub owners to Gitea orgs.

## Recommended token scopes

GitHub token (classic PAT):

- repo
- admin:org
- user

This action has not been exhaustively tested with the most minimal scope set.

Gitea token:

- `write:organization` (create/ensure orgs)
- `write:repository` (mirror/create repos)

## v2

`dangjinghao/gitea-mirror-action@v2` is implemented in Python and runs as a composite action.

### Inputs

See the full list in [action.yml](action.yml). Common inputs:

- `fetch-from-pat` (**required**): `"true"` (PAT mode) or `"false"` (public mode)
- `github-token` (**required**)
- `gitea-url` (**required**)
- `gitea-token` (**required**)
- `debug`: `"true"` / `"false"`
- `dry-run`: `"true"` / `"false"`
- `mirror-interval`: e.g. `8h`, `60m`
- `clone-wiki`: `"true"` / `"false"`
- `filter-mode`: `include` or `exclude` (default: `exclude`)

Mode-specific inputs:

- Public mode: `github-owner`, `gitea-org`, `filter-repo-list`
- PAT mode: `org-map`, `filter-shell-patterns`
  - If `org-map` doesn't contain a map that matchs a repository which will be mirrored, and there isn't a default map `*:xxx`, this repository will be skipped with a warn log printed.

Filtering notes:

- Public mode uses `filter-repo-list` (comma-separated repo names like `repo1,repo2`).
- PAT mode uses `filter-shell-patterns` (comma-separated shell patterns matching `owner/repo`, e.g. `myorg/*,someone/repo1`).
- In PAT mode, `filter-shell-patterns` defaults to `*`. With the default `filter-mode: exclude`, that would exclude everything.
  - It is recommended to change this value.

### Example (PAT mode)

```yaml
name: Mirror GitHub repos to Gitea
on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

jobs:
  mirror-with-pat:
    runs-on: ubuntu-latest
    steps:
      - uses: dangjinghao/gitea-mirror-action@v2
        with:
          fetch-from-pat: "true"
          github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          clone-wiki: "true"
          mirror-interval: "8h"
          filter-mode: "include"
          filter-shell-patterns: ${{ vars.FILTER_SHELL_PATTERNS }}
          org-map: ${{ vars.ORG_MAP }}
          debug: ${{ vars.DEBUG }}
          dry-run: ${{ vars.DRY_RUN }}
```

Example variables:

- `DEBUG`: `false`
- `DRY_RUN`: `false`
- `FILTER_SHELL_PATTERNS`: `dangjinghao/exclude-code,myfriend/*`
- `ORG_MAP`: `dangjinghao:gh-djh,myorg:myorg,*:default-org`

How PAT mode works:

- `org-map` maps a GitHub owner/org to a Gitea org.
  - `*:some-org` acts as a default mapping.
- Repositories are mirrored to the mapped org. If the target Gitea org does not exist, it will be created.
- Repo visibility is preserved when mirroring (private stays private).

### Example (public mode)

```yaml
jobs:
  mirror-public:
    runs-on: ubuntu-latest
    steps:
      - uses: dangjinghao/gitea-mirror-action@v2
        with:
          fetch-from-pat: "false"
          github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          github-owner: "some-owner"
          gitea-org: "some-gitea-org"
          filter-mode: "exclude"
          filter-repo-list: "repo-to-skip-1,repo-to-skip-2"
```

## v1

`dangjinghao/gitea-mirror-action@v1` depends on [gitea-github-mirror](https://github.com/filipnet/gitea-github-mirror) with [my modificaion](https://github.com/dangjinghao/gitea-github-mirror). **Only public repository mirror is supported by v1.**

### Inputs

```yaml
inputs:
  mirror-github-owner:
    description: "GitHub owner (username or organization)"
    required: true
  mirror-github-token:
    description: "GitHub personal access token with repo read access"
    required: true
  mirror-gitea-url:
    description: "URL to your Gitea instance (e.g. https://git.example.com)"
    required: true
  mirror-gitea-org:
    description: "Gitea organization where mirrors will be created"
    required: true
  mirror-gitea-user:
    description: "Gitea user that owns the API token"
    required: true
  mirror-gitea-token:
    description: "Gitea API token with write permissions"
    required: true
  mirror-clone-wiki:
    description: "Whether to clone wiki (true/false)"
    required: false
    default: "false"
  mirror-filter-mode:
    description: 'Filter mode: "include" or "exclude"'
    required: false
    default: "exclude"
  mirror-include-repos:
    description: "Space-separated list of repos to include (only used if filter-mode=include)"
    required: false
    default: ""
  mirror-exclude-repos:
    description: "Space-separated list of repos to exclude (only used if filter-mode=exclude)"
    required: false
    default: ""
  mirror-mirror-interval:
    description: "Mirror sync interval (e.g. 8h, 60m)"
    required: false
    default: "8h"
  mirror-debug:
    description: "Enable debug mode (true/false)"
    required: false
    default: "true"
  mirror-dry-run:
    description: "Enable dry-run mode without making changes (true/false)"
    required: false
    default: "false"
```

### Exmaple

```yaml
name: mirror github repo
on:
  schedule:
    - cron: "0 0 * * *"
jobs:
  github-mirror-dangjinghao:
    runs-on: ubuntu-latest
    steps:
      - uses: dangjinghao/gitea-mirror-action@v2
        with:
          mirror-github-owner: dangjinghao
          mirror-clone-wiki: "true"
          mirror-filter-repo-list: ${{ vars.MIRROR_EXCLUDE_REPOS }}
          mirror-github-token: ${{ secrets.MIRROR_GITHUB_TOKEN }}
          mirror-gitea-url: ${{ vars.MIRROR_GITEA_URL }}
          mirror-gitea-token: ${{ secrets.MIRROR_GITEA_TOKEN }}
          mirror-gitea-org: ${{ vars.MIRROR_GITEA_ORG }}

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
