from comsol_client import ComsolClient

#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import scipy.constants as con

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

comsol_root = r'C:\Programs\Comsol'

client = ComsolClient(comsol_root)
model = client.create_model("Model1")

#%% geometry
geom = model.create_geometry()
geom.new_cylinder(name="cyl_cavity", r=r_cavity, l=h_cavity)
geom.new_cylinder(name="cyl_stub", r=r_stub, l=h_stub)

# cavity drive
geom.new_cylinder(name="cyl_cavity_drive1", r=r_bulk, l=l_cavity_drive_1+r_cavity, ax='x', pos=[-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])
geom.new_cylinder(name="cyl_cavity_drive2", r=r_pin, l=l_cavity_drive_2, ax='x', pos=[-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])

# chip tube
geom.new_block(name="blk_tube", w=2*r_tube, h=2*r_tube, l=l_tube, ax='x', pos=[0, 0, z_tube])
geom.new_block(name="blk_tube2", w=(w_chip+0.5e-3), h=(h_chip+0.5e-3), l=l_tube_2, ax='x', pos=[0, 0, z_tube])
geom.new_block(name="blk_chip", w=w_chip, h=h_chip, l=l_chip, ax='x', pos=[x_chip, 0, z_tube])

# qubit drive
geom.new_cylinder(name="cyl_qubit_drive1", r=r_bulk, l=l_qubit_drive_1, ax='y', pos=[x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])
geom.new_cylinder(name="cyl_qubit_drive2", r=r_pin, l=l_qubit_drive_2, ax='y', pos=[x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])

# output
geom.new_cylinder(name="cyl_output1", r=r_bulk, l=l_qubit_drive_1, ax='y', pos=[x_output, -(r_tube+l_output_1), z_tube])
geom.new_cylinder(name="cyl_output2", r=r_pin, l=l_qubit_drive_2, ax='y', pos=[x_output, -(r_tube+l_output_1), z_tube])

# # combine
geom.difference(name="dif1",
                input1=["cyl_cavity", "blk_tube", "blk_tube2", "cyl_cavity_drive1", "cyl_qubit_drive1", "cyl_output1"],
                input2=["cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2"],
                keep_input1=False, keep_input2=True, keep_intb=False)

geom.run()

#%% material
mat_air = model.create_material('Air')
# mat_air.new_param(tags="relpermeability", values=0.1)
mat_air.select("dif1")

mat_si = model.create_material('Si')
mat_si.select("blk_chip")

#%% physics
phys = model.create_physics("emw", "ElectromagneticWaves")
phys.PEC_3D(["cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2"])

# phys.port3D(2, 'lport1')
# phys.port3D(3, 'lport1')

sel = model.comp1.selection().create('testt', "Box")
sel.set("condition", "intersects")
sel.set("entitydim", 2)

xx = -(l_cavity_drive_1+r_cavity)
yy = 0
zz = z_cavity_drive + (r_pin+r_bulk)/2

sel.set("xmin", xx-1e-6)
sel.set("xmax", xx+1e-6)
sel.set("ymin", yy-1e-6)
sel.set("ymax", yy+1e-6)
sel.set("zmin", zz-1e-6)
sel.set("zmax", zz+1e-6)

phys.port3D(1, 'testt')

# model.physics("emw").create("pec2", "DomainPerfectElectricConductor", 3)
# model.physics("emw").feature("pec2").selection().set(2, 3, 5, 7)
#
# model.param().set("LJ1", str(L_junction))
# model.physics("emw").create("lelement1", "LumpedElement", 2)
# model.physics("emw").feature("lelement1").set("LumpedElementType", "Inductor")
# model.physics("emw").feature("lelement1").set("Lelement", "LJ1")
# model.physics("emw").feature("lelement1").selection().set(30)
#
# # model.physics("emw").create("sctr1", "Scattering", 2)
# # model.physics("emw").feature("sctr1").selection().set(15)
#
# model.physics("emw").create("lport1", "LumpedPort", 2)
# model.physics("emw").feature("lport1").set("PortType", "Coaxial")
# model.physics("emw").feature("lport1").set("PortExcitation", "off")
# model.physics("emw").feature("lport1").selection().set(1)
#
# model.physics("emw").create("lport2", "LumpedPort", 2)
# model.physics("emw").feature("lport2").set("PortType", "Coaxial")
# model.physics("emw").feature("lport2").set("PortExcitation", "off")
# model.physics("emw").feature("lport2").selection().set(46)
#
#
# model.physics("emw").create("lport3", "LumpedPort", 2)
# model.physics("emw").feature("lport3").set("PortType", "Coaxial")
# model.physics("emw").feature("lport3").set("PortExcitation", "off")
# # model.physics("emw").feature("lport3").selection().set(58)
# model.physics("emw").feature("lport3").selection().set(68)
#
# pymodel.save('model_5')
#
# #%% mesh
# model.component("comp1").mesh().create("mesh1")
# model.mesh("mesh1").autoMeshSize(2)
# model.mesh("mesh1").run()

model.save()
model.show_tree()


# # 5. 保存
# model.save()
# client.disconnect()

