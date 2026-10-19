# MIL-012: VPN actions for deployment (WireGuard and Tailscale)

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-012 |
| CrossReference | [BC-001], [US-001], [MIL-004], [MIL-011], [ADR-0006] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; reviewed (RC-080), accepted by the author in chat as stand-in for S01 with target date 2026-11-06 | [c5d5941] |

---

## Purpose

Decide whether a deployment job on a Gitea runner can reach a private network through a shared, versioned action, and release it if it can.

A deployment often has to reach hosts that are not on the internet. The GitHub marketplace has the action `tailscale/github-action` for a Tailscale network; it is written for GitHub Actions and has not been verified on Gitea Actions. WireGuard has no equivalent action at all. Two experimental composite actions for Gitea Actions already exist on the unreleased branch `wireguard-vpn-action` (`actions/connect-wireguard`, `actions/connect-tailscale`), with guides and offline tests (574 tests pass), but neither has run on a real runner, and the one question that decides whether the Tailscale action works is open: whether `tailscaled`, started in the background of one step, is still alive in the next step of the job.

This milestone runs both on a real runner of the instance, fixes what that shows, and releases them. It adds a capability, so it is a minor release ([ADR-0006]).

## Deliverable

Release `2.2.0` of this repository with two composite actions, `actions/connect-wireguard` and `actions/connect-tailscale`, each with a guide, a README section, wiki pages in English, Danish and Bahasa Malaysia, a changelog entry under `Added`, and an offline test. A record of one successful deployment-shaped job per action on the instance. An ADR for the decision to deliver a VPN as a composite action. In `TirSystem/sqa-qc-framework`: the templates `deploy-wireguard.yml` and `deploy-tailscale.yml` pinned to the release tag instead of the branch, in a pull request of their own.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A `uses:` of a composite action in a subfolder of this repository (`TirSystem/github-action/actions/<name>@<ref>`) resolves on the instance; the form that works (short, or the full address) is recorded | A run starts and executes the action; the form is recorded | No form resolves |
| 2 | `connect-wireguard` brings a tunnel up on a runner of the instance, a following step reaches a host behind the tunnel, and the `down` step removes the interface and the file | Recorded run; `wg show` and the file are absent afterwards | The tunnel is not up in the following step, or anything remains |
| 3 | `connect-tailscale` joins a tailnet on a runner of the instance in TUN mode and in userspace mode, a following step reaches a tailnet host, and `down` leaves no node in the tailnet | Recorded run for both modes; the node list shows no node afterwards | `tailscaled` does not survive to the next step, or a node remains |
| 4 | No secret appears in any log of the runs above (auth key, OAuth secret, WireGuard keys), checked by a search of the run logs for the secret values | Count is 0 | A secret value appears in a log |
| 5 | The runner requirements are recorded as verified: the container options, the label, and whether `wireguard-go` or the kernel module was used | Recorded in both guides | A requirement is only assumed |
| 6 | The scripts of the actions are linted (shellcheck, shfmt) and their tests run on every pull request in `validate-workflows.yml`; a seeded error fails the run | Fails on a seeded error, passes on the fix | Not part of the validation |
| 7 | The README, both guides and the wiki pages (English, Danish, Bahasa Malaysia) describe the actions at `@v2` and no longer call them experimental; a search of `guides/`, `README.md` and `docs/wiki/` finds no `@wireguard-vpn-action` | Count is 0 | A page still names the branch |
| 8 | The release is a minor (`2.2.0`): the changelog has an `Added` entry, the major tag `v2` moves to it, and `v1` is not touched | Released | Another level, or `v1` moved |
| 9 | The framework templates name the release tag, not the branch, in a pull request of `TirSystem/sqa-qc-framework` opened after release 2.2.0 | Pull request open with the tag | A template names the branch |
| 10 | Reviewed | A review record (`RC-*`) for this milestone, the actions, the tests and the guides, each with a verdict of Go | An instance without a record |

## Dependencies

| Depends on | Reason |
| --- | --- |
| [MIL-004] | The release process and the Release workflow that publish `2.2.0` |
| [MIL-011] | The default `tools-ref` and the `MAJOR_TAG` file; the release is the first after the fix |
| [ADR-0006] | A new capability is a minor release, and a moving major tag follows it |
| A runner with `NET_ADMIN`, `/dev/net/tun` and a label of its own (S03) | Both actions need a network interface; outside this repository, set up by the runner's operator |
| A WireGuard peer and a Tailscale tag with an OAuth client (S03) | Test peers for criteria 2 and 3; secrets held by the operator, never in this repository |
| `TirSystem/sqa-qc-framework`, branch `ssdf-workflow-selection-vpn` | Holds the templates and the rules that call the actions; criterion 9 changes it in its own pull request |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Business Case objective O6: a shared, versioned action that brings a VPN up for a deployment job on a Gitea runner | [BC-001] |
| User stories | [US-001] (no new story: the tasks below are technical; the actions are used by deployment jobs, not by a person) |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S05 |
| Approving reviewer | S01 |

## Target Date

2026-11-06 (Friday), proposed: two weeks of work from 2026-10-26, because the trials need a runner with extra privileges and test peers that the operator must set up. It overlaps [MIL-002] (2026-10-19 to 2026-10-31), which is documentation and does not touch the runners' network. The Business Case sets no deadline. S01 confirmed the date when accepting this milestone, in chat on 2026-10-19.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Check that a subfolder action resolves | On a throwaway branch of a repository, call `actions/connect-wireguard` and `actions/connect-tailscale` with the short form and with the full address, at the branch. Record which form starts a run and the message when one does not. | No | |
| 2 | Prepare the trial runner | With the operator: a runner labelled `vpn` whose container has `NET_ADMIN` and `/dev/net/tun`; a WireGuard peer and a host behind it; a Tailscale tag, an OAuth client and a host in the tailnet. Secrets are stored as organization secrets and are not recorded here. | No | |
| 3 | Verify `connect-wireguard` | Run a deployment-shaped job (connect, reach the host over the tunnel, disconnect with `if: always()`) with a kernel module and with `wireguard-go`. Record the runs and what remains on the runner. Fix the script where it fails and extend the tests. | No | [MIL-012] |
| 4 | Verify `connect-tailscale` | Run the same job in TUN and in userspace mode. Decide whether `tailscaled` survives to the next step; if it does not, change how it is started (for example `setsid`, or a post step) and test it. Record the node list after the run. | No | [MIL-012] |
| 5 | Search the logs for secrets | Search every run log of tasks 3 and 4 for the secret values and for the key file path; fix any leak. | No | |
| 6 | Lint and test the action scripts in CI | Add shellcheck and shfmt for `actions/**/*.sh` and the two test files to `validate-workflows.yml`; show a seeded error fails the run. | No | [MIL-001] |
| 7 | Remove the experimental notices | Update both guides with the verified runner requirements, change `@wireguard-vpn-action` to `@v2` everywhere, and add the README section for the actions. | No | |
| 8 | Wiki pages | Add pages for the two actions in English, Danish and Bahasa Malaysia, following the wiki rules of [MIL-005], and register them in the wiki index. | No | [MIL-005] |
| 9 | Record the decision and the objective | Write an ADR: a VPN is delivered as a composite action, not as a reusable workflow (a called workflow runs as a separate job), and not through the marketplace action (written for GitHub). Objective O6, its scope item and success criterion 6 are already in [BC-001], and the schedule row, Gantt bar, scope entry, dependency and risk are in [PP-001] (added at acceptance, [RC-080], [RC-081]); this task writes the ADR only. | No | [ADR-0006] |
| 10 | Release 2.2.0 | Add the `Added` entry to the changelog, run the Release workflow (dry run first), and check that `v2` points at `v2.2.0` and `v1` is unchanged. | No | [ADR-0006] |
| 11 | Pin the framework templates | In `TirSystem/sqa-qc-framework`, change `@wireguard-vpn-action` to `@v2` in the two templates and the branch guide, remove the "experimental" notes that the release resolves, and open the pull request after release 2.2.0. This is a change in another repository, in its own pull request. | No | |
| 12 | Review | Record `RC-*` for this milestone, the actions with their tests, and the guides, each with a verdict. | No | |

---

[BC-001]: ../business-case.md
[US-001]: ../user-stories.md
[MIL-001]: ./mil-001-stabilise-metadata-sync.md
[MIL-002]: ./mil-002-onboarding-and-operations.md
[MIL-004]: ./mil-004-versioned-release.md
[MIL-005]: ./mil-005-wiki-and-translations.md
[MIL-011]: ./mil-011-code-metrics-default-tools-ref.md
[MIL-012]: ./mil-012-vpn-actions-for-deployment.md
[RC-080]: ../sqa/reviews/rc-080-mil-012-plan.md
[RC-081]: ../sqa/reviews/rc-081-bc-001-o6.md
[ADR-0006]: ../adr/adr-0006-release-process-and-version-pinning.md
[PP-001]: ../project-plan.md
[c5d5941]: https://git.tirsystem.com/TirSystem/github-action/commit/c5d59418698316866807388bf61dcb6166d9fa8b
