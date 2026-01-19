class result_mixin:
    def __init__(self, model, name="pg1", type="PlotGroup3D"):
        pg = model.result().create(name, type)

        self._model = model
        self._pg = pg
        self._std_name = name

    def arrow_volume(self, name, obj):
        _av = self._pg.create(name, "ArrowVolume")

        _av.set("data", "dset1")
        _av.set("solutionparams", "parent")
        _av.set("evaluationsettings", "parent")

        if obj == 'E':
            _av.setIndex("expr", "emw.Ex", 0)
            _av.setIndex("expr", "emw.Ey", 1)
            _av.setIndex("expr", "emw.Ez", 2)
            _av.set("color", "red")
        elif obj == 'H':
            _av.setIndex("expr", "emw.Hx", 0)
            _av.setIndex("expr", "emw.Hy", 1)
            _av.setIndex("expr", "emw.Hz", 2)
            _av.set("color", "blue")

        _av.set("placement", "elements")
        _av.set("maxpointcount", '100000')
        _av.set("arrowlength", "logarithmic")

        self._pg.run()