# ADR-0011: A VPN for deployment is delivered as a composite action

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0011 |
| CrossReference | [MIL-012], [ADR-0005], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

A deployment job often has to reach hosts that are not on the internet. [MIL-012] adds a way to bring a VPN up in the job, for WireGuard and for Tailscale. The GitHub marketplace has `tailscale/github-action` for Tailscale; it is written for GitHub Actions, has not been verified on Gitea Actions, and WireGuard has no such action. Every other shared automation of this repository is a reusable workflow ([ADR-0005], [ADR-0009], [ADR-0010]), so the question is whether a VPN is one too.

Options:

1. **A reusable workflow.** Consistent with the rest of the repository. But a called workflow runs as a separate job, on its own runner and network; a tunnel brought up there is gone when that job ends and is never seen by the caller's deployment job. It cannot work.
2. **The marketplace action `tailscale/github-action`.** No code to maintain. Written for GitHub, not verified on Gitea, nothing for WireGuard, and an action from outside the instance that receives the VPN secret.
3. **A composite action of this repository**, one for each VPN, in `actions/<name>/`, called as a step of the caller's own job with `uses:` and `gitea.action_path` for its script. It runs in the job, so the tunnel is there for the steps after it.

Facts: a composite action in a subfolder of this repository resolves on the instance in both the short form (`TirSystem/github-action/actions/<name>@<ref>`) and with the full address, and `gitea.action_path` points at its folder (verified in [MIL-012] task 1, runs 417 and 418 of the instance). A key must not reach a log or a command line. A tunnel needs a network interface, so the runner container needs `NET_ADMIN` and `/dev/net/tun`, which this repository cannot give.

## Decision

A VPN for deployment is delivered as **a composite action of this repository**, one per VPN: `actions/connect-wireguard` and `actions/connect-tailscale`.

- Each action has a script file next to its `action.yml` that does the work. The `run:` lines only call it, and every input reaches the script as an environment variable, never as an interpolated expression ([ADR-0005]).
- Each action has an `up` and a `down` mode. The caller runs `down` in a last step with `if: always()`.
- Secrets are masked first, written only to a file of mode 600 where a file is needed, never printed and never put on a command line.
- The scripts are linted (shellcheck and shfmt) and tested offline with stub commands on every pull request.
- The actions are versioned with the repository ([ADR-0006]); a new action is a minor release, and callers pin the tag.
- The runner is outside the scope of the action: the operator (S03) provides a runner whose container has `NET_ADMIN` and `/dev/net/tun`. The actions state the requirement and fail with a message that names it.

## Consequences

**Positive:**

- The tunnel lives in the job that deploys, which a reusable workflow cannot do.
- One implementation for Gitea, covered by offline tests; no GitHub-only action receives the VPN secret.
- WireGuard and Tailscale share one contract (`up`, `down`, a health check, masked secrets, categorised errors).

**Negative:**

- Two scripts to maintain, and behaviour that stubs cannot show (daemon start-up, `sudo`, the runner's capabilities) is verified only by runs on a real runner ([MIL-012] tasks 3 and 4).
- A composite action cannot declare a post step, so the caller must remember the `down` step; a cancelled job can leave a node or a key file behind until the runner cleans up.
- The action needs a privileged runner, which widens the attack surface of that runner; the guides tell the operator to keep it to a dedicated label.

## Affected Artifacts

- [MIL-012] — the decision behind its deliverable and its tasks 3 and 4.
- [ADR-0005] — the same contract style (script file, environment variables, categorised failures) is used for the actions.
- [ADR-0006] — a new action is a minor release.

---

[MIL-012]: ../milestones/mil-012-vpn-actions-for-deployment.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0006]: ./adr-0006-release-process-and-version-pinning.md
[ADR-0009]: ./adr-0009-wiki-publishing-reusable-workflow.md
[ADR-0010]: ./adr-0010-code-metrics-badges-contract.md
