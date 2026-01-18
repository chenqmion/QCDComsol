import os
import numpy as np
import textwrap
import re
import jpype

class physics_mixin:
    def create_physics(self, name="emw", phys="ElectromagneticWaves"):
        # comp = self.modelNode("comp1")
        _phy = self.comp1.physics().create(name, phys, "geom1")
        return _phy

    def show_options(self):
        print("ElectromagneticWaves", "Electrostatics")

    def PEC_3D(self, objs):
        try:
            _pec = self.create('pec3d_' + objs, "DomainPerfectElectricConductor", 3)
            _pec.label('pec3d_' + objs)
            _pec.selection().named("geom1_" + objs + "_dom")
            # self.run('pec3d_' + objs)

        except:
            for _obj in objs:
                _pec = self.create('pec3d_' + _obj, "DomainPerfectElectricConductor", 3)
                _pec.label('pec3d_' + _obj)
                _pec.selection().named("geom1_" + _obj + "_dom")
                # self.run('pec3d_' + _obj)

    def port3D(self, port_num, bnd_name):
        _port = self.create("lport" + str(port_num), "LumpedPort", 2)
        _port.set("PortType", "Coaxial")
        _port.set("PortExcitation", "off")
        _port.selection().named(bnd_name)

        # model.physics("emw").create("lport1", "LumpedPort", 2)
        # model.physics("emw").feature("lport1").set("PortType", "Coaxial")
        # model.physics("emw").feature("lport1").set("PortExcitation", "off")
        # model.physics("emw").feature("lport1").selection().set(1)


