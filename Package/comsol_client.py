import os

import jpype
import jpype.imports

class ComsolClient:
    _is_started = False

    def __init__(self, comsol_root):
        self.comsol_root = comsol_root
        self.connect()

    def connect(self):
        if self._is_started:
            return

        jvm_path = os.path.join(self.comsol_root, "java", "win64", "jre", "bin", "server", "jvm.dll")
        if not os.path.exists(jvm_path):
            raise FileNotFoundError(f"JVM not found at: {jvm_path}")

        plugins_path = os.path.join(self.comsol_root, "plugins", "*")

        jpype.startJVM(
            jvm_path,
            "-Djava.class.path=" + plugins_path,
            "-Dcs.display=headless"
        )
        ComsolClient._is_started = True

        # 4. 导入核心工具
        from com.comsol.model.util import ModelUtil
        ModelUtil.initStandalone(False)

        self.ModelUtil = ModelUtil
        print("COMSOL client started!")

    def create_model(self, mph_name):
        from comsol_wrapper import JavaWrapper
        java_model = self.ModelUtil.create(mph_name)
        wrapper = JavaWrapper(java_model, mph_name)
        wrapper.modelNode().create("comp1")
        return wrapper

    def load_model(self, mph_path):
        from comsol_wrapper import JavaWrapper
        mph_name = os.path.basename(mph_path)[:-4]
        java_model = self.ModelUtil.load(mph_name, mph_path)
        return JavaWrapper(java_model, mph_name)

    def disconnect(self):
        from comsol_wrapper import JavaWrapper
        self.ModelUtil.disconnect()

