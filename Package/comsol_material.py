import os
import numpy as np
import textwrap
import re
import jpype

class material_mixin:
    def create_material(self, name):
        comp = self.modelNode("comp1")
        _mat = comp.material().create(name, "Common")

        material_path = os.path.join(os.getcwd(), "material", "comsol_" + name + '.txt')
        if os.path.exists(material_path):
            context = {'_mat': _mat,
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

                output_path = "fixed_.txt"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(clean_code)

                exec(clean_code, globals(), context)

            print('Loaded material')

        return _mat

    def new_param(self, *, tags, values):
        try:
            self.propertyGroup("def").set(tags, values)
        except:
            for num_tag in range(np.size(tags)):
                self.propertyGroup("def").set(tags[num_tag], values[num_tag])

    def select(self, objs):
        try:
            self.selection().named(objs)
        except:
            for _obj in objs:
                self.selection().named(_obj)

