# Reaching a tailnet with Tailscale

The composite action `actions/connect-tailscale` joins a Tailscale network from
a Gitea Actions runner, so the next steps of the same job (a deployment over
SSH, a migration) can reach hosts on the tailnet. It does what the GitHub
marketplace action `tailscale/github-action` does, written for Gitea Actions:
that action is built for GitHub and has not been verified on Gitea. It is
**experimental**: it is on `main` but not released, and it has not yet run on a
runner with a real tailnet (MIL-012). For a plain tunnel without a third-party service, see
[WireGuard](vpn-wireguard.md).

A node belongs to one job: every job that deploys joins on its own and logs out
in a last step. It cannot be a reusable workflow, because a called workflow runs
as a separate job.

## Use it

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2

      - name: Connect Tailscale
        uses: TirSystem/github-action/actions/connect-tailscale@main
        with:
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci
          version: 1.80.2
          health-check-host: deploy-host

      - name: Deploy
        run: ssh deploy@deploy-host ./deploy.sh

      - name: Disconnect Tailscale
        if: always()
        uses: TirSystem/github-action/actions/connect-tailscale@main
        with:
          action: down
```

If the short form does not resolve on your instance (Gitea looks for the action
on the host set in `DEFAULT_ACTIONS_URL`), use the full address:
`https://git.tirsystem.com/TirSystem/github-action/actions/connect-tailscale@main`.

Until release 2.2.0 the actions exist only on `main`, so the examples call
`@main`; `@v2` does not contain them yet. After the release, use `@v2`.

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `action` | `up` | `up` or `down` |
| `authkey` | | A Tailscale auth key, as a secret. Give this or `oauth-secret` |
| `oauth-secret` | | The secret of an OAuth client with the scope `auth_keys`, as a secret. Needs `tags` |
| `tags` | | ACL tags of the node, `tag:ci` or `tag:ci,tag:deploy`. Required with `oauth-secret` |
| `hostname` | runner name | Name of the node in the tailnet |
| `version` | | The exact version to install when the runner has no `tailscale`, for example `1.80.2`. Empty uses the installed one and fails when there is none |
| `sha256` | | The SHA-256 of the downloaded archive `tailscale_<version>_<arch>.tgz`; the install fails when it differs. Recommended |
| `userspace-networking` | `false` | `true` runs without a TUN device |
| `args` | | Extra flags for `tailscale up`, for example `--accept-routes`. Never a secret |
| `timeout` | `60` | Seconds to wait for the node |
| `health-check-host` | | A tailnet host that must answer a Tailscale ping |

## Set it up

1. In the Tailscale admin console define a tag for CI (`tag:ci`) in the policy
   file, with the owners that may use it, and an access rule that lets
   `tag:ci` reach only the hosts and ports the deployment needs.
2. Create either an **OAuth client** with the scope `auth_keys` (write) for that
   tag, or an **auth key** that is reusable only when needed, ephemeral,
   pre-authorized and tagged. The OAuth client is preferred: it does not expire
   the way a key does, and each run gets a fresh ephemeral key.
3. Store the secret as a secret of the organization, with a name that does not
   start with `GITEA_` or `GITHUB_`.
4. Rotate the secret when a person with access leaves.

The state of the node is kept in memory. With an OAuth client the key is
ephemeral, so the node disappears from the tailnet when the job ends, even if
the last step does not run. With an auth key that is not ephemeral, a cancelled
job can leave the node in the tailnet until `down` runs or it is removed in the
admin console: create the key as ephemeral.

## The runner

- The job runs as root, or `sudo` is available (the action uses `sudo` only
  when the job is not root). The action downloads the Tailscale binaries from
  `pkgs.tailscale.com` when `tailscale` is not on the runner; `version` is then
  required, and `sha256` makes the install check the archive. A runner image
  that already contains Tailscale skips the download.
- The action starts its own `tailscaled`. It refuses to run when a `tailscaled`
  already answers on the runner, because that daemon belongs to the host and
  `down` would log it out: use the action on job containers, not on a runner
  that runs jobs directly on a host with its own Tailscale.
- **TUN mode** (the default) needs the capability `NET_ADMIN` and the device
  `/dev/net/tun` in the runner container: in the `act_runner` configuration set
  under `container:` `options: "--cap-add=NET_ADMIN --device=/dev/net/tun"`.
- **Userspace mode** (`userspace-networking: true`) needs neither, but the
  tailnet is then reached only through a SOCKS5 proxy on `localhost:1055`:

  ```bash
  ssh -o ProxyCommand="nc -X 5 -x localhost:1055 %h %p" deploy@deploy-host
  ```

  Tools that cannot use a proxy do not work in this mode.
- Use a dedicated runner with a label of its own (for example `vpn`) for jobs
  that join a tailnet.
- The daemon is started in the background of the "Run the Tailscale step". That
  it stays alive for the following steps of the job has to be confirmed on the
  runner in use; the first trial must do so.

## What the action does

- masks the secrets in the log first;
- passes the auth key to `tailscale up` in a file of mode 600 (`--auth-key=file:`),
  never on a command line, and deletes the file at once;
- prints errors as `::error::[category] message`, with the categories
  `configuration`, `environment` and `connection`;
- waits until `tailscaled` answers before `tailscale up` (up to 30 seconds);
- on `down` logs the node out, stops `tailscaled` and deletes its work folder,
  and only when this action started that daemon.

The `file:` form of `--auth-key` needs a recent Tailscale; with an old pinned
version `tailscale up` reports an invalid key.

## Troubleshooting

| Message | Cause |
| --- | --- |
| `[configuration] give authkey or oauth-secret` | Neither was given, or both |
| `[configuration] tags is required` | `oauth-secret` without `tags` |
| `[environment] could not download` | The runner cannot reach `pkgs.tailscale.com`, or the version does not exist |
| `[connection] tailscale up failed` | A wrong or expired key, a tag the client may not use, or a missing TUN device (try `userspace-networking`); the last lines of `tailscaled` follow |
| `[connection] health-check-host ... does not answer` | The access rule does not let `tag:ci` reach the host |
