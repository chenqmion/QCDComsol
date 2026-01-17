import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import scipy.constants as con

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import mph

#%%
phi0 = con.value('mag. flux quantum')/(2*con.pi)

r_cavity = 4.5e-3
h_cavity = 50e-3

r_stub = 1.5e-3
h_stub = 15e-3

r_pin = 0.4e-3
r_bulk = 0.91e-3

z_tube = np.copy(h_stub) - 1.5e-3
r_tube = 2.5e-3
# l_tube = r_cavity + 25e-3

z_cavity_drive = 25e-3
l_cavity_drive_1 = 1e-3
l_cavity_drive_2 = 2e-3

x_qubit_drive = r_cavity + 4e-3
l_qubit_drive_1 = 3e-3
l_qubit_drive_2 = 2e-3

x_output = x_qubit_drive + 10e-3
l_output_1 = 2e-3
l_output_2 = 2e-3

#%% chip
x_chip = r_cavity - 2.5e-3 # fixed !
# l_chip = (r_cavity - x_chip) + (l_tube - r_cavity) + 1e-3
w_chip = 7e-3
h_chip = 675e-6

l_chip = 26.5e-3
l_tube = (l_chip - 1e-3) - (r_cavity - x_chip) + r_cavity
l_tube_2 = l_tube - 10e-3

x_bulb_1 = x_chip + 0.5e-3
w_bulb_1 = 200e-6
h_bulb_1 = 530e-6

x_bulb_2 = x_qubit_drive - 600e-6
w_bulb_2 = 50e-6
h_bulb_2 = 200e-6

w_cap_1 = 250e-6
h_cap_1 = 200e-6
w_cap_2 = 50e-6
h_cap_2 = 200e-6

w_junction = 300e-6
h_junction = 50e-6
L_junction = 5.2e-9

w_link_1 = 50e-6
h_link_1 = 200e-6

w_link_2 = (x_bulb_2-x_bulb_1) - (w_bulb_1+w_link_1+w_cap_1+w_junction+w_cap_2)
h_link_2 = 100e-6

x_resonator = x_qubit_drive + 1000e-6
l_resonator = 7400e-6
w_resonator = 200e-6

#%%
client = mph.start()
pymodel = client.create('Model')
model = pymodel.java

model.modelNode().create("comp1")
model.component("comp1").geom().create("geom1", 3)

#%% geometry
model.geom("geom1").feature().create("cyl_cavity", "Cylinder")
model.geom("geom1").feature("cyl_cavity").set('r', r_cavity)
model.geom("geom1").feature("cyl_cavity").set('h', h_cavity)

model.geom("geom1").feature().create("cyl_stub", "Cylinder")
model.geom("geom1").feature("cyl_stub").set('r', r_stub)
model.geom("geom1").feature("cyl_stub").set('h', h_stub)

# cavity drive
model.geom("geom1").feature().create("cyl_cavity_drive1", "Cylinder")
model.geom("geom1").feature("cyl_cavity_drive1").set('axistype', 'x')
model.geom("geom1").feature("cyl_cavity_drive1").set("pos", [-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])
model.geom("geom1").feature("cyl_cavity_drive1").set('r', r_bulk)
model.geom("geom1").feature("cyl_cavity_drive1").set('h', (l_cavity_drive_1+r_cavity))

model.geom("geom1").feature().create("cyl_cavity_drive2", "Cylinder")
model.geom("geom1").feature("cyl_cavity_drive2").set('axistype', 'x')
model.geom("geom1").feature("cyl_cavity_drive2").set("pos", [-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])
model.geom("geom1").feature("cyl_cavity_drive2").set('r', r_pin)
model.geom("geom1").feature("cyl_cavity_drive2").set('h', l_cavity_drive_2)

# chip tube
model.geom("geom1").feature().create("cyl_tube", "Block")
model.geom("geom1").feature("cyl_tube").set('axistype', 'x')
model.geom("geom1").feature("cyl_tube").set("pos", [0, -r_tube, z_tube + r_tube])
model.geom("geom1").feature("cyl_tube").set('size', [2*r_tube, 2*r_tube, l_tube])

model.geom("geom1").feature().create("cyl_tube2", "Block")
model.geom("geom1").feature("cyl_tube2").set('axistype', 'x')
model.geom("geom1").feature("cyl_tube2").set("pos", [0, -(h_chip+0.5e-3)/2, z_tube+(w_chip+0.5e-3)/2])
model.geom("geom1").feature("cyl_tube2").set('size', [(w_chip+0.5e-3), (h_chip+0.5e-3), l_tube_2])

# chip
model.geom("geom1").feature().create("blk_chip", "Block")
model.geom("geom1").feature("blk_chip").set("pos", [x_chip, -h_chip/2, z_tube-w_chip/2])
model.geom("geom1").feature("blk_chip").set("size", [l_chip, h_chip, w_chip])

model.geom("geom1").feature().create("wp2", "WorkPlane")
model.geom("geom1").feature("wp2").set("unite", True)
model.geom("geom1").feature("wp2").set("quickplane", "zx")
model.geom("geom1").feature("wp2").set("quicky", h_chip/2)

## qubit
model.geom("geom1").feature("wp2").geom().create("c_bulb_1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("c_bulb_1").set("size", [h_bulb_1, w_bulb_1])
model.geom("geom1").feature("wp2").geom().feature("c_bulb_1").set("pos", [z_tube-h_bulb_1/2, x_bulb_1])

model.geom("geom1").feature("wp2").geom().create("w_bulb_1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("w_bulb_1").set("size", [h_link_1, w_link_1])
model.geom("geom1").feature("wp2").geom().feature("w_bulb_1").set("pos", [z_tube-h_link_1/2, x_bulb_1+w_bulb_1])

model.geom("geom1").feature("wp2").geom().create("r_cap1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_cap1").set("size", [h_cap_1, w_cap_1])
model.geom("geom1").feature("wp2").geom().feature("r_cap1").set("pos", [z_tube-h_cap_1/2, x_bulb_1+w_bulb_1+w_link_1])

model.geom("geom1").feature("wp2").geom().create("r_junction", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_junction").set("size", [h_junction, w_junction])
model.geom("geom1").feature("wp2").geom().feature("r_junction").set("pos", [z_tube-h_junction/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1])

model.geom("geom1").feature("wp2").geom().create("r_cap2", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_cap2").set("size", [h_cap_2, w_cap_2])
model.geom("geom1").feature("wp2").geom().feature("r_cap2").set("pos", [z_tube-h_cap_2/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1+w_junction])

model.geom("geom1").feature("wp2").geom().create("r_bulb_2", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r_bulb_2").set("size", [h_bulb_2, w_link_2])
model.geom("geom1").feature("wp2").geom().feature("r_bulb_2").set("pos", [z_tube-h_bulb_2/2, x_bulb_2-w_link_2])

# model.geom("geom1").feature("wp2").geom().create("c_bulb_2", "Circle")
# model.geom("geom1").feature("wp2").geom().feature("c_bulb_2").set("r", r_bulb_2)
# model.geom("geom1").feature("wp2").geom().feature("c_bulb_2").set("pos", [x_bulb_2, 0])

model.geom("geom1").feature("wp2").geom().create("uni1", "Union")
model.geom("geom1").feature("wp2").geom().feature("uni1").selection("input").set("c_bulb_1", "w_bulb_1", "r_cap1")
model.geom("geom1").feature("wp2").geom().feature("uni1").set("intbnd", False)

model.geom("geom1").feature("wp2").geom().create("uni2", "Union")
model.geom("geom1").feature("wp2").geom().feature("uni2").selection("input").set("r_bulb_2", "r_cap2")
model.geom("geom1").feature("wp2").geom().feature("uni2").set("intbnd", False)

## resonator
model.geom("geom1").feature("wp2").geom().create("r1", "Rectangle")
model.geom("geom1").feature("wp2").geom().feature("r1").set("size", [w_resonator, l_resonator])
model.geom("geom1").feature("wp2").geom().feature("r1").set("pos", [z_tube-w_resonator/2, x_resonator])

# qubit drive
model.geom("geom1").feature().create("cyl_qubit_drive1", "Cylinder")
model.geom("geom1").feature("cyl_qubit_drive1").set('axistype', 'y')
model.geom("geom1").feature("cyl_qubit_drive1").set("pos", [x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])
model.geom("geom1").feature("cyl_qubit_drive1").set('r', r_bulk)
model.geom("geom1").feature("cyl_qubit_drive1").set('h', l_qubit_drive_1)

model.geom("geom1").feature().create("cyl_qubit_drive2", "Cylinder")
model.geom("geom1").feature("cyl_qubit_drive2").set('axistype', 'y')
model.geom("geom1").feature("cyl_qubit_drive2").set("pos", [x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])
model.geom("geom1").feature("cyl_qubit_drive2").set('r', r_pin)
model.geom("geom1").feature("cyl_qubit_drive2").set('h', l_qubit_drive_2)

# output
model.geom("geom1").feature().create("cyl_output1", "Cylinder")
model.geom("geom1").feature("cyl_output1").set('axistype', 'y')
model.geom("geom1").feature("cyl_output1").set("pos", [x_output, -(r_tube+l_output_1), z_tube])
model.geom("geom1").feature("cyl_output1").set('r', r_bulk)
model.geom("geom1").feature("cyl_output1").set('h', l_output_1)

model.geom("geom1").feature().create("cyl_output2", "Cylinder")
model.geom("geom1").feature("cyl_output2").set('axistype', 'y')
model.geom("geom1").feature("cyl_output2").set("pos", [x_output, -(r_tube+l_output_1), z_tube])
model.geom("geom1").feature("cyl_output2").set('r', r_pin)
model.geom("geom1").feature("cyl_output2").set('h', l_output_2)

# combine
model.geom("geom1").feature().create("diff1", "Difference")
model.geom("geom1").feature("diff1").selection("input").set("cyl_cavity", "cyl_tube", "cyl_tube2", "cyl_cavity_drive1", "cyl_qubit_drive1", "cyl_output1")
model.geom("geom1").feature("diff1").selection("input2").set("cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2")
model.geom("geom1").feature("diff1").set("keepsubtract", True)
model.geom("geom1").feature("diff1").set("intbnd", False)

model.geom("geom1").run("fin")

#%% material
model.component("comp1").material().create("mat1", "Common")
model.material("mat1").propertyGroup("def").set("relpermittivity", "1")
model.material("mat1").propertyGroup("def").set("relpermeability", "1")
model.material("mat1").propertyGroup("def").set("electricconductivity", "0")

model.component("comp1").material().create("mat2", "Common")
model.material("mat2").propertyGroup("def").set("relpermittivity", "11.7")
model.material("mat2").propertyGroup("def").set("relpermeability", "1")
model.material("mat2").propertyGroup("def").set("electricconductivity", "1e-12")
model.material("mat2").selection().set(4, 6)

pymodel.save('model_5')

#%% physics
model.component("comp1").physics().create("emw", "ElectromagneticWaves", "geom1")
model.physics("emw").create("pec2", "DomainPerfectElectricConductor", 3)
model.physics("emw").feature("pec2").selection().set(2, 3, 5, 7)

model.physics("emw").create("pec3", "PerfectElectricConductor", 2)
model.physics("emw").feature("pec3").selection().set(29, 31, 55)
# model.physics("emw").feature("pec3").selection().set(29, 31, 65)

model.param().set("LJ1", str(L_junction))
model.physics("emw").create("lelement1", "LumpedElement", 2)
model.physics("emw").feature("lelement1").set("LumpedElementType", "Inductor")
model.physics("emw").feature("lelement1").set("Lelement", "LJ1")
model.physics("emw").feature("lelement1").selection().set(30)

# model.physics("emw").create("sctr1", "Scattering", 2)
# model.physics("emw").feature("sctr1").selection().set(15)

model.physics("emw").create("lport1", "LumpedPort", 2)
model.physics("emw").feature("lport1").set("PortType", "Coaxial")
model.physics("emw").feature("lport1").set("PortExcitation", "off")
model.physics("emw").feature("lport1").selection().set(1)

model.physics("emw").create("lport2", "LumpedPort", 2)
model.physics("emw").feature("lport2").set("PortType", "Coaxial")
model.physics("emw").feature("lport2").set("PortExcitation", "off")
model.physics("emw").feature("lport2").selection().set(46)


model.physics("emw").create("lport3", "LumpedPort", 2)
model.physics("emw").feature("lport3").set("PortType", "Coaxial")
model.physics("emw").feature("lport3").set("PortExcitation", "off")
# model.physics("emw").feature("lport3").selection().set(58)
model.physics("emw").feature("lport3").selection().set(68)

pymodel.save('model_5')

#%% mesh
model.component("comp1").mesh().create("mesh1")
model.mesh("mesh1").autoMeshSize(2)
model.mesh("mesh1").run()

#%% study
model.study().create("std1")
model.study("std1").feature().create("eig", "Eigenfrequency")
model.study("std1").feature("eig").set('shift', "3[GHz]")
model.study("std1").feature("eig").set('neigs', "5")
model.study("std1").feature("eig").set('eigwhich', 'lr')

# # model.study("std1").run()
model.study("std1").createAutoSequences("all")
model.sol("sol1").runAll()

#%% plot
model.result().create("pg1", "PlotGroup3D")

model.result("pg1").feature().create("arwv1", "ArrowVolume")
model.result("pg1").feature("arwv1").set("data", "dset1")
model.result("pg1").feature("arwv1").set("solutionparams", "parent")
# model.result("pg1").feature("arwv1").set("evaluationsettings", "parent")
model.result("pg1").feature("arwv1").setIndex("expr", "emw.Ex", 0)
model.result("pg1").feature("arwv1").setIndex("expr", "emw.Ey", 1)
model.result("pg1").feature("arwv1").setIndex("expr", "emw.Ez", 2)
model.result("pg1").feature("arwv1").set("placement", "elements")
model.result("pg1").feature("arwv1").set("maxpointcount", '100000')
model.result("pg1").feature("arwv1").set("arrowlength", "logarithmic")
model.result("pg1").feature("arwv1").set("color", "blue")

model.result("pg1").feature().create("arwv2", "ArrowVolume")
model.result("pg1").feature("arwv2").set("data", "dset1")
model.result("pg1").feature("arwv2").set("solutionparams", "parent")
# model.result("pg1").feature("arwv2").set("evaluationsettings", "parent")
model.result("pg1").feature("arwv2").setIndex("expr", "emw.Hx", 0)
model.result("pg1").feature("arwv2").setIndex("expr", "emw.Hy", 1)
model.result("pg1").feature("arwv2").setIndex("expr", "emw.Hz", 2)
model.result("pg1").feature("arwv2").set("placement", "elements")
model.result("pg1").feature("arwv2").set("maxpointcount", '100000')
model.result("pg1").feature("arwv2").set("arrowlength", "logarithmic")
model.result("pg1").feature("arwv2").set("color", "red")

# model.result("pg1").feature().create("vol1", "Volume")
# model.result("pg1").feature("vol1").set("data", "dset1")
# model.result("pg1").feature("vol1").set("solutionparams", "parent")

# model.result().dataset().create("cpl1", "CutPlane")
# model.result().dataset("cpl1").set("quickplane", "xz")
#
# model.result("pg1").feature().create("surf1", "Surface")
# model.result("pg1").feature("surf1").set("data", "cpl1")
# model.result("pg1").feature("surf1").set("solutionparams", "parent")

# model.result("pg1").run()

#%%
pymodel.save('model_5')

# #%% data
# freqs = pymodel.evaluate('emw.freq', dataset="Study 1//Solution 1")
# Qs = pymodel.evaluate('emw.Qfactor', dataset="Study 1//Solution 1")
#
# P_electric = pymodel.evaluate('emw.intWe', dataset="Study 1//Solution 1")
# P_magnetic = pymodel.evaluate('emw.intWm', dataset="Study 1//Solution 1")
#
# P_1 = pymodel.evaluate('emw.Pport_1', dataset="Study 1//Solution 1")
# P_2 = pymodel.evaluate('emw.Pport_2', dataset="Study 1//Solution 1")
# P_3 = pymodel.evaluate('emw.Pport_3', dataset="Study 1//Solution 1")
#
# kappa_1s = (-P_1)/(P_electric+P_magnetic)
# kappa_2s = (-P_2)/(P_electric+P_magnetic)
# kappa_3s = (-P_3)/(P_electric+P_magnetic)
# kappa_mat = np.array([kappa_1s, kappa_2s, kappa_3s])
#
# T_mat = np.array([1/kappa_1s, 1/kappa_2s, 1/kappa_3s])
#
# Q_1s = (2*np.pi*freqs)/kappa_1s
# Q_2s = (2*np.pi*freqs)/kappa_2s
# Q_3s = (2*np.pi*freqs)/kappa_3s
#
# print(freqs)
# print(Qs)
# # print(1/(1/Q_1s + 1/Q_2s + 1/Q_3s))
# print(kappa_mat)
#
# plt.figure()
# plt.pcolormesh(np.log10(T_mat))
# plt.show()

#%%
exec(open('epr_analysis.py').read())