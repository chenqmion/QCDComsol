# QCDComsol
This is the COMSOL Multiphysics engine for microwave simulation. It is an important part of [QCDesigner](https://github.com/chenqmion/QCDesigner) but can be used standalone.

## Start client and create model
```
client = ComsolClient(comsol_root)
model = client.create_model("Wavepool_1")
```
## Define geometry
```
geom = geometry_mixin(model)
geom.new_cylinder(name="cyl_cavity", r=r_cavity, l=h_cavity)
geom.new_cylinder(name="cyl_stub", r=r_stub, l=h_stub)
```
## Define material
```
mat_air = material_mixin(model, 'Air')
mat_air.select("dif1")
```
## Physics
```
phys = physics_mixin(model,"emw", "ElectromagneticWaves")
phys.PEC_3D(["cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2"])
```
## Mesh
```
mesh = mesh_mixin(model,"mesh1")
mesh.auto('normal')
mesh.finish()
```
## Study
```
std1 = study_mixin(model, "std1")
std1.solve_eigenfrequency(freq=3e9, num=5, mode='lr')
```
## Plot
```
pg1 = result_mixin(model, "pg1", "PlotGroup3D")
pg1.arrow_volume("arwv_E", obj='E')
pg1.arrow_volume("arwv_H", obj='H')
```
## EPR analysis
```
EPR_mixin(model)
```
## Acknowledgement
This project does not reference but is motivated by [PyInventor](https://github.com/AndrewOriani/PyInventor), [MPh](https://github.com/MPh-py/MPh) and [pyEPR](https://github.com/zlatko-minev/pyEPR). Check them out!

