import numpy as np

class layout_mixin:
    def __init__(self, model, name, ax, value):
        comp = model.modelNode("comp1")
        geom = comp.geom("geom1")
        self._comp = comp
        self._geom = geom

        plane = self.new_plane(name=name, ax=ax, value=value)
        self._plane = plane.geom()

        self._current_feature = 'layout_0'

    def new_plane(self, *, name, ax='z', value=0 ):
        plane = self._geom.feature().create(name, "WorkPlane")

        plane.set("selplaneshow", True)

        plane.set("unite", True)
        if ax == 'x':
            plane.set("quickplane", "yz")
        elif ax == 'y':
            plane.set("quickplane", "zx")
        elif ax == 'z':
            plane.set("quickplane", "xy")

        plane.set("quicky", value)
        self._geom.run(name)
        return plane

    def import_gds(self, *, path):
        _gds = self._plane.create(self._current_feature, "Import")
        _gds.set("filename", path)
        _gds.set("updategeomunit", False)
        _gds.importData()

        bnd_gnd = self._comp.selection().create('gnd_bnd', "Intersection")
        bnd_gnd.set("entitydim", 2)
        bnd_gnd.set("input", ["geom1_wp_1_layout_0_LAYER0_bnd", "geom1_wp_1_layout_0_LAYER1_bnd"])

        bnd_jj = self._comp.selection().create('jj_bnd', "Union")
        bnd_jj.set("entitydim", 2)
        bnd_jj.set("input", ["geom1_wp_1_layout_0_LAYER3_bnd"])

    def rotate_gds(self, *, degree):
        new_feature = self._current_feature[:7] + str(int(self._current_feature[7:]) + 1)
        _rot = self._plane.create(new_feature, "Rotate")
        _rot.selection("input").set(self._current_feature)
        _rot.set("rot", degree)
        self._plane.run(new_feature)
        self._current_feature = new_feature

    def move_gds(self, *, pos=[0, 0]):
        new_feature = self._current_feature[:7] + str(int(self._current_feature[7:]) + 1)
        _mov = self._plane.create(new_feature, "Move")
        _mov.selection("input").set(self._current_feature)
        _mov.set("displx", pos[0])
        _mov.set("disply", pos[1])
        # _mov.set("newposx", pos[0])
        # _mov.set("newposy", pos[1])
        self._plane.run(new_feature)
        self._current_feature = new_feature


