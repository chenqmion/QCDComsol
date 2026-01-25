class result_mixin:
    def __init__(self, model, name="pg1", type="PlotGroup3D"):
        pg = model.result().create(name, type)

        self._model = model
        self._pg = pg
        self._std_name = name

    def arrow_volume(self, name, obj, mode='elements'):
        _av = self._pg.create(name, "ArrowVolume")

        _av.set("solutionparams", "parent")
        # _av.set("evaluationsettings", "parent")

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

        if (mode == 'elements') or (mode == 'gausspoints'):
            _av.set("placement", mode)
            _av.set("maxpointcount", 1000000)
        else:
            _av.set("placement", "grid");
            _av.set("xnumber", 100);
            _av.set("ynumber", 100);
            _av.set("znumber", 100);

        _av.set("arrowlength", "logarithmic")

        self._pg.run()

    def volume(self, name, obj, mode='volume'):
        if mode == 'volume':
            _vol = self._pg.create(name, "Volume")
        elif mode == 'isosurface':
            _vol = self._pg.create("iso1", "Isosurface")
            _vol.set("number", 100)

        _vol.set("data", "dset1")
        _vol.set("solutionparams", "parent")
        # _vol.set("evaluationsettings", "parent")

        if obj == 'E':
            _vol.set("expr", "emw.normE")
        else:
            _vol.set("expr", "emw.normH")

        _vol.set("colortable", "RainbowLight")
        _vol.set("colorscalemode", "logarithmic")

        self._pg.run()