import jpype

class JavaWrapper:
    def __init__(self, java_model, mph_name):
        self._java_model = java_model
        self._mph_name = mph_name

    def __getattr__(self, name):
        java_attr = getattr(self._java_model, name)

        if callable(java_attr):
            def hooked(*args, **kwargs):
                new_args = self._convert_args(args)
                result = java_attr(*new_args, **kwargs)
                if (result is not None) and (hasattr(result, 'getClass')):
                    class_name = result.getClass().getName()
                    if ("com.comsol" in class_name):
                        return JavaWrapper(result, self._mph_name)

                return result
            return hooked

        return java_attr

    def _convert_args(self, args):
        new_args = []
        for arg in args:
            if isinstance(arg, list):
                if any(isinstance(x, str) for x in arg):
                    new_args.append(jpype.JArray(jpype.JString)(arg))
                elif any(isinstance(x, float) for x in arg):
                    new_args.append(jpype.JArray(jpype.JDouble)(arg))
                elif all(isinstance(x, int) for x in arg):
                    new_args.append(jpype.JArray(jpype.JInt)(arg))
                elif all(isinstance(x, bool) for x in arg):
                    new_args.append(jpype.JArray(jpype.JBoolean)(arg))
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)
        return tuple(new_args)

    def save(self):
        self._java_model.save(self._mph_name + r'.mph')
        return None

    def get_data(self, name):
        try:
            val = self._java_model.getStringArray(name)
            return list(val)
        except:
            pass

        try:
            val = self._java_model.getString(name)
            return str(val)
        except:
            pass

        try:
            val = self._java_model.getDouble(name)
            return float(val)
        except:
            pass

        try:
            val = self._java_model.getInt(name)
            return int(val)
        except:
            pass

        try:
            val = self._java_model.getBoolean(name)
            return bool(val)
        except:
            pass
