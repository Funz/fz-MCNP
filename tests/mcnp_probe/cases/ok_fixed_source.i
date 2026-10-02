Co-60 point source inside a 5 cm lead spherical shell
c Hypothese: H3/H9 source fixe: banniere de fin, tallies F2/F4 dans outp et mctal
c Attendu: 'run terminated when ... particle histories were done'; mctal tally 2 (7 bins e) et 4
 1   0          -1        imp:p=1      $ inner void
 2   1  -11.35   1 -2     imp:p=1      $ lead shell 10-15 cm
 3   0           2 -3     imp:p=1      $ void around the shell
 4   0           3        imp:p=0      $ outside world

 1   so   10
 2   so   15
 3   so   100

 mode  p
 m1    82000 1
 sdef  pos=0 0 0  par=p  erg=d1
 si1   L  1.1732  1.3325
 sp1      1       1
 f2:p  2
 fc2   Photon flux leaving the shield
 e2    0.1 0.2 0.5 1.0 1.2 1.4
 f4:p  2
 prdmp j j 1
 nps   200000
