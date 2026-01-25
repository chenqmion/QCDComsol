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

        import os, subprocess, time, platform, re, glob, jpype

        # --- 1. Platform Detection ---
        current_os = platform.system()
        is_mac = (current_os == "Darwin")

        # --- 2. Path Setup based on your Scan ---
        if is_mac:
            arch = "macarm64" if platform.machine() == "arm64" else "maci64"
            server_exe_name = "comsol"
            jvm_lib_name = "libjvm.dylib"
        else:
            arch = "win64"
            # Updated based on your diagnostic: comsolmphserver.exe
            server_exe_name = "comsolmphserver.exe"
            jvm_lib_name = "jvm.dll"

        # Construct path: C:\Programs\Comsol\bin\win64\comsolmphserver.exe
        bin_arch_path = os.path.join(self.comsol_root, "bin", arch)
        server_executable = os.path.join(bin_arch_path, server_exe_name)

        if not os.path.exists(server_executable):
            raise FileNotFoundError(f"Executable not found at {server_executable}. "
                                    f"Please check your comsol_root.")

        # --- 3. Windows DLL Environment Fix ---
        if not is_mac:
            # Add bin and lib to PATH so dependencies like fl_node.dll are found
            lib_arch_path = os.path.join(self.comsol_root, "lib", arch)
            for p in [bin_arch_path, lib_arch_path]:
                if os.path.exists(p) and p not in os.environ['PATH']:
                    os.environ['PATH'] = p + os.path.pathsep + os.environ['PATH']

            # Python 3.8+ DLL Directory Logic
            if hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(bin_arch_path)
                    if os.path.exists(lib_arch_path):
                        os.add_dll_directory(lib_arch_path)
                except Exception as e:
                    print(f"Note: DLL directory notice: {e}")

        # --- 4. Start Server ---
        print(f"Starting Server: {server_executable}")
        # Windows comsolmphserver.exe doesn't need 'server' argument
        cmd = [server_executable, 'server', '-port', '2036'] if is_mac else [server_executable, '-port', '2036']

        self._server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
            universal_newlines=True,
            shell=(not is_mac)
        )

        # --- 5. Port Capture ---
        actual_port = 2036
        start_time = time.time()
        while True:
            line = self._server_process.stdout.readline()
            if line:
                # Capture the port from log: e.g., "COMSOL Multiphysics server ... listening on port 2036"
                match = re.search(r"listening on port\s+(\d+)", line)
                if match:
                    actual_port = int(match.group(1))
                    print(f"✅ Server Port: {actual_port}")
                    break
            if time.time() - start_time > 30:
                print("⚠️ Port capture timeout. Please check your license.")
                break

        # --- 6. JVM Dependency Setup (Clean Classpath) ---
        jars = []
        plugins_path = os.path.join(self.comsol_root, "plugins")
        common_path = os.path.join(self.comsol_root, "java", "common")
        for p in [plugins_path, common_path]:
            if os.path.exists(p):
                jars += glob.glob(os.path.join(p, "*.jar"))
        jars.sort()

        # --- 7. Start JVM ---
        if not jpype.isJVMStarted():
            if is_mac:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "Contents", "Home", "lib", "server",
                                        jvm_lib_name)
            else:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "bin", "server", jvm_lib_name)

            jpype.startJVM(
                jvm_path,
                f"-Djava.class.path={os.path.pathsep.join(jars)}",
                "-Dcs.standalone=false",
                "-Dcs.display=headless",
                "-Xmx2g",
                convertStrings=True
            )

        # --- 8. Connect ---
        from com.comsol.model.util import ModelUtil
        time.sleep(2)  # Necessary delay for Windows socket stabilization
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

    def disconnect(self):
        from comsol_wrapper import JavaWrapper
        self.ModelUtil.disconnect()

