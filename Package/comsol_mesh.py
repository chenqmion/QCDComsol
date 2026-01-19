class mesh_mixin:
    def __init__(self, model, name):
        comp = model.modelNode("comp1")
        mesh = comp.mesh().create("mesh1")

        self._comp = comp
        self._mesh = mesh
        self._name = name

    def auto(self, key):
        levels = {'extremely_fine': 1, 'extra fine': 2, 'finer': 3,
                  'fine': 4, 'normal': 5, 'coarse': 6,
                  'coarser':7, 'extra_coarse': 8, 'extremely_coarse': 9}

        self._mesh.autoMeshSize(levels[key])

    def finish(self):
        self._mesh.run()