# comsol_client.py
import os, jpype, jpype.imports
from comsol_server import ComsolServer
from comsol_wrapper import JavaWrapper

class ComsolClient:
    """
    管理 JVM 生命周期、COMSOL 连接以及模型的创建与加载。
    注意：JVM 进程全局只能启动一次（JPype 限制），因此本类应在整个脚本中只实例化一次。
    """
    _jvm_started = False  # 类变量：仅用于防止重复启动 JVM，语义清晰

    def __init__(self, comsol_root: str):
        self.comsol_root = comsol_root
        self._package_dir = os.path.dirname(os.path.abspath(__file__))
        self.ModelUtil = None

        server = ComsolServer(comsol_root)
        port = server.start()
        self._server = server

        if not ComsolClient._jvm_started:
            classpath = self._build_classpath()
            jvm_path = self._get_jvm_path(server._arch, server._is_mac)
            self._start_jvm(jvm_path, classpath)
            ComsolClient._jvm_started = True

        self.ModelUtil = self._connect_model_util(port)
        print(f">>> COMSOL Connected (port {port}) <<<")

    # --- JVM 相关 ---

    def _build_classpath(self) -> list[str]:
        plugins = os.path.join(self.comsol_root, "plugins")
        common = os.path.join(self.comsol_root, "java", "common")
        jars = []
        if os.path.exists(plugins):
            for f in os.listdir(plugins):
                if f.endswith(".jar") and f.lower().startswith(
                    ("com.comsol.", "org.eclipse.", "javax.websocket")
                ):
                    jars.append(os.path.join(plugins, f))
        if os.path.exists(common):
            jars += [os.path.join(common, f) for f in os.listdir(common) if f.endswith(".jar")]
        return sorted(set(jars))

    def _get_jvm_path(self, arch: str, is_mac: bool) -> str:
        lib = "libjvm.dylib" if is_mac else "jvm.dll"
        if is_mac:
            return os.path.join(self.comsol_root, "java", arch, "jre", "Contents", "Home", "lib", "server", lib)
        return os.path.join(self.comsol_root, "java", arch, "jre", "bin", "server", lib)

    def _start_jvm(self, jvm_path: str, classpath: list[str]):
        jpype.startJVM(
            jvm_path,
            f"-Djava.class.path={os.path.pathsep.join(classpath)}",
            "-XX:TieredStopAtLevel=1",
            "-Dcs.standalone=false",
            "-Dcs.display=headless",
            "-Xmx2g",
            convertStrings=True,
        )

    # --- COMSOL 连接 ---

    def _connect_model_util(self, port: int):
        from com.comsol.model.util import ModelUtil
        import time
        for _ in range(20):
            try:
                ModelUtil.connect("localhost", port)
                return ModelUtil
            except:
                time.sleep(0.1)
        raise RuntimeError(f"Failed to connect to COMSOL at port {port}")

    # --- 模型操作 ---

    def create_model(self, name: str):
        try:
            self.ModelUtil.remove(name)  # 清除同名旧模型
        except:
            pass
        java_model = self.ModelUtil.create(name)
        model = JavaWrapper(java_model, name, self._package_dir)
        model.modelNode().create("comp1")
        return model

    def load_model(self, mph_path: str) -> JavaWrapper:
        if not os.path.exists(mph_path):
            raise FileNotFoundError(mph_path)
        name = os.path.basename(mph_path).replace(".mph", "")
        java_model = self.ModelUtil.load(name, mph_path)
        return JavaWrapper(java_model, name, self._package_dir)

    def disconnect(self):
        try: self.ModelUtil.disconnect()
        except: pass
        self._server.stop()
        print(">>> COMSOL Disconnected <<<")