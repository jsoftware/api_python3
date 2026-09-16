Broadcastly_z_ =: {{
'l r' =. }. u b. 0
cs =. ((-@<. #) {. ]) $
fr =. -@[ }. $@]
csx =. l cs x [ csy =. r cs y
fxy =. (l fr x) ,:!.1&|. r fr y
assert. (+./@:(=&1) *./@:+. =/) fxy
mxy =. (=/ +."1 ~:&1) fxy
ranks =. (+.&(2&(>/\))/@(1&,.) # |:@(-~ +/\"1)) mxy
ranks =. (l , r) -.~ ranks (] , +"1) csx ,&# csy
repr =. u`'' <F..('"' ,&< (,&< '0'&;)~) ranks
'fx fy' =. mxy <@|.@#"1 fxy
(x ($,)~ fx , csx) repr`:6 y ($,)~ fy , csy
}}
