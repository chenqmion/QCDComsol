import jpype
from comsol_geometry import geometry_mixin
from comsol_material import material_mixin

class JavaWrapper(geometry_mixin, material_mixin):
    """
    Generic Wrapper combining JPype type conversion and Mixin functionality.
    """

    def __init__(self, java_model, mph_name=None):
        self._java_model = java_model
        self._mph_name = mph_name

    def __getattr__(self, name):
        # Phase 1: Native Java
        try:
            java_attr = getattr(self._java_model, name)
            if callable(java_attr):
                def hooked(*args, **kwargs):
                    new_args = self._convert_args(args)
                    result = java_attr(*new_args, **kwargs)
                    if result is not None and hasattr(result, 'getClass'):
                        if "com.comsol" in result.getClass().getName():
                            return JavaWrapper(result, self._mph_name)
                    return result
                return hooked
            return java_attr
        except AttributeError:
            pass

        # Phase 2: Child Node Lookup
        try:
            class_name = self._get_java_type()
            allowed = self._get_allowed_accessors(class_name)

            for method in allowed:
                if hasattr(self._java_model, method):
                    child = getattr(self._java_model, method)(name)
                    if child is not None:
                        return JavaWrapper(child, self._mph_name)
        except:
            pass

        raise AttributeError(f"Attribute '{name}' not found on {self.tag()} ({class_name})")

    def _convert_args(self, args):
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if not arg:
                    new_args.append(arg)
                elif any(isinstance(x, bool) for x in arg):
                    new_args.append(jpype.JArray(jpype.JBoolean)(arg))
                elif any(isinstance(x, float) for x in arg):
                    new_args.append(jpype.JArray(jpype.JDouble)(arg))
                elif any(isinstance(x, int) for x in arg):
                    new_args.append(jpype.JArray(jpype.JInt)(arg))
                elif any(isinstance(x, str) for x in arg):
                    new_args.append(jpype.JArray(jpype.JString)(arg))
                else: new_args.append(arg)

            elif isinstance(arg, bool):
                new_args.append(jpype.JBoolean(arg))
            elif isinstance(arg, float):
                new_args.append(jpype.JDouble(arg))
            elif isinstance(arg, int):
                new_args.append(jpype.JInt(arg))
            elif isinstance(arg, str):
                new_args.append(jpype.JString(arg))
            else:
                new_args.append(arg)

        return tuple(new_args)

    def _get_allowed_accessors(self, class_name):
        if ("Model" in class_name) and ("ModelNode" not in class_name):
            return ["modelNode", "study", "result", "material", "dataset"]
        elif "ModelNode" in class_name:
            return ["geom", "mesh", "physics", "material"]
        elif any(x in class_name for x in ["Geom", "Mesh", "Physics", "Study"]):
            return ["feature", "prop", "selection"]
        return ["feature"]

    def _get_java_type(self):
        try: return self._java_model.getClass().getSimpleName()
        except: return "Unknown"

    def tag(self):
        try: return self._java_model.tag()
        except: return "NoTag"

    def save(self, filename=None):
        target = filename if filename else (self._mph_name + '.mph')
        print(f"Saving to {target}...")
        self._java_model.save(target)

    def show_tree(self, max_depth=5):
        print(f"\n📦 {self.tag()} ({self._get_java_type()})")
        self._print_recursive(self, "", 0, max_depth)

    def _print_recursive(self, wrapper_node, prefix, depth, max_depth):
        if depth >= max_depth:
            return

        class_name = wrapper_node._get_java_type()
        allowed = self._get_allowed_accessors(class_name)

        children = []
        for method in allowed:
            try:
                if not hasattr(wrapper_node._java_model, method):
                    continue

                # Get the child collection (e.g., .feature(), .geom())
                java_method = getattr(wrapper_node._java_model, method)
                found = java_method()

                # Validation: COMSOL collections usually have a .tags() or are iterable
                if found is not None:
                    # Check if it's actually a collection we can iterate over
                    # We wrap it in list() to verify it's a valid Java collection/array
                    child_list = list(found)
                    for c in child_list:
                        children.append((method, wrapper_node.__class__(c, wrapper_node._mph_name)))
            except:
                # If the method exists but fails (e.g., needs args or not a collection), skip it
                continue

        count = len(children)
        for i, (m, child) in enumerate(children):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}[{m}] {child.tag()} ({child._get_java_type()})")

            # Recurse
            new_prefix = prefix + ("    " if is_last else "│   ")
            self._print_recursive(child, new_prefix, depth + 1, max_depth)