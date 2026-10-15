# Reference MCNP outputs

| Directory | Origin | Content |
|---|---|---|
| `mcnp6.1/ok_godiva/` | real run, MCNP 6.1 (2018), test case of the Java `Funz/plugin-MCNP` | `godiva` (input, r = 8.778 cm, 1010 cycles), `outp` (XSDIR path anonymized), `out.txt` (terminal output) |
| `mcnp6.3/<case>/` | real runs, MCNP 6.3.0 (2026-10-15), cases of `tests/mcnp_probe/cases` | input `<case>.i`, `outp`, `mctal` when written, `out.txt` (terminal output); data paths replaced by `/path/to/MCNP_DATA` |
| `synthetic/trap_echo/` | hand-written | error messages quoted in comments of the echoed input: must not be taken for errors |

`mcnp6.3` runs: `tasks 8`, site `xsdir` files (`xsdir71`, ENDF/B-VII.1, for all cases except
`ok_fixed_source`, run with an ENDF/B-VIII.0 + `mcplib84` `xsdir`). `err_line_128` has no `outp`
(MCNP stops before writing it). See `tests/mcnp_probe/README.md`, section "Acquis", for what
each case established.
