# Sondes MCNP : consolidation des hypothèses du plugin

Jeux de données courts (Godiva, 5 000 à 10 000 neutrons/cycle ; une source fixe photons)
destinés à être lancés avec un MCNP réel. Les sorties servent à :

- trancher les hypothèses sur lesquelles reposent `MCNP.sh` et l'extraction des sorties de `MCNP.json` ;
- confirmer les affirmations de la notice synthétique MCNP (skill v0.2 : `input-MCNP.md`, `output-MCNP.md`,
  `error-MCNP.md` ; messages annoncés comme reproduits avec MCNP 6.3.0, sans sortie jointe) ;
- remplacer les fichiers de référence synthétiques par des sorties réelles (fait : `tests/fixtures/mcnp6.3/`).

## Lancement

```bash
cd tests/mcnp_probe
MCNP_CMD=/chemin/vers/mcnp6 DATAPATH=/chemin/vers/MCNP_DATA ./run_probe.sh
# MCNP_CMD   : défaut mcnp6 dans le PATH, sinon $MCNP_PATH/MCNP_CODE/bin/mcnp6 ou $MCNP_PATH/bin/mcnp6
# DATAPATH   : répertoire contenant xsdir (défaut : $MCNP_PATH/MCNP_DATA s'il existe)
# MCNP_TASKS : nombre de threads (option "tasks N"), ex. MCNP_TASKS=4
# MCNP_OPTS  : options supplémentaires de la ligne de commande (ex. xsdir=xsdir71)
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

## Acquis antérieurs (sans exécution de MCNP 6.3)

- Sortie réelle MCNP 6.1 (cas Godiva du plugin Java `plugin-MCNP`, 2018) : ligne keff
  `| the final estimated combined collision/absorption/track-length keff = 1.00248 with an estimated
  standard deviation of 0.00062 |`, bannière `run terminated when    1010 kcode cycles were done.`
  (deux occurrences), `mcrun  is done` sur la sortie standard seulement. Fichier de référence :
  `tests/fixtures/mcnp6.1/ok_godiva/`.
- Le plugin fz précédent ne pouvait pas fonctionner : `MCNP.sh` sortait en code 2 (« Usage ») quand
  fz lui passait un seul fichier d'entrée (cas normal), et l'extraction utilisait `match(s, re, arr)`,
  propre à gawk (erreur de syntaxe avec mawk, awk par défaut de Debian/Ubuntu, et avec l'awk BSD de macOS).

## Acquis (2026-10-15, MCNP 6.3.0)

Exécution : `mcnp6` 6.3.0 (binaire Linux LANL, `ld=01/26/23`, `release/6.3-55762725c4`), Debian 12,
`MCNP_TASKS=8`, gawk 5.2. Données : `xsdir` de site (pas celui de la distribution LANL),
`MCNP_OPTS="xsdir=xsdir71"` (ENDF/B-VII.1, suffixes `.02c`…`.18c`, aucune table photon)
pour les 20 cas ; `xsdir=xsdir80-mc61-irdff2` (ENDF/B-VIII.0 + `mcplib84`) pour les cas `ok_*`,
seul moyen de faire tourner `ok_fixed_source`. Sorties réelles retenues (chemins des données remplacés
par `/path/to/MCNP_DATA`) : `tests/fixtures/mcnp6.3/`. Une passe préalable sans `DATAPATH` a
aussi été faite (tous les cas s'arrêtent sur `ixsdir`, sauf erreurs de lecture d'entrée).

| Id | Résultat | Constat (texte exact) |
|---|---|---|
| H1 | confirmé | `outp`, `runtpe.h5` (pas de `runtpe`), `srctp` ; `mctal` seulement avec `PRDMP j j 1` (`ok_tally_kcode`, `ok_fixed_source`), absent de `ok_baseline`. `runtpe.h5` écrit même après des erreurs fatales (`err_hash_comment`, `ok_lib_00c`). |
| H2 | confirmé | `\| the final estimated combined collision/absorption/track-length keff = 0.997944 with an estimated standard deviation of 0.000575 \|` ; terminal : `final k(col/abs/trk len) = 0.997944     std dev = 0.000575`, puis `mcrun  is done`. |
| H3 | confirmé | kcode : `run terminated when     130 kcode cycles were done.` ; source fixe : `run terminated when      200000  particle histories were done.` (deux occurrences dans `outp`). |
| H4 | **établi : inutilisable** | code retour 0 pour les 20 cas, y compris erreurs fatales, bad trouble, particules perdues, `DATAPATH` invalide et absence d'`outp` (`err_line_128`). `MCNP.sh` continue de décider sur `outp`. |
| H5 | confirmé, notice infirmée sur le texte | `  fatal error.  no m card for material no. 1` (début de ligne, après la ligne d'entrée fautive). `#` en commentaire : `  fatal error.  symbol too long:  enriched` (×3) puis `  fatal error.  entries must be numerical.`, et non « is not a legal data symbol ». |
| H6 | **infirmé (format)** | `bad trouble in subroutine <s> of <m>` puis **une ligne vide**, puis la raison : `bad trouble in subroutine pass0 of imcn` / `` / `unexpected eof in file err_missing_blank.i`. Le plugin lisait la ligne vide : corrigé. Table absente (`92235.99c`) : `  fatal error.   cross-section tables missing for zaid = 92235.99c` (trois espaces), pas de bad trouble (ni `ixsdir` ni `rhoden`). `err_ksrc_outside` avec données : `fatal error.  the entire source was rejected.` puis `run terminated because of fatal errors.`, **sans** le `bad trouble in subroutine skcode` / `no source points in kcode` annoncé (présent seulement dans la passe sans données). |
| H7 | confirmé (1 thread) | `run terminated because  10 particles got lost.` + `  warning.  no final keff estimate made because no active cycles run.` Avec `tasks 8` : `17 particles got lost` (les threads dépassent la limite de 10). |
| H8 | confirmé | `          perturbation      k(trk ln)   std. dev.` puis `                   1          0.00802     0.00004` / `2  -0.00807  0.00004` (5 décimales fixes, signe `-` seul). σ(dk) = 4e-5 pour σ(k) = 1,1e-3 : échantillonnage corrélé, ordre de grandeur non critiqué ici. |
| H9 | confirmé | blocs `tally n`, `vals` (4 couples par ligne), `tfc`. F2 avec 6 bornes `e2` : `et       7` (bin total ajouté), dernier couple 3.55903E-05 0.0080 = somme des 6 bins = dernière valeur `tfc`. F4 sans bin : un seul couple. Règle du dernier couple fausse pour un tally à plusieurs cellules sans bin total (non testé, documenté). |
| H10 | confirmé | `outp already exists.  outq is created instead.` (stdout). |
| H11 | non tranché | aucune table `.00c` dans les `xsdir` du site (`fatal error.   cross-section tables missing for zaid = 92234.00c`). Sensibilité au `xsdir` sans suffixe : `92235.02c` (293,6 K) dans les deux cas, keff 0.997944 (ENDF/B-VII.1) contre 1.000082 (ENDF/B-VIII.0). |
| H13 | confirmé | ligne 1 d'`outp` : `          Code Name & Version = mcnp6, 6.3.0, production` (minuscules, contrairement à `MCNP6` supposé). |
| H15 | confirmé | `run terminated when it had used  0.3  minutes of computer time.` → `NORMAL END`, keff présent (0.999444 ± 0.000496). |
| H16 | confirmé | nombre à 16 chiffres accepté, fin normale, keff 1.003398. |
| H17 | **infirmé** | ni erreur fatale ni fin anormale : `run terminated when      40 kcode cycles were done.` + `  warning.  no final keff estimate made because no active cycles run.` Le plugin donnait `NORMAL END` : statut `NO KEFF: ...` ajouté, avertissement sur stderr dans `MCNP.sh` (code 0 conservé). |
| H18 | confirmé | `outp` produit ; `bad trouble in subroutine ixsdir of imcn` / `` / `data file xsdir71 does not exist.` (ou `xsdir_mcnp6.3` sans option `xsdir=`) dans `outp` et sur stdout ; sans `DATAPATH` : `warning.  DATAPATH environment var is not set` et `DATAPATH must be set by user` (stdout). |
| H19 | confirmé, **sans `outp`** | aucun `outp` ; terminal seulement : `bad trouble in subroutine exemes of mcnp` / `` / `input file data beyond column 128.` Via fz : `MCNP.sh` code 5, `mcnp_status` lu dans `out.txt` = `BAD TROUBLE: input file data beyond column 128. (subroutine exemes of mcnp)`. |
| H20 | **infirmé en partie** | point `KSRC` dans le réflecteur eau accepté, puis arrêt au cycle 2 : `bad trouble in subroutine colidk of mcrun` / `source particle no.         6400` / `the new source has overrun the old source.` → `run terminated because of bad trouble.` Référence (`var_ksrc_fuel`) : 1.205271 ± 0.001424. La raison suit `source particle no.` : extraction adaptée. |
| H21 | confirmé, avec réserve | `  fatal error.   cross-section tables missing for zaid = 24028.00c` puis `bad trouble in subroutine rhoden of imcn` / `` / `atomic weight of  24028 is zero.` ; l'erreur fatale précède et l'emporte dans le statut. Réserve : `.00c` absent du `xsdir`, donc la table manque aussi pour une autre raison. |

Bout en bout (`run_fz_e2e.py`, fz 1.1 et 1.2, `xsdir71`, `tasks 8`) : `examples/godiva.inp`, r = 8,5 / 8,7407 / 9,0 →
`done`, `NORMAL END`, keff = 0.976714 ± 0.000545 / 0.997944 ± 0.000575 / 1.022940 ± 0.000567.
`fz list --check` (fz 1.2) : modèle `MCNP` et calculateur `localhost_MCNP` `passed` ; `fzr --model MCNP`
sans `--calculators` fonctionne. Avec fz 1.1, `fz list --check` ne liste pas `localhost_MCNP`
(calculateur `sh://` en échec : « Empty sh:// command ») : utiliser fz ≥ 1.2.

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
