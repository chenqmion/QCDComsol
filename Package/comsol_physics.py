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
            # self.run('pec3d_' + objs)

        except:
            for _obj in objs:
                _pec = self._phy.create('pec3d_' + _obj, "DomainPerfectElectricConductor", 3)
                _pec.label('pec3d_' + _obj)
                _pec.selection().named("geom1_" + _obj + "_dom")
                # self.run('pec3d_' + _obj)

    def port3D(self, port_num, byl_name):
        _port = self._phy.create("lport" + str(port_num), "LumpedPort", 2)
        _port.set("PortType", "Coaxial")
        _port.set("PortExcitation", "off")
        _port.selection().named(byl_name+'_bnd')



