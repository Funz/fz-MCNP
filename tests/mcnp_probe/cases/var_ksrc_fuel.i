Godiva probe - water-reflected sphere, KSRC in the fuel
c Hypothese: H20 reference de var_ksrc_nonfissile (KSRC au centre du combustible)
c Attendu: fin normale; keff de reference
 1    1  -18.74  -1     imp:n=1   $ enriched uranium sphere (godiva)
 2    2  -1.0     1 -2  imp:n=1   $ water reflector 8.7407 - 20 cm
 3    0           2     imp:n=0   $ outside world

 1    so 8.7407
 2    so 20

 kcode 5000 1.0 20 70
 ksrc  0 0 0
 m1    92235 -93.71  92238 -5.27  92234 -1.02
 m2    1001 2  8016 1
