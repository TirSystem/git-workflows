# Reaching a tailnet with Tailscale

The composite action `actions/connect-tailscale` joins a Tailscale network from
a Gitea Actions runner, so the next steps of the same job (a deployment over
SSH, a migration) can reach hosts on the tailnet. It does what the GitHub
marketplace action `tailscale/github-action` does, written for Gitea Actions:
that action is built for GitHub and has not been verified on Gitea. It is
**experimental**: it lives on the branch `wireguard-vpn-action` until a trial
shows it is wanted. For a plain tunnel without a third-party service, see
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
        uses: TirSystem/github-action/actions/connect-tailscale@v2
        with:
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci
          version: 1.80.2
          health-check-host: deploy-host

      - name: Deploy
        run: ssh deploy@deploy-host ./deploy.sh

      - name: Disconnect Tailscale
        if: always()
        uses: TirSystem/github-action/actions/connect-tailscale@v2
        with:
          action: down
```

If the short form does not resolve on your instance (Gitea looks for the action
on the host set in `DEFAULT_ACTIONS_URL`), use the full address:
`https://git.tirsystem.com/TirSystem/github-action/actions/connect-tailscale@v2`.
To try the branch before it is released, replace `@v2` with
`@wireguard-vpn-action`.

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `action` | `up` | `up` or `down` |
| `authkey` | | A Tailscale auth key, as a secret. Give this or `oauth-secret` |
| `oauth-secret` | | The secret of an OAuth client with the scope `auth_keys`, as a secret. Needs `tags` |
| `tags` | | ACL tags of the node, `tag:ci` or `tag:ci,tag:deploy`. Required with `oauth-secret` |
| `hostname` | runner name | Name of the node in the tailnet |
| `version` | `latest` | The version to install when the runner has no `tailscale`. Pin it |
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

The node is ephemeral and its state is kept in memory, so it disappears from the
tailnet when the job ends, even if the last step does not run.

## The runner

- The job runs as root or can use `sudo`. The action downloads the Tailscale
  binaries from `pkgs.tailscale.com` when `tailscale` is not on the runner.
  Pin `version`; a runner image that already contains Tailscale skips the
  download.
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
- on `down` logs the node out, stops `tailscaled` and deletes its work folder.

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
