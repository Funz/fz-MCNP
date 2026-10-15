# Reference MCNP outputs

| Directory | Origin | Content |
|---|---|---|
| `mcnp6.1/ok_godiva/` | real run, MCNP 6.1 (2018), test case of the Java `Funz/plugin-MCNP` | `godiva` (input, r = 8.778 cm, 1010 cycles), `outp` (XSDIR path anonymized), `out.txt` (terminal output) |
| `synthetic/err_*`, `synthetic/ok_*`, `synthetic/trap_echo` | hand-written | minimal `outp`/`mctal` files built from the MCNP 6.3 messages quoted in the MCNP synthetic notice (skill v0.1 and v0.2, same messages: `error-MCNP.md`, `output-MCNP.md`) and from the MCTAL layout described there |

The synthetic files are **not** MCNP outputs: they only carry the lines the plugin parses.
Replace each of them by the corresponding real output of `tests/mcnp_probe` (same case name)
once the probe has been run, and adjust `tests/test_outputs.py` if the real format differs.
