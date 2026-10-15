Godiva probe - water-reflected sphere, KSRC in the reflector only
c Hypothese: H20 point KSRC dans une cellule non fissile d'importance non nulle (skill v0.2 : non rejete)
c Attendu: pas d'erreur; premiers cycles a k tres faible; keff final a comparer a var_ksrc_fuel
 1    1  -18.74  -1     imp:n=1   $ enriched uranium sphere (godiva)
 2    2  -1.0     1 -2  imp:n=1   $ water reflector 8.7407 - 20 cm
 3    0           2     imp:n=0   $ outside world

 1    so 8.7407
 2    so 20

 kcode 5000 1.0 20 70
 ksrc  15 0 0
 m1    92235 -93.71  92238 -5.27  92234 -1.02
 m2    1001 2  8016 1
