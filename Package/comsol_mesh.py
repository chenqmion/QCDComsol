class mesh_mixin:
    def __init__(self, model, name="mesh1"):
        comp = model.modelNode("comp1")
        try:
            comp.mesh().remove(name)
        except:
            pass

        mesh = comp.mesh().create(name)

        self._comp = comp
        self._mesh = mesh
        self._name = name

    def auto(self, key):
        levels = {
            'extremely fine': 1,
            'extra fine': 2,
            'finer': 3,
            'fine': 4,
            'normal': 5,
            'coarse': 6,
            'coarser': 7,
            'extra coarse': 8,
            'extremely coarse': 9
        }

        self._mesh.autoMeshSize(levels[key])

    def finish(self):
        self._mesh.run()