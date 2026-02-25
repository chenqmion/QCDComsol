import jpype
import numpy as np


class JavaWrapper:
    """
    Core wrapper class for COMSOL objects.
    Preserves specific type conversion logic and smart node navigation.
    """

    def __init__(self, java_model, mph_name="model", comsol_client=None):
        # Use __dict__ to set attributes to avoid infinite recursion in __getattr__
        self.__dict__['_java_model'] = java_model
        self.__dict__['_mph_name'] = mph_name
        self.__dict__['_comsol_client'] = comsol_client

    # =========================================================================
    # 1. Core Logic: Attribute Dispatch & Navigation
    # =========================================================================
    def __getattr__(self, name):
        """
        Attribute lookup priority:
        1. Local methods defined in this class (e.g., save, show_tree)
        2. Special naming corrections (e.g., param -> varnames)
        3. Native Java methods/attributes (with auto type conversion)
        4. COMSOL Child Node Navigation (smart search based on node type)
        """

        # Priority 0: Check if the method exists locally in Python
        if hasattr(self.__class__, name):
            return getattr(self, name)

        class_simple_name = self._get_java_type()

        # Priority 1: Naming conflicts correction
        if name == "param" and class_simple_name == "ModelParamClient":
            name = "varnames"

        # Priority 2: Native Java Access
        if hasattr(self._java_model, name):
            java_attr = getattr(self._java_model, name)

            if callable(java_attr):
                def hooked(*args, **kwargs):
                    new_args = self._convert_args(args)
                    result = java_attr(*new_args, **kwargs)
                    return self._auto_wrap(result)

                return hooked

            return self._auto_wrap(java_attr)

        # Priority 3: Smart Child Node Navigation
        accessors = self._get_allowed_accessors(class_simple_name)
        for method in accessors:
            try:
                accessor = getattr(self._java_model, method)
                child = accessor(name)
                if child is not None:
                    return JavaWrapper(child, self._mph_name, self._comsol_client)
            except:
                continue

        raise AttributeError(f"Attribute '{name}' not found in {self.tag()} ({class_simple_name})")

    def _get_allowed_accessors(self, class_name):
        """Defines valid navigation paths based on the COMSOL object type."""
        if ("Model" in class_name) and ("ModelNode" not in class_name):
            return ["modelNode", "study", "result", "param", "sol"]
        elif "ModelNode" in class_name:
            return ["geom", "material", "physics", "mesh", "view"]
        elif any(x in class_name for x in ["Geom", "Mesh", "Physics", "Study"]):
            return ["feature", "prop", "selection", "create"]
        return ["feature"]

    # =========================================================================
    # 2. Type Conversion Helpers (Python <-> Java)
    # =========================================================================
    def _convert_args(self, args):
        """
        Converts Python arguments to specific Java types (JArray, JInt, etc.)
        FIX: Now checks for mixed types (Int/Float) to prevent crashes.
        """
        new_args = []
        for arg in args:
            # Handle Lists/Tuples -> Java Arrays
            if isinstance(arg, (list, tuple)):
                if not arg:
                    new_args.append(arg)
                    continue

                # FIX: Check if ANY element is a float/numpy.float.
                # If so, we must treat the whole array as Double, even if arg[0] is int.
                has_float = any(isinstance(x, (float, np.floating)) for x in arg)

                first = arg[0]

                if isinstance(first, bool):
                    new_args.append(jpype.JArray(jpype.JBoolean)(arg))
                elif has_float:
                    # Promote mixed arrays (e.g. [0, 0, 1.5]) to Double Array
                    new_args.append(jpype.JArray(jpype.JDouble)(arg))
                elif isinstance(first, int):
                    # Only use Int Array if NO floats are present
                    new_args.append(jpype.JArray(jpype.JInt)(arg))
                elif isinstance(first, str):
                    new_args.append(jpype.JArray(jpype.JString)(arg))
                else:
                    new_args.append(arg)

            # Handle Basic Primitives -> Java Types
            elif isinstance(arg, bool):
                new_args.append(jpype.JBoolean(arg))
            elif isinstance(arg, int):
                new_args.append(jpype.JInt(arg))
            elif isinstance(arg, float):
                new_args.append(jpype.JDouble(arg))
            elif isinstance(arg, str):
                new_args.append(jpype.JString(arg))
            else:
                new_args.append(arg)
        return tuple(new_args)

    def _auto_wrap(self, result):
        """Recursively wraps the result from Java."""
        if result is None:
            return None

        if hasattr(result, 'getClass'):
            java_class_name = str(result.getClass().getName())

            if java_class_name.startswith('['):
                return [self._auto_wrap(x) for x in result]

            if "com.comsol" in java_class_name:
                return JavaWrapper(result, self._mph_name, self._comsol_client)

            if java_class_name.startswith('java.lang.'):
                return self._final_unwrap(result)

        return result

    def _final_unwrap(self, item):
        """Converts Java wrapper types to Python primitives."""
        try:
            cname = item.getClass().getSimpleName()
            if cname == "String": return str(item)
            if cname == "Double": return float(item)
            if cname == "Integer": return int(item)
            if cname == "Boolean": return bool(item)
        except:
            pass
        return item

    # =========================================================================
    # 3. Utility Methods (Information & File IO)
    # =========================================================================
    def _get_java_type(self):
        try:
            return self._java_model.getClass().getSimpleName()
        except:
            return "Unknown"

    def tag(self):
        try:
            return str(self._java_model.tag())
        except:
            return "NoTag"

    def save(self, filename=None):
        target = filename if filename else (self._mph_name + '.mph')
        print(f"Saving to {target}...")
        self._java_model.save(target)

    def show_tree(self, max_depth=3):
        print(f"\n[Tree View] {self.tag()} ({self._get_java_type()})")
        self._print_recursive(self, "", 0, max_depth)

    def _print_recursive(self, node, prefix, depth, max_depth):
        if depth >= max_depth: return
        accessors = self._get_allowed_accessors(node._get_java_type())
        children = []
        for m in accessors:
            try:
                java_res = getattr(node._java_model, m)()
                for c in list(java_res):
                    children.append((m, JavaWrapper(c)))
            except:
                continue

        for i, (m, child) in enumerate(children):
            connector = "└── " if i == len(children) - 1 else "├── "
            print(f"{prefix}{connector}[{m}] {child.tag()} ({child._get_java_type()})")
            next_prefix = prefix + ("    " if i == len(children) - 1 else "│   ")
            self._print_recursive(child, next_prefix, depth + 1, max_depth)