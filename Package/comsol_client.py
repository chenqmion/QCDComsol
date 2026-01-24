import os
import glob
import platform
import subprocess
import time
import re
import jpype
import jpype.imports


class ComsolClient:
    _is_started = False
    _server_process = None

    def __init__(self, comsol_root):
        self.comsol_root = comsol_root
        self.connect()

    def connect(self):
        if self._is_started: return

        # --- Platform Detection ---
        os_name = platform.system()
        is_mac = (os_name == "Darwin")

        # --- 1. Path Setup ---
        if is_mac:
            arch = "macarm64" if platform.machine() == "arm64" else "maci64"
            server_exe = os.path.join(self.comsol_root, "bin", "comsol")
            jvm_name = "libjvm.dylib"
        else:
            arch = "win64"
            server_exe = os.path.join(self.comsol_root, "bin", "comsolserver.exe")
            jvm_name = "jvm.dll"

        # --- 2. Start Server ---
        print(f"Starting Server: {server_exe}")
        # Use 'server' flag on Mac, but standard server exe on Windows
        cmd = [server_exe, 'server', '-port', '2036'] if is_mac else [server_exe, '-port', '2036', '-silent']

        self._server_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=os.environ.copy(), universal_newlines=True,
            shell=(not is_mac)  # Windows needs shell=True often
        )

        # --- 3. Dynamic Port Capture ---
        actual_port = 2036
        start_time = time.time()
        while True:
            line = self._server_process.stdout.readline()
            if line:
                match = re.search(r"listening on port\s+(\d+)", line)
                if match:
                    actual_port = int(match.group(1))
                    print(f"✅ Server Port: {actual_port}")
                    break
            if time.time() - start_time > 30: break

        # --- 4. Dependency Setup (STRICTLY NON-RECURSIVE) ---
        print("Configuring dependencies...")
        jars = []
        # Same logic as your working version
        plugins_path = os.path.join(self.comsol_root, "plugins")
        jars += glob.glob(os.path.join(plugins_path, "*.jar"))

        common_path = os.path.join(self.comsol_root, "java", "common")
        jars += glob.glob(os.path.join(common_path, "*.jar"))
        jars.sort()

        # --- 5. Start JVM ---
        if not jpype.isJVMStarted():
            if is_mac:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "Contents", "Home", "lib", "server",
                                        jvm_name)
            else:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "bin", "server", jvm_name)

            jvm_args = [
                f"-Djava.class.path={os.path.pathsep.join(jars)}",
                "-Dcs.standalone=false",
                "-Dcs.display=headless",
                "-Xmx2g"
            ]
            jpype.startJVM(jvm_path, *jvm_args, convertStrings=True)

        # --- 6. Connection ---
        from com.comsol.model.util import ModelUtil
        print("Waiting 2 seconds for Server...")
        time.sleep(2)

        try:
            print(f"Executing ModelUtil.connect('localhost', {actual_port})...")
            ModelUtil.connect("localhost", actual_port)
            self.ModelUtil = ModelUtil
            ComsolClient._is_started = True
            print(">>> Connection Successful! <<<")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            if self._server_process: self._server_process.kill()
            raise e

    def disconnect(self):
        if self._server_process:
            print("Closing COMSOL Server...")
            if self.ModelUtil:
                try:
                    self.ModelUtil.disconnect()
                except:
                    pass
            self._server_process.kill()
            ComsolClient._is_started = False

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

