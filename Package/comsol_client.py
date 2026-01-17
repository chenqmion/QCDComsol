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
        return JavaWrapper(java_model, mph_name)

    def load_model(self, mph_path):
        from comsol_wrapper import JavaWrapper
        mph_name = os.path.basename(mph_path)[:-4]
        java_model = self.ModelUtil.load(mph_name, mph_path)
        return JavaWrapper(java_model, mph_name)

    def disconnect(self):
        from comsol_wrapper import JavaWrapper
        self.ModelUtil.disconnect()
#
# # ================= 1. 启动 JVM =================
# if not jpype.isJVMStarted():
#     path_jvm = os.path.join(comsol_root, r"java\win64\jre\bin\server\jvm.dll")
#     path_plugins = os.path.join(comsol_root, r"plugins\*")
#
#     jpype.startJVM(
#         path_jvm,
#         "-Djava.class.path=" + path_plugins,
#         "-Dcs.display=headless"
#     )
#
#     # from com.comsol.model import *
#     # from com.comsol.model.util import *
#
# print("JVM 启动成功，正在加载 COMSOL API...")
#
# # # ================= 2. 导入 COMSOL 类 =================
# # # ModelUtil 是 COMSOL API 的入口点
# from com.comsol.model.util import ModelUtil
#
# # except ImportError:
# #     print("错误：无法导入 COMSOL 类，请检查 Classpath 路径是否正确")
# #     exit()
# #
# # # ================= 3. 初始化 COMSOL =================
# # # initStandalone(False) 表示不使用图形界面
# ModelUtil.initStandalone(False)
# # print("COMSOL 引擎初始化完成")
# #
# # # ================= 4. 操作模型 =================
# try:
#     # 创建一个新模型
#     model = ModelUtil.create("Model1")
#     print(f"已创建模型: {model.tag()}")
#
#     # 示例：添加一个 3D 组件
#     component = model.modelNode().create("comp1")
#     geom = component.geom().create("geom1", 3)
#
#     # 示例：创建一个 Block
#     blk = geom.feature().create("blk1", "Block")
#     blk.set("size", ["1", "2", "3"])
#     geom.run()
#     print("已创建几何 Block")
#
#     # 保存模型 (可选)
#     model.save(r"test_1.mph")
#     print(os.getcwd())
#
# except Exception as e:
#     print(f"发生错误: {e}")