# Reaching a private network with WireGuard

The composite action `actions/connect-wireguard` brings a WireGuard tunnel up on
a Gitea Actions runner, so the next steps of the same job (a deployment over
SSH, a database migration) can reach hosts that are not on the internet. It is
the WireGuard counterpart of the Tailscale action. It is **experimental**: it
is released in 2.2.0, and it has not yet run on a runner with a real tunnel
(MIL-012).

A tunnel belongs to one job: every job that deploys brings its own tunnel up
and takes it down. It cannot be a reusable workflow, because a called workflow
runs as a separate job.

## Use it

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2

      - name: Connect the VPN
        uses: TirSystem/git-workflows/actions/connect-wireguard@v2
        with:
          config: ${{ secrets.WG_CONFIG }}
          health-check-host: 10.8.0.1

      - name: Deploy
        run: ssh deploy@10.8.0.10 ./deploy.sh

      - name: Disconnect the VPN
        if: always()
        uses: TirSystem/git-workflows/actions/connect-wireguard@v2
        with:
          action: down
```

If the short form does not resolve on your instance (Gitea looks for the action
on the host set in `DEFAULT_ACTIONS_URL`), use the full address:
`https://git.tirsystem.com/TirSystem/git-workflows/actions/connect-wireguard@v2`.

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `action` | `up` | `up` or `down` |
| `config` | | A complete wg-quick file, as a secret. When set, the fields below are ignored |
| `private-key`, `address`, `peer-public-key`, `endpoint`, `allowed-ips` | | The fields of a configuration, all five needed without `config` |
| `preshared-key`, `dns` | | Optional |
| `persistent-keepalive` | `25` | Seconds |
| `interface` | `wg0` | Interface name |
| `health-check-host` | | A host behind the tunnel; the step fails when it does not answer a ping |

## Set it up

1. On the WireGuard server add one peer for CI, with its own key pair and an
   address inside the tunnel (`10.8.0.2/32`). Let it reach only the hosts the
   deployment needs.
2. Store the configuration (or the private key) as a secret of the
   organization, never in the repository. Give the secret a name that does not
   start with `GITEA_` or `GITHUB_`.
3. Set `allowed-ips` to the private network only. `0.0.0.0/0` sends all of the
   job's traffic, including the checkout, through the tunnel.
4. Rotate the key when a person with access to the secret leaves.

## The runner must allow it

A tunnel needs a network interface, so the runner needs more than a plain job
container:

- the job runs as root, or `sudo` is available (the action uses `sudo` only
  when the job is not root, and installs `wireguard-tools` with `apt` when it is
  missing, so a Debian or Ubuntu image);
- the container has the capability `NET_ADMIN` and the device `/dev/net/tun`.
  In the `act_runner` configuration set under `container:`
  `options: "--cap-add=NET_ADMIN --device=/dev/net/tun"`;
- without the kernel module the action uses `wireguard-go` (user space), which
  needs the same capability and device.

Use a dedicated runner with a label of its own (for example `vpn`) and put
`runs-on: vpn` on the jobs that need it, so the other jobs do not get the extra
privilege.

## What the action does

- masks the keys in the log before anything else (the values of `PrivateKey`
  and `PresharedKey` of a full configuration, and the key inputs);
- refuses an input that holds a line break, because an extra line in the file
  could add a `PostUp` command that runs as root;
- writes `/etc/wireguard/<interface>.conf` with mode 600 and brings it up with
  `wg-quick` (through `env`, so the `wireguard-go` choice survives `sudo`); the
  file is removed again when the interface does not come up;
- prints errors as `::error::[category] message`, with the categories
  `configuration`, `environment` and `connection`;
- on `down` takes the interface down and deletes the file.

It never prints a key. Do not turn on shell tracing (`set -x`) in the steps
that follow.

## Troubleshooting

| Message | Cause |
| --- | --- |
| `[configuration] ... is empty` | Neither `config` nor all five fields were given |
| `[environment] ... NET_ADMIN and /dev/net/tun` | The runner container lacks the capability or the device |
| `[connection] wg-quick could not bring wg0 up` | A wrong key, endpoint or a firewall; run `wg show` on the server |
| `[connection] health-check-host ... does not answer` | The tunnel is up but the host is not in `allowed-ips`, or is blocked |
