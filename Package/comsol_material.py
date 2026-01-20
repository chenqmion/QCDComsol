import os
import numpy as np
import textwrap
import re
import jpype

class material_mixin:
    def __init__(self, model, name):
        comp = model.modelNode("comp1")
        mat = comp.material().create(name, "Common")

        self._comp = comp
        self._mat = mat
        self._name = name

        material_path = os.path.join(model._comsol_client, "material", "comsol_" + name + '.txt')
        if os.path.exists(material_path):
            self.builtin_material(material_path)

    def builtin_material(self, material_path):
        context = {'_mat': self._mat,
                   'true': True,
                   'false': False}
        with open(material_path, 'r') as f:
            clean_code = re.sub(r'new\s+\w+(?=\()', '', f.read())
            clean_code = re.sub(r'new\s+\w+(\[\])+\s*\{', '[', clean_code)
            clean_code = re.sub(r'\((double|int|float|String|boolean)\)', '', clean_code)
            clean_code = clean_code.replace('{', '[').replace('}', ']').replace(';', '')
            clean_code = clean_code.replace('model.component("comp1").material("mat1")', '_mat')

            clean_code = textwrap.dedent(clean_code)
            lines = [line.strip() for line in clean_code.splitlines() if line.strip()]

            processed_lines = []
            for line in lines:
                if line.startswith(".") and processed_lines:
                    processed_lines[-1] = processed_lines[-1] + line
                else:
                    processed_lines.append(line)

            clean_code = "\n".join(processed_lines)
            exec(clean_code, globals(), context)

    def new_param(self, *, tags, values):
        try:
            self._mat.propertyGroup("def").set(tags, values)
        except:
            for num_tag in range(np.size(tags)):
                self._mat.propertyGroup("def").set(tags[num_tag], values[num_tag])

    def select(self, objs):
        try:
            self._mat.selection().named("geom1_" + objs + "_dom")
        except:
            for _obj in objs:
                self._mat.selection().named("geom1_" + _obj + "_dom")

