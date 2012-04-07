(**** start.gcode for The Replicator, single head ****)
M73 P0 (enable build progress)
G21 (set units to mm)
G90 (set positioning to absolute)
(**** begin homing ****)
G162 X Y F2500 (home XY axes maximum
G161 Z F1100 (home Z axis minimum)
G92 Z-5 (set Z to -5)
G1 Z0.0 (move Z to "0")
G161 Z F100 (home Z axis minimum)
M132 X Y Z A B (Recall stored home offsets for XYZAB axis)
(**** end homing ****)
G1 X112 Y-73 Z150 F3300.0 (move to waiting position)
G130 X0 Y0 A0 B0 (Lower stepper Vrefs while heating)
M109 S<setting.chamber.bedTemperature> T0 (set HBP temperature)
M6 T0 (wait for toolhead, and HBP to reach temperature)
M104 S<setting.temperature.baseTemperature> T0 (set extruder temperature)
M6 T0 (wait for toolhead, and HBP to reach temperature)
G130 X120 Y120 A127 B127 (Set Stepper motor Vref to defaults)
M108 R3.0 T0
G0 X112 Y-73 (Position Nozzle)
G0 Z0.6      (Position Height)
M108 R4.0    (Set Extruder Speed)
M101         (Start Extruder)
G4 P1500     (Create Anchor)
(**** end of start.gcode ****)
