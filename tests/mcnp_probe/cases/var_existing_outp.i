Godiva probe - bare HEU sphere
c Hypothese: H10 outp deja present: MCNP ecrit-il outq ? (run_probe cree un outp avant le calcul)
c Attendu: nouvelle sortie dans outq, outp intact
 1    1  -18.74  -1  imp:n=1   $ enriched uranium sphere (godiva)
 2    0           1  imp:n=0   $ all space outside the sphere

 1    so 8.7407

 kcode 5000 1.0 20 70
 ksrc  0 0 0
 m1    92235 -93.71  92238 -5.27  92234 -1.02
