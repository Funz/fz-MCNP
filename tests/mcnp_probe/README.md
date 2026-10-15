# Sondes MCNP : consolidation des hypothèses du plugin

Jeux de données courts (Godiva, 5 000 à 10 000 neutrons/cycle ; une source fixe photons)
destinés à être lancés avec un MCNP réel. Les sorties servent à :

- trancher les hypothèses sur lesquelles reposent `MCNP.sh` et l'extraction des sorties de `MCNP.json` ;
- confirmer les affirmations de la notice synthétique MCNP (skill v0.2 : `input-MCNP.md`, `output-MCNP.md`,
  `error-MCNP.md` ; messages annoncés comme reproduits avec MCNP 6.3.0, sans sortie jointe) ;
- remplacer les fichiers de référence synthétiques (`tests/fixtures/synthetic/`) par des sorties réelles.

## Lancement

```bash
cd tests/mcnp_probe
MCNP_CMD=/chemin/vers/mcnp6 DATAPATH=/chemin/vers/MCNP_DATA ./run_probe.sh
# MCNP_CMD   : défaut mcnp6 dans le PATH, sinon $MCNP_PATH/MCNP_CODE/bin/mcnp6 ou $MCNP_PATH/bin/mcnp6
# DATAPATH   : répertoire contenant xsdir (défaut : $MCNP_PATH/MCNP_DATA s'il existe)
# MCNP_TASKS : nombre de threads (option "tasks N"), ex. MCNP_TASKS=4
# MCNP_OPTS  : options supplémentaires de la ligne de commande
# MCNP_LABEL : suffixe de l'archive (ex. mcnp63)
# filtre optionnel sur les noms de cas : ./run_probe.sh 'ok_*'
```

Chaque cas est lancé comme le fait le plugin : `mcnp6 i=<cas>.i o=outp [tasks N] [MCNP_OPTS]`.
Durée totale estimée : quelques minutes (dominée par `ok_baseline`, `ok_lib_00c` : 1,3 M histoires ;
`ok_ctme` : 0,3 min par construction).

Test de bout en bout via fz (depuis la racine du dépôt) :

```bash
MCNP_CMD=/chemin/vers/mcnp6 DATAPATH=/chemin/vers/MCNP_DATA python3 tests/mcnp_probe/run_fz_e2e.py
```

Exécute le plugin (`localhost_MCNP` → `MCNP.sh`) sur `examples/godiva.inp` (rayons 8,5 / 8,7407 / 9,0).

Fichiers à transmettre : `results-<label>-<date>.tar.gz` et `results-fz-e2e/`.
Chaque cas contient l'entrée, `outp` (ou `outq`), `stdout.txt`, `stderr.txt`, `mctal` s'il existe,
le code de retour (`.exit_code`), la durée et la liste des fichiers produits (`.files_after`).
Les fichiers de reprise binaires (`runtpe`, `*.h5`) sont listés puis supprimés ; les fichiers de
plus de 20 Mo sont remplacés par un extrait. `summary.txt` résume l'ensemble, y compris les
valeurs extraites par le modèle `MCNP.json` (si fz est installé).

## Acquis (sans exécution dans cette révision)

- Sortie réelle MCNP 6.1 (cas Godiva du plugin Java `plugin-MCNP`, 2018) : ligne keff
  `| the final estimated combined collision/absorption/track-length keff = 1.00248 with an estimated
  standard deviation of 0.00062 |`, bannière `run terminated when    1010 kcode cycles were done.`
  (deux occurrences), `mcrun  is done` sur la sortie standard seulement. Fichier de référence :
  `tests/fixtures/mcnp6.1/ok_godiva/`.
- Le plugin fz précédent ne pouvait pas fonctionner : `MCNP.sh` sortait en code 2 (« Usage ») quand
  fz lui passait un seul fichier d'entrée (cas normal), et l'extraction utilisait `match(s, re, arr)`,
  propre à gawk (erreur de syntaxe avec mawk, awk par défaut de Debian/Ubuntu, et avec l'awk BSD de macOS).

## Hypothèses testées

| Id | Hypothèse | Cas |
|---|---|---|
| H1 | Fichiers produits avec `i=<cas> o=outp` : `outp`, `runtpe` ou `runtpe.h5` (6.3), `srctp`, `mctal` seulement avec `PRDMP` | `ok_baseline`, `ok_tally_kcode` |
| H2 | Ligne keff finale identique en 6.3 (`the final estimated combined collision/absorption/track-length keff = ... with an estimated standard deviation of ...`) | `ok_baseline` |
| H3 | Fin normale : `run terminated when ...` dans `outp` (texte en source fixe : `... particle histories were done.`) | `ok_*` |
| H4 | Code retour de `mcnp6` : 0 en fin normale ; valeur en erreur fatale / bad trouble / particules perdues (non utilisé par le plugin tant que non établi) | tous |
| H5 | Format `  fatal error.  <message>` en début de ligne dans `outp` ; message après la ligne d'entrée fautive | `err_no_mcard`, `err_hash_comment` |
| H6 | Format `bad trouble in subroutine <s> of <module>` suivi de la raison sur la ligne suivante, dans `outp` ; sous-programme pour une table absente (`ixsdir` ou `rhoden`, skill v0.2) | `err_missing_blank`, `err_ksrc_outside`, `err_missing_zaid` |
| H7 | Arrêt sur particules perdues : `run terminated because  10 particles got lost.` + `no final keff estimate` | `err_lost` |
| H8 | Tableau PERT : en-tête `perturbation  k(trk ln)  std. dev.` puis une ligne `<n> <dk> <sigma>` par perturbation (signe, notation, colonnes supplémentaires éventuelles) | `ok_pert` |
| H9 | MCTAL : blocs `tally n`, `vals` (couples moyenne / erreur relative, 4 par ligne), `tfc` ; dernier couple = bin total | `ok_tally_kcode`, `ok_fixed_source` |
| H10 | `outp` déjà présent : MCNP écrit `outq` sans écraser (justifie le `rm -f outp mctal` du plugin) | `var_existing_outp` |
| H11 | Bibliothèque `.00c` disponible ; écart de keff avec les ZAID sans suffixe (première table de xsdir) | `ok_lib_00c` vs `ok_baseline` |
| H13 | Version lisible dans l'en-tête de `outp` (`Code Name & Version = MCNP6, ...`) : candidate pour un `code_id` de cache fz | `ok_baseline` |
| H15 | Arrêt par `CTME` avec `kct = 0` : texte de la bannière de fin (reconnu comme fin normale ?) | `ok_ctme` |
| H16 | Nombre à 16 chiffres (sortie brute d'une formule fz) accepté | `var_long_number` |
| H17 | `kct <= ikz` : erreur fatale ou fin sans keff | `err_kct_le_ikz` |
| H18 | `DATAPATH` invalide : message (`data file xsdir... does not exist`) dans `outp` ou seulement sur la sortie standard ; `outp` produit ou non | `env_bad_datapath` |
| H19 | Ligne de plus de 128 colonnes : `bad trouble ... input file data beyond column 128` | `err_line_128` |
| H20 | Point `KSRC` dans une cellule non fissile d'importance non nulle : non rejeté (skill v0.2), fin normale ; keff final récupéré ou biaisé par rapport à la référence | `var_ksrc_nonfissile`, `var_ksrc_fuel` |
| H21 | ZAID inexistant (Z et A inversés, `24028.00c`, skill v0.2) : `cross-section tables missing` + `bad trouble in subroutine rhoden` ; ordre des deux messages dans `outp` | `err_zaid_z_a` |

La première ligne de commentaire de chaque cas (`c Hypothese` / `c Attendu`) rappelle l'objet du test.
Un résultat contraire à « Attendu » est une information, pas un échec : il corrige l'hypothèse.

## Apports de la notice synthétique MCNP v0.2

- Inchangé par rapport à la version utilisée pour écrire le plugin : formats de sortie (bannière de fin,
  ligne keff, tableau PERT, MCTAL, `outp` → `outq`), messages `fatal error` / `bad trouble` déjà repris.
- Nouveau, sans effet sur l'extraction mais sur l'interprétation des résultats : une fin normale avec un
  keff et un σ plausibles **ne prouve pas** que la source a convergé. Unités faiblement couplées avec `KSRC`
  dans une seule unité : k = 0,928 au lieu de 0,993 (vérifié MCNP 6.3 selon la notice), contrôle d'entropie
  « passed ». Un point `KSRC` dans une cellule non fissile n'est pas rejeté (H20). Le plugin ne détecte pas
  ces cas : `mcnp_status` reste `NORMAL END`.
- Nouveau : ZAID inexistant → `bad trouble in subroutine rhoden` (H21) ; `this cell has no surfaces` imprimé
  **avant** l'écho de la carte fautive (sans effet : le statut reprend le texte du message, pas sa position) ;
  `lost particle in newcel - zero lattice element hit` (réseaux) ; tableau des isotopes : `82000` n'a pas de
  table neutron `.00c`/`.80c`, d'où `82000.84p` (photons) dans `ok_fixed_source`.

## Non couvert

- Exécution MPI (`mcnp6.mpi`, `mpirun`) : à décrire par l'utilisateur si elle est utilisée ;
  le plugin ne lance que `mcnp6` (threads via `MCNP_TASKS`).
- Reprise (`mcnp6 c i=... r=...`) et `FMESH`/`meshtal` : non extraits par le plugin.
- Sorties de MCNP 6.2 : formats supposés identiques à 6.1/6.3.
