import os
import numpy as np
import textwrap
import re
import jpype

class physics_mixin:
    def __init__(self, model, name, phys):
        comp = model.modelNode("comp1")
        phy = comp.physics().create(name, phys, "geom1")

        self._comp = comp
        self._phy = phy
        self._name = name

    def show_options(self):
        print("ElectromagneticWaves", "Electrostatics")

    def PEC_3D(self, objs):
        try:
            _pec = self._phy.create('pec3d_' + objs, "DomainPerfectElectricConductor", 3)
            _pec.label('pec3d_' + objs)
            _pec.selection().named("geom1_" + objs + "_dom")

        except:
            for _obj in objs:
                _pec = self._phy.create('pec3d_' + _obj, "DomainPerfectElectricConductor", 3)
                _pec.label('pec3d_' + _obj)
                _pec.selection().named("geom1_" + _obj + "_dom")

    def port3D(self, port_num, cyl_name):
        _port = self._phy.create("lport" + str(port_num), "LumpedPort", 2)
        _port.set("PortType", "Coaxial")
        _port.set("PortExcitation", "off")
        _port.selection().named(cyl_name+'_bnd')

    def PEC_2D(self, objs):
        try:
            _pec = self._phy.create('pec2d_' + objs, "PerfectElectricConductor", 2)
            _pec.label('pec2d_' + objs)
            _pec.selection().named(objs + "_bnd")

        except:
            for _obj in objs:
                _pec = self._phy.create('pec2d_' + _obj, "PerfectElectricConductor", 2)
                _pec.label('pec2d_' + _obj)
                _pec.selection().named(_obj + "_bnd")

    def Lumped(self, obj, type, value):
        _port = self._phy.create("lump_" + obj, "LumpedElement", 2)
        _port.set("LumpedElementType", type)

        if type == 'Inductor':
            _port.set("Lelement", value)

        _port.selection().named(obj+'_bnd')



