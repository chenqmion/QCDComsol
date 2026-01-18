class geometry_mixin:
    def create_geometry(self):
        comp = self.modelNode("comp1")
        return comp.geom().create("geom1", 3)

    def new_cylinder(self, *, name, r, l, ax='z', pos=[0,0,0], mid_plane=False):
        _cyl = self.feature().create(name, "Cylinder")
        _cyl.label(name)
        _cyl.set("selresult", True)

        # model.component("comp1").geom("geom1").feature("dif2").set("selresultshow", "bnd");

        _cyl.set('r', r)
        _cyl.set('h', l)
        _cyl.set('axistype', ax)

        if not(mid_plane):
            _cyl.set("pos", pos)
        else:
            idx_l = 'xyz'.find(ax)
            pos[idx_l] += -l/2
            _cyl.set("pos", pos)

        self.run(name)

    def new_block(self, *, name, w, h, l, ax='z', pos=[0, 0, 0], mid_plane=False):
        _blk = self.feature().create(name, "Block")
        _blk.label(name)
        _blk.set("selresult", True)

        _blk.set('size', [w, h, l])
        _blk.set('axistype', ax)

        _blk.set("base", "center")
        if mid_plane:
            _blk.set("pos", pos)
        else:
            idx_l = 'xyz'.find(ax)
            pos[idx_l] += l/ 2
            _blk.set("pos", pos)

        self.run(name)

    #%% boolean
    def union(self, *, name, input, keep_input, keep_intb):
        _uni = self.feature().create(name, "Union")
        _uni.label(name)
        _uni.set("selresult", True)

        _uni.selection("input").set(input)

        _uni.set("keepadd", keep_input)
        _uni.set("intbnd", keep_intb)

        self.run(name)

    def difference(self, *, name, input1, input2, keep_input1, keep_input2, keep_intb):
        _dif = self.feature().create(name, "Difference")
        _dif.label(name)
        _dif.set("selresult", True)
        _dif.set("selresultshow", "dom")

        _dif.selection("input").set(input1)
        _dif.selection("input2").set(input2)

        _dif.set("keepadd", keep_input1)
        _dif.set("keepsubtract", keep_input2)
        _dif.set("intbnd", keep_intb)

        self.run(name)