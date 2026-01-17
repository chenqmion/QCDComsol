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

comp = model.modelNode().create("comp1")
geom = comp.geom().create("geom1", 3)

#%% geometry
cyl_cavity = geom.feature().create("cyl_cavity", "Cylinder")
cyl_cavity.set('r', r_cavity)
cyl_cavity.set('h', h_cavity)

cyl_stub = geom.feature().create("cyl_stub", "Cylinder")
cyl_stub.set('r', r_stub)
cyl_stub.set('h', h_stub)

# cavity drive
cyl_cavity_drive1 = geom.feature().create("cyl_cavity_drive1", "Cylinder")
cyl_cavity_drive1.set('axistype', 'x')
cyl_cavity_drive1.set("pos", [-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])
cyl_cavity_drive1.set('r', r_bulk)
cyl_cavity_drive1.set('h', (l_cavity_drive_1+r_cavity))

geom.feature().create("cyl_cavity_drive2", "Cylinder")
geom.feature("cyl_cavity_drive2").set('axistype', 'x')
geom.feature("cyl_cavity_drive2").set("pos", [-(l_cavity_drive_1+r_cavity), 0, z_cavity_drive])
geom.feature("cyl_cavity_drive2").set('r', r_pin)
geom.feature("cyl_cavity_drive2").set('h', l_cavity_drive_2)

# chip tube
geom.feature().create("cyl_tube", "Block")
geom.feature("cyl_tube").set('axistype', 'x')
geom.feature("cyl_tube").set("pos", [0, -r_tube, z_tube + r_tube])
geom.feature("cyl_tube").set('size', [2*r_tube, 2*r_tube, l_tube])

geom.feature().create("cyl_tube2", "Block")
geom.feature("cyl_tube2").set('axistype', 'x')
geom.feature("cyl_tube2").set("pos", [0, -(h_chip+0.5e-3)/2, z_tube+(w_chip+0.5e-3)/2])
geom.feature("cyl_tube2").set('size', [(w_chip+0.5e-3), (h_chip+0.5e-3), l_tube_2])

# chip
geom.feature().create("blk_chip", "Block")
geom.feature("blk_chip").set("pos", [x_chip, -h_chip/2, z_tube-w_chip/2])
geom.feature("blk_chip").set("size", [l_chip, h_chip, w_chip])

geom.feature().create("wp2", "WorkPlane")
geom.feature("wp2").set("unite", True)
geom.feature("wp2").set("quickplane", "zx")
geom.feature("wp2").set("quicky", h_chip/2)

## qubit
geom.feature("wp2").geom().create("c_bulb_1", "Rectangle")
geom.feature("wp2").geom().feature("c_bulb_1").set("size", [h_bulb_1, w_bulb_1])
geom.feature("wp2").geom().feature("c_bulb_1").set("pos", [z_tube-h_bulb_1/2, x_bulb_1])

geom.feature("wp2").geom().create("w_bulb_1", "Rectangle")
geom.feature("wp2").geom().feature("w_bulb_1").set("size", [h_link_1, w_link_1])
geom.feature("wp2").geom().feature("w_bulb_1").set("pos", [z_tube-h_link_1/2, x_bulb_1+w_bulb_1])

geom.feature("wp2").geom().create("r_cap1", "Rectangle")
geom.feature("wp2").geom().feature("r_cap1").set("size", [h_cap_1, w_cap_1])
geom.feature("wp2").geom().feature("r_cap1").set("pos", [z_tube-h_cap_1/2, x_bulb_1+w_bulb_1+w_link_1])

geom.feature("wp2").geom().create("r_junction", "Rectangle")
geom.feature("wp2").geom().feature("r_junction").set("size", [h_junction, w_junction])
geom.feature("wp2").geom().feature("r_junction").set("pos", [z_tube-h_junction/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1])

geom.feature("wp2").geom().create("r_cap2", "Rectangle")
geom.feature("wp2").geom().feature("r_cap2").set("size", [h_cap_2, w_cap_2])
geom.feature("wp2").geom().feature("r_cap2").set("pos", [z_tube-h_cap_2/2, x_bulb_1+w_bulb_1+w_link_1+w_cap_1+w_junction])

geom.feature("wp2").geom().create("r_bulb_2", "Rectangle")
geom.feature("wp2").geom().feature("r_bulb_2").set("size", [h_bulb_2, w_link_2])
geom.feature("wp2").geom().feature("r_bulb_2").set("pos", [z_tube-h_bulb_2/2, x_bulb_2-w_link_2])

# geom.feature("wp2").geom().create("c_bulb_2", "Circle")
# geom.feature("wp2").geom().feature("c_bulb_2").set("r", r_bulb_2)
# geom.feature("wp2").geom().feature("c_bulb_2").set("pos", [x_bulb_2, 0])

geom.feature("wp2").geom().create("uni1", "Union")
geom.feature("wp2").geom().feature("uni1").selection("input").set("c_bulb_1", "w_bulb_1", "r_cap1")
geom.feature("wp2").geom().feature("uni1").set("intbnd", False)

geom.feature("wp2").geom().create("uni2", "Union")
geom.feature("wp2").geom().feature("uni2").selection("input").set("r_bulb_2", "r_cap2")
geom.feature("wp2").geom().feature("uni2").set("intbnd", False)

## resonator
geom.feature("wp2").geom().create("r1", "Rectangle")
geom.feature("wp2").geom().feature("r1").set("size", [w_resonator, l_resonator])
geom.feature("wp2").geom().feature("r1").set("pos", [z_tube-w_resonator/2, x_resonator])

# qubit drive
geom.feature().create("cyl_qubit_drive1", "Cylinder")
geom.feature("cyl_qubit_drive1").set('axistype', 'y')
geom.feature("cyl_qubit_drive1").set("pos", [x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])
geom.feature("cyl_qubit_drive1").set('r', r_bulk)
geom.feature("cyl_qubit_drive1").set('h', l_qubit_drive_1)

geom.feature().create("cyl_qubit_drive2", "Cylinder")
geom.feature("cyl_qubit_drive2").set('axistype', 'y')
geom.feature("cyl_qubit_drive2").set("pos", [x_qubit_drive, -(r_tube+l_qubit_drive_1), z_tube])
geom.feature("cyl_qubit_drive2").set('r', r_pin)
geom.feature("cyl_qubit_drive2").set('h', l_qubit_drive_2)

# output
geom.feature().create("cyl_output1", "Cylinder")
geom.feature("cyl_output1").set('axistype', 'y')
geom.feature("cyl_output1").set("pos", [x_output, -(r_tube+l_output_1), z_tube])
geom.feature("cyl_output1").set('r', r_bulk)
geom.feature("cyl_output1").set('h', l_output_1)

geom.feature().create("cyl_output2", "Cylinder")
geom.feature("cyl_output2").set('axistype', 'y')
geom.feature("cyl_output2").set("pos", [x_output, -(r_tube+l_output_1), z_tube])
geom.feature("cyl_output2").set('r', r_pin)
geom.feature("cyl_output2").set('h', l_output_2)

# combine
geom.feature().create("diff1", "Difference")
geom.feature("diff1").selection("input").set("cyl_cavity", "cyl_tube", "cyl_tube2", "cyl_cavity_drive1", "cyl_qubit_drive1", "cyl_output1")
geom.feature("diff1").selection("input2").set("cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2")
geom.feature("diff1").set("keepsubtract", True)
geom.feature("diff1").set("intbnd", False)

geom.run("fin")

# comp = model.modelNode().create("comp1")
#
# # 添加几何
# geom = comp.geom().create("geom1", 3)
#
# # 添加一个方块
# blk = geom.feature().create("blk1", "Block")
#
# # 重点测试：自动数组转换 (Python List -> Java Array)
# # 原生 JPype 这里必须写复杂的 JArray 代码，现在直接写 list
# blk.set("size", ["0.5", "1.2", "3.0"])
# blk.set("pos", ["0", "0", "0"])
#
# # 运行几何构建
# geom.run()
#
# # 5. 保存
model.save()
# client.disconnect()

