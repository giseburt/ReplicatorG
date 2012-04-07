(******* End.gcode*******)
M73 P100 (end  build progress )
G92 E3 (set E to 3, for rapid reversal)
G1 E0 F1800 (move E to 0, backward, at 30mm/s)
G0 Z155
M18
M109 S0 T0
M104 S0 T0
G162 X Y F2500
M18
M70 P5 ( We <3 Making Things!)
M72 P1  ( Play Ta-Da song )
(*********end End.gcode*******)
