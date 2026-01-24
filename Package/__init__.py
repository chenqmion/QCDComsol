from comsol_client import ComsolClient

from comsol_geometry import geometry_mixin
from comsol_material import material_mixin
from comsol_physics import physics_mixin
from comsol_mesh import mesh_mixin
from comsol_study import study_mixin
from comsol_result import result_mixin

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

# # comsol_root = r'C:\Programs\Comsol'
#
# # !export DYLD_LIBRARY_PATH=/Applications/COMSOL62/Multiphysics/bin/macarm64:$DYLD_LIBRARY_PATH
#
# import os
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

comsol_root=r'/Applications/COMSOL63/Multiphysics'

client = ComsolClient(comsol_root)
model = client.create_model("Model1")

model.param().set('l1', "1")

#%% geometry
geom = geometry_mixin(model)
geom.new_cylinder(name="cyl_cavity", r=r_cavity, l=h_cavity)
geom.new_cylinder(name="cyl_stub", r=r_stub, l=h_stub)

# chip tube
geom.new_block(name="blk_tube", w=2*r_tube, h=2*r_tube, l=l_tube, ax='x', pos=[0, 0, z_tube])
geom.new_block(name="blk_tube2", w=(w_chip+0.5e-3), h=(h_chip+0.5e-3), l=l_tube_2, ax='x', pos=[0, 0, z_tube])
geom.new_block(name="blk_chip", w=w_chip, h=h_chip, l=l_chip, ax='x', pos=[x_chip, 0, z_tube])

# cavity drive
geom.new_coaxport(name="cyl_cavity_drive", r1=r_bulk, r2=r_pin, l1=l_cavity_drive_1+r_cavity, l2=l_cavity_drive_2, ax='x', pos=[-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])

# qubit drive
geom.new_coaxport(name="cyl_qubit_drive", r1=r_bulk, r2=r_pin, l1=l_qubit_drive_1, l2=l_qubit_drive_2, ax='y', pos=[x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])

# output
geom.new_coaxport(name="cyl_output", r1=r_bulk, r2=r_pin, l1=l_qubit_drive_1, l2=l_qubit_drive_2, ax='y', pos=[x_output, -(r_tube+l_output_1), z_tube])

# combine
geom.difference(name="dif1",
                input1=["cyl_cavity", "blk_tube", "blk_tube2", "cyl_cavity_drive1", "cyl_qubit_drive1", "cyl_output1"],
                input2=["cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2"],
                keep_input1=False, keep_input2=True, keep_intb=False)

geom.finish()

#%% material
mat_air = material_mixin(model, 'Air')
# mat_air.new_param(tags="relpermeability", values=0.1)
mat_air.select("dif1")

mat_si = material_mixin(model, 'Si')
mat_si.select("blk_chip")

#%% physics
phys = physics_mixin(model,"emw", "ElectromagneticWaves")
phys.PEC_3D(["cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2"])
phys.port3D(1, "cyl_cavity_drive")
phys.port3D(2, "cyl_qubit_drive")
phys.port3D(3, "cyl_output")

#%% mesh
mesh = mesh_mixin(model,"mesh1")
mesh.auto('normal')
mesh.finish()

#%% study
std1 = study_mixin(model, "std1")
std1.solve_eigenfrequency(freq=3e9, num=5, mode='lr')
std1.param_sweep(var='l1', rang=[0,1])

#%% plot
pg1 = result_mixin(model, "pg1", "PlotGroup3D")
pg1.arrow_volume("arwv_E", obj='E')
pg1.arrow_volume("arwv_H", obj='H')

model.save()
model.show_tree()


# client.disconnect()

