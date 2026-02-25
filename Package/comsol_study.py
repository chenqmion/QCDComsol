class study_mixin:
    def __init__(self, model, name):
        std = model.study().create(name)

        self._model = model
        self._std = std
        self._std_name = name

    def solve_eigenfrequency(self, *, freq, num, mode='lr'):
        stp = self._std.feature().create('eig1', "Eigenfrequency")
        stp.set("eigunit", "GHz")
        stp.set('shift', str(freq/1e9))
        stp.set('neigs', num)
        stp.set('eigwhich', mode)

        self._std.createAutoSequences("all")
        self._model.sol('sol1').runAll()

    def param_sweep(self, var, rang):
        stp = self._std.create("param", "Parametric")
        stp.setIndex("pname", var, 0)
        stp.setIndex("plistarr", " ".join(str(_x) for _x in rang), 0)
        stp.setIndex("punit", "GHz", 0)

        self._std.createAutoSequences("all")
        sol2 = self._model.sol().create("sol2")
        sol2.study("std1")
        sol2.label("Parametric Solutions 1")

        self._model.batch("p1").feature("so1").set("psol", "sol2")
        self._model.batch("p1").run("compute")