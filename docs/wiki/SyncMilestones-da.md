<!-- translation of SyncMilestones.md, source sha256 59a0aa110097 -->

> Dette er en oversættelse af [`SyncMilestones`](SyncMilestones). Den engelske side er autoritativ, og ændringer her bliver overskrevet, næste gang wikien publiceres.

[English](SyncMilestones) · **Dansk** · [Bahasa Melayu](SyncMilestones-ms)

# Udgivelse af accepterede milepæle

Sådan bliver et projekts accepterede milepæle til milepæle og issues på Gitea med
det scopede workflow `sync-milestones.yml`. Det erstatter den kopi af
`sync-milestones.yml`, et repository før holdt i `.gitea/workflows/`. Beslutningen
er ADR-0018 i dette repository; hvornår et repository bruger det, står i
[brugsreglerne](https://git.tirsystem.com/TirSystem/git-workflows/src/branch/main/guides/adoption-rules.md#publish-accepted-milestones).

## Hvad det gør

For hvert milepælsdokument i `docs/milestones/` opretter eller opdaterer det
Gitea-milepælen og ét issue pr. opgaverække via
`framework/scripts/ci-publish-milestones.sh publish`, som kører
`sync-project.sh --accepted-only`. Kun en milepæl, hvis seneste række i Version
History er `Accepted`, og hvis seneste gennemgang er en Go, bliver publiceret. En
`Proposed`-milepæl eller en uden Go-gennemgang springes over med årsagen i loggen.

## Mappen er tilvalget

Workflowet er scoped: instansen kører det i hvert repository i organisationen, så
et repository tilføjer ingen fil. Et repository publicerer, når det har mappen
`docs/milestones/`. Et repository uden den slutter grønt, skriver at der intet er
at publicere og foretager intet API-kald.

## Secrets

To organisations-secrets, gemt i den organisation, hvor hvert publicerende
repository ligger. Der er ingen fallback: en kørsel uden en af dem slutter som
`[configuration]` og nævner den. Intet ældre navn (`GITEA_TOKEN`, `SYNC_TOKEN`)
læses, og intet token skrives ud eller sættes på en kommandolinje.

| Secret | Bruges til |
| --- | --- |
| `TOKEN_FOR_GITEA_REPO` | At læse repositories: projektet og det private framework, over HTTPS |
| `TOKEN_FOR_GITEA_ISSUES` | At publicere: kun issues og milepæle |

Scopes, hvem der gemmer dem, og hvordan de udskiftes, står i
[Credentials](Credentials-da).

## Hvor frameworkets scripts kommer fra

Milepælsscriptsene er frameworkets. Workflowet henter dem fra en af to kilder og
skriver i loggen, hvilken:

- **Projektets egen submodul**, når `framework/scripts/ci-publish-milestones.sh`
  findes i repositoryet. Scriptsene er den udgivelse, projektet har fastlåst.
- **En fastlåst udgivelse** ellers: framework-repositoryet hentes ind i
  `framework/` ved tagget `FRAMEWORK_TAG` i `tools/sync_milestones.py`. Tagget
  flyttes kun i en udgivelse af dette repository, og en gren bruges aldrig. Et
  projekt uden submodulen kan derfor også publicere.

Loglinjen nævner kilden og det tag eller den commit, der blev brugt.

## Et push publicerer, en manuel kørsel er en tørkørsel

| Start | Hvad der sker |
| --- | --- |
| Push til standardgrenen, der ændrer `docs/milestones/**` eller `docs/sqa/reviews/**` | Publicerer (`--apply`) |
| Manuel kørsel (`workflow_dispatch`) med `dry_run` slået til (standard) | Skriver planen og opretter intet |
| Manuel kørsel med `dry_run` slået fra | Publicerer |

`--accepted-only` er altid med. Kørsler står i kø i gruppen
`publish-accepted-milestones`, og en kørsel afbryder aldrig en anden. Workflowet
har `permissions: contents: read`.

## Intet lukkes eller slettes

En milepæl, der fjernes fra `docs/milestones/`, lader sin Gitea-milepæl og sine
issues stå, som de er. Workflowet har ingen indstilling, der lukker eller sletter.
Hver rigtig kørsel redigerer issues for alle accepterede milepæle, og værten
registrerer hver redigering.

## Fjern en gammel kopi

En kopi af `sync-milestones.yml` i `.gitea/workflows/` kører ved siden af det
scopede workflow og publicerer to gange. Slet kopien i en pull request i dens
repository; det scopede workflow behøver ingen fil i stedet. Det er ikke længere
nødvendigt at installere frameworkets skabelon `templates/ci/` til dette workflow.

## Skal endnu verificeres på instansen

ADR-0018 hviler på forhold, som MIL-019 opgave 1 endnu ikke har verificeret i en
scoped kørsel:

- at organisations-secrets'ene `TOKEN_FOR_GITEA_REPO` og `TOKEN_FOR_GITEA_ISSUES`
  kan læses;
- at det private framework kan hentes over HTTPS;
- om den indlejrede submodul `framework/qc` er nødvendig for scriptsene (kopien
  hentede den med `--recursive`).

Indtil det er registreret, er denne vejledning beslutningen, ikke et testet
resultat.
