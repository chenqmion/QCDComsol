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

    file_path = os.path.abspath(__file__)
    comsol_client = os.path.dirname(file_path)

    def __init__(self, comsol_root):
        self.comsol_root = comsol_root
        self.connect()

    def connect(self):
        if self._is_started: return

        # --- 1. Platform & Path Setup (Standardized) ---
        current_os = platform.system()
        is_mac = (current_os == "Darwin")
        arch = "macarm64" if (is_mac and platform.machine() == "arm64") else ("maci64" if is_mac else "win64")
        server_exe = "comsol" if is_mac else "comsolmphserver.exe"
        jvm_name = "libjvm.dylib" if is_mac else "jvm.dll"

        bin_path = os.path.join(self.comsol_root, "bin", arch)
        server_executable = os.path.join(bin_path, server_exe)

        # --- 2. Windows DLL Setup ---
        if not is_mac:
            lib_path = os.path.join(self.comsol_root, "lib", arch)
            for p in [bin_path, lib_path]:
                if os.path.exists(p):
                    if p not in os.environ['PATH']:
                        os.environ['PATH'] = p + os.path.pathsep + os.environ['PATH']
                    if hasattr(os, 'add_dll_directory'):
                        try:
                            os.add_dll_directory(p)
                        except:
                            pass

        # --- 3. Start COMSOL Server ---
        print(f"Starting Server: {server_executable}")
        cmd = [server_executable, 'server', '-port', '2036'] if is_mac else [server_executable, '-port', '2036',
                                                                             '-silent']
        self._server_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=os.environ.copy(), universal_newlines=True, shell=(not is_mac)
        )

        # --- 4. Capture Port ---
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

        # --- 5. REFINED CLASSPATH (Top-level only) ---
        print("Loading dependencies (Top-level plugins)...")
        jars = []
        plugins_path = os.path.join(self.comsol_root, "plugins")
        common_path = os.path.join(self.comsol_root, "java", "common")

        # KEY OPTIMIZATION:
        # We load every jar in 'plugins', but DO NOT use recursive=True.
        # This includes javax.websocket, org.eclipse, and com.comsol
        # without diving into conflict-prone subdirectories.
        if os.path.exists(plugins_path):
            jars += glob.glob(os.path.join(plugins_path, "*.jar"))

        if os.path.exists(common_path):
            jars += glob.glob(os.path.join(common_path, "*.jar"))

        # Remove duplicates and sort for deterministic behavior
        jars = sorted(list(set(jars)))
        print(f"Total Jars loaded: {len(jars)}")

        # --- 6. Start JVM ---
        if not jpype.isJVMStarted():
            if is_mac:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "Contents", "Home", "lib", "server",
                                        jvm_name)
            else:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "bin", "server", jvm_name)

            jpype.startJVM(
                jvm_path,
                f"-Djava.class.path={os.path.pathsep.join(jars)}",
                "-Dcs.standalone=false",
                "-Dcs.display=headless",
                "-Xmx2g",
                convertStrings=True
            )

        # --- 7. Final Connection ---
        from com.comsol.model.util import ModelUtil
        time.sleep(2)
        try:
            print(f"Connecting to localhost:{actual_port}...")
            ModelUtil.connect("localhost", actual_port)
            self.ModelUtil = ModelUtil
            ComsolClient._is_started = True
            print(">>> Connection Successful! <<<")
        except Exception as e:
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
        wrapper = JavaWrapper(java_model, mph_name, self.comsol_client)
        wrapper.modelNode().create("comp1")
        return wrapper

    def load_model(self, mph_path):
        from comsol_wrapper import JavaWrapper
        mph_name = os.path.basename(mph_path)[:-4]
        java_model = self.ModelUtil.load(mph_name, mph_path)
        return JavaWrapper(java_model, mph_name, self.comsol_client)

