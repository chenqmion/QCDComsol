import jpype
import numpy as np

class JavaWrapper:
    """
    Generic Wrapper combining JPype type conversion and COMSOL node navigation.
    English comments used as requested.
    """

    def __init__(self, java_model, mph_name="model", comsol_client=None):
        self._java_model = java_model
        self._mph_name = mph_name
        self._comsol_client = comsol_client

    def __getattr__(self, name):
        # Phase 0: Fix the specific naming conflict for Parameters
        class_simple_name = self._get_java_type()

        # If we are on the Parameter object and user calls .param(),
        # redirect to .varnames() which is the actual Java method name.
        if name == "param" and class_simple_name == "ModelParamClient":
            name = "varnames"

        # Phase 1: Native Java Access
        try:
            java_attr = getattr(self._java_model, name)
            if callable(java_attr):
                def hooked(*args, **kwargs):
                    new_args = self._convert_args(args)
                    result = java_attr(*new_args, **kwargs)

                    if result is None:
                        return None

                    if hasattr(result, 'getClass'):
                        # Convert the Java String to a Python string explicitly
                        java_class_name = str(result.getClass().getName())

                        # 1. Wrap COMSOL-specific objects
                        if "com.comsol" in java_class_name:
                            return JavaWrapper(result, self._mph_name, self._comsol_client)

                        # 2. Now .startswith() will work because java_class_name is a Python str
                        if java_class_name.startswith('['):
                            return [self._wrap_result(x) for x in result]

                        # 3. Handle basic Java lang types
                        if java_class_name.startswith('java.lang.'):
                            return self._wrap_result(result)

                    return result

                return hooked
            return java_attr
        except AttributeError:
            pass

        # Phase 2: Child Node Lookup (e.g., model.physics("emw"))
        class_name = self._get_java_type()
        allowed = self._get_allowed_accessors(class_name)

        for method in allowed:
            try:
                if hasattr(self._java_model, method):
                    # Attempt to fetch child by name, e.g., model.geom("geom1")
                    child = getattr(self._java_model, method)(name)
                    if child is not None:
                        return JavaWrapper(child, self._mph_name, self._comsol_client)
            except:
                # If this accessor fails, continue to the next one in the list
                continue

        raise AttributeError(f"Attribute '{name}' not found on {self.tag()} ({class_name})")

    def _convert_java_array(self, java_array):
        """Recursively converts Java arrays/collections to Python lists."""
        python_list = []
        for item in java_array:
            if hasattr(item, 'getClass') and str(item.getClass().getName()).startswith('['):
                # If the item is itself an array (2D, 3D...), recurse
                python_list.append(self._convert_java_array(item))
            else:
                # Otherwise, wrap the individual element (converts Double to float, etc.)
                python_list.append(self._wrap_result(item))
        return python_list

    def _wrap_result(self, item):
        """Convert basic Java return types to native Python types."""
        if item is None: return None
        if isinstance(item, (str, int, float, bool)): return item

        # Check simple class names for conversion
        try:
            cname = item.getClass().getSimpleName()
            if cname == "String": return str(item)
            if cname == "Double": return float(item)
            if cname == "Integer": return int(item)
            if cname == "Boolean": return bool(item)
        except:
            pass
        return item

    def _convert_args(self, args):
        """
        Smart conversion:
        - Integers stay as JInt (needed for geom dim, index, etc.)
        - Floats become JDouble (needed for parameters, coordinates)
        - Lists are converted to typed JArrays
        """
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if not arg:
                    new_args.append(arg)
                elif any(isinstance(x, bool) for x in arg):
                    new_args.append(jpype.JArray(jpype.JBoolean)(arg))
                elif any(isinstance(x, float) for x in arg):
                    # If list contains any float, convert whole list to Double
                    new_args.append(jpype.JArray(jpype.JDouble)([float(x) for x in arg]))
                elif any(isinstance(x, int) for x in arg):
                    new_args.append(jpype.JArray(jpype.JInt)(arg))
                elif any(isinstance(x, str) for x in arg):
                    new_args.append(jpype.JArray(jpype.JString)(arg))
                else:
                    new_args.append(arg)

            elif isinstance(arg, bool):
                new_args.append(jpype.JBoolean(arg))

            # --- KEY FIX HERE ---
            elif isinstance(arg, int):
                # Keep as Integer for COMSOL dimensions/counts
                new_args.append(jpype.JInt(arg))
            elif isinstance(arg, float):
                # Use Double for precision/coordinates/parameters
                new_args.append(jpype.JDouble(arg))
            # --------------------

            elif isinstance(arg, str):
                new_args.append(jpype.JString(arg))
            else:
                new_args.append(arg)
        return tuple(new_args)

    def _get_allowed_accessors(self, class_name):
        """Determine which accessor methods are valid for the current Java class type."""
        if ("Model" in class_name) and ("ModelNode" not in class_name):
            return ["modelNode", "study", "result", "param"]
        elif "ModelNode" in class_name:
            return ["geom", "material", "physics", "mesh"]
        elif "Param" in class_name:
            # ModelParamClient handles get/set directly
            return []
        elif any(x in class_name for x in ["Geom", "Mesh", "Physics", "Study"]):
            return ["feature", "prop", "selection"]
        return ["feature"]

    def _get_java_type(self):
        """Get the simple class name of the wrapped Java object."""
        try:
            return self._java_model.getClass().getSimpleName()
        except:
            return "Unknown"

    def tag(self):
        """Get the COMSOL tag for the node."""
        try:
            return self._java_model.tag()
        except:
            return "NoTag"

    def save(self, filename=None):
        """Saves the mph file."""
        target = filename if filename else (self._mph_name + '.mph')
        print(f"Saving to {target}...")
        self._java_model.save(target)

    def show_tree(self, max_depth=5):
        """Prints a visual tree of the model structure."""
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
                java_method = getattr(wrapper_node._java_model, method)
                found = java_method()
                if found is not None:
                    # Convert found collection to list for iteration
                    child_list = list(found)
                    for c in child_list:
                        children.append((method, JavaWrapper(c, self._mph_name, self._comsol_client)))
            except:
                continue

        count = len(children)
        for i, (m, child) in enumerate(children):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}[{m}] {child.tag()} ({child._get_java_type()})")
            new_prefix = prefix + ("    " if is_last else "│   ")
            self._print_recursive(child, new_prefix, depth + 1, max_depth)