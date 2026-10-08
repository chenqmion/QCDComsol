import jpype
import numpy as np

class JavaWrapper:
    def __init__(self, java_model, mph_name="model", comsol_client=None):
        # 使用 __dict__ 赋值，彻底避免 __getattr__ 循环
        self.__dict__['_java_model'] = java_model
        self.__dict__['_mph_name'] = mph_name
        self.__dict__['_comsol_client'] = comsol_client

    def __getattr__(self, name):
        """
        属性查找优先级：
        1. 本地定义的方法 (save, show_tree)
        2. 特殊命名修正 (param -> varnames)
        3. 原生 Java 方法/属性
        4. COMSOL 节点导航 (geom, physics...)
        """
        # 0. 优先返回本地定义的方法
        if hasattr(self.__class__, name):
            return getattr(self, name)

        # 1. 特殊命名冲突修正
        class_simple_name = self._get_java_type()
        if name == "param" and class_simple_name == "ModelParamClient":
            name = "varnames"

        # 2. 原生 Java 访问
        if hasattr(self._java_model, name):
            java_attr = getattr(self._java_model, name)
            if callable(java_attr):
                def hooked(*args, **kwargs):
                    new_args = self._convert_args(args)
                    result = java_attr(*new_args, **kwargs)
                    return self._auto_wrap(result)

                return hooked
            return self._auto_wrap(java_attr)

        # 3. COMSOL 子节点快捷导航
        accessors = self._get_allowed_accessors(class_simple_name)
        for method in accessors:
            try:
                # 尝试调用诸如 modelNode("comp1") 或 geom("geom1")
                accessor = getattr(self._java_model, method)
                child = accessor(name)
                if child is not None:
                    return JavaWrapper(child, self._mph_name, self._comsol_client)
            except:
                continue

        raise AttributeError(f"在 {self.tag()} ({class_simple_name}) 中找不到属性: '{name}'")

    def _auto_wrap(self, result):
        """统一的包装逻辑"""
        if result is None:
            return None

        # 处理 Java 数组 (递归转换)
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
        """将 Java 基础类型转为 Python"""
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
        """将 Python 参数转为 Java 需要的 JArray/JInt 等"""
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if not arg:
                    new_args.append(arg)
                # 优化：根据第一个元素判断数组类型，提升效率
                first = arg[0]
                if isinstance(first, bool):
                    new_args.append(jpype.JArray(jpype.JBoolean)(arg))
                elif isinstance(first, float):
                    new_args.append(jpype.JArray(jpype.JDouble)(arg))
                elif isinstance(first, int):
                    new_args.append(jpype.JArray(jpype.JInt)(arg))
                elif isinstance(first, str):
                    new_args.append(jpype.JArray(jpype.JString)(arg))
                else:
                    new_args.append(arg)
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

    def _get_allowed_accessors(self, class_name):
        """定义不同节点的合法跳转路径"""
        if ("Model" in class_name) and ("ModelNode" not in class_name):
            return ["modelNode", "study", "result", "param", "sol"]
        elif "ModelNode" in class_name:
            return ["geom", "material", "physics", "mesh", "view"]
        elif any(x in class_name for x in ["Geom", "Mesh", "Physics", "Study"]):
            return ["feature", "prop", "selection", "create"]
        return ["feature"]

    # --- 以下是本地工具方法 ---

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
        print(f"\n📦 {self.tag()} ({self._get_java_type()})")
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
            self._print_recursive(child, prefix + ("    " if i == len(children) - 1 else "│   "), depth + 1, max_depth)