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

# ## qubit
# geom.feature("wp2").geom().create("c_bulb_1", "Rectangle")
# geom.feature("wp2").geom().feature("c_bulb_1").set("size", [h_bulb_1, w_bulb_1])
# geom.feature("wp2").geom().feature("c_bulb_1").set("pos", [z_tube-h_bulb_1/2, x_bulb_1])
#
# geom.feature("wp2").geom().create("w_bulb_1", "Rectangle")
# geom.feature("wp2").geom().feature("w_bulb_1").set("size", [h_link_1, w_link_1])
# geom.feature("wp2").geom().feature("w_bulb_1").set("pos", [z_tube-h_link_1/2, x_bulb_1+w_bulb_1])
#
# geom.feature("wp2").geom().create("r_cap1", "Rectangle")
# geom.feature("wp2").geom().feature("r_cap1").set("size", [h_cap_1, w_cap_1])
# geom.feature("wp2").geom().feature("r_cap1").set("pos", [z_tube-h_cap_1/2, x_bulb_1+w_bulb_1+w_link_1])
#
# geom.feature("wp2").geom().create("r_junction", "Rectangle")
# geom.feature("wp2").geom().feature("r_junction").set("size", [h_junction, w_junction])
# geom.feature("wp2").geom().feature("r_junction").set("pos", [z_tube-h_junction/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1])
#
# geom.feature("wp2").geom().create("r_cap2", "Rectangle")
# geom.feature("wp2").geom().feature("r_cap2").set("size", [h_cap_2, w_cap_2])
# geom.feature("wp2").geom().feature("r_cap2").set("pos", [z_tube-h_cap_2/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1+w_junction])
#
# geom.feature("wp2").geom().create("r_bulb_2", "Rectangle")
# geom.feature("wp2").geom().feature("r_bulb_2").set("size", [h_bulb_2, w_link_2])
# geom.feature("wp2").geom().feature("r_bulb_2").set("pos", [z_tube-h_bulb_2/2, x_bulb_2-w_link_2])
#
# # geom.feature("wp2").geom().create("c_bulb_2", "Circle")
# # geom.feature("wp2").geom().feature("c_bulb_2").set("r", r_bulb_2)
# # geom.feature("wp2").geom().feature("c_bulb_2").set("pos", [x_bulb_2, 0])
#
# geom.feature("wp2").geom().create("uni1", "Union")
# geom.feature("wp2").geom().feature("uni1").selection("input").set("c_bulb_1", "w_bulb_1", "r_cap1")
# geom.feature("wp2").geom().feature("uni1").set("intbnd", False)
#
# geom.feature("wp2").geom().create("uni2", "Union")
# geom.feature("wp2").geom().feature("uni2").selection("input").set("r_bulb_2", "r_cap2")
# geom.feature("wp2").geom().feature("uni2").set("intbnd", False)
#
# ## resonator
# geom.feature("wp2").geom().create("r1", "Rectangle")
# geom.feature("wp2").geom().feature("r1").set("size", [w_resonator, l_resonator])
# geom.feature("wp2").geom().feature("r1").set("pos", [z_tube-w_resonator/2, x_resonator])
#

# geom.run("fin")
model.save()
model.show_tree()


# # 5. 保存
model.save()
# client.disconnect()

