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

        # Windows 专用的清理逻辑：启动前杀掉残留的 server
        if platform.system() == "Windows":
            os.system("taskkill /F /IM comsolmphserver.exe /T >nul 2>&1")

        # --- 1. Platform Detection ---
        current_os = platform.system()
        is_mac = (current_os == "Darwin")
        arch = "macarm64" if (is_mac and platform.machine() == "arm64") else ("maci64" if is_mac else "win64")

        # Executable names based on your diagnostic
        server_exe = "comsol" if is_mac else "comsolmphserver.exe"
        jvm_lib_name = "libjvm.dylib" if is_mac else "jvm.dll"

        bin_path = os.path.join(self.comsol_root, "bin", arch)
        server_executable = os.path.join(bin_path, server_exe)

        # --- 2. Windows DLL Environment Fix ---
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

        # --- 3. Start Server ---
        print(f"Starting Server: {server_executable}")
        # Note: No -silent on Windows to ensure we see port reassignments
        cmd = [server_executable, 'server', '-port', '2036'] if is_mac else [server_executable, '-port', '2036']

        self._server_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=os.environ.copy(), universal_newlines=True, shell=(not is_mac)
        )

        # --- 4. Dynamic Port Capture ---
        actual_port = 2036
        start_time = time.time()
        while True:
            line = self._server_process.stdout.readline()
            if line:
                print(f"Server Log: {line.strip()}")
                match = re.search(r"listening on port\s+(\d+)", line)
                if match:
                    actual_port = int(match.group(1))
                    print(f"✅ Server Port: {actual_port}")
                    break
            if time.time() - start_time > 30:
                break

        # --- 5. REFINED CLASSPATH (Fixed Variable Scope) ---
        print("Loading dependencies (Top-level plugins)...")
        jars_list = []  # Renamed to avoid confusion
        plugins_path = os.path.join(self.comsol_root, "plugins")
        common_path = os.path.join(self.comsol_root, "java", "common")

        # Non-recursive top-level scan (Prevents Jetty conflicts)
        if os.path.exists(plugins_path):
            jars_list += glob.glob(os.path.join(plugins_path, "*.jar"))

        if os.path.exists(common_path):
            jars_list += glob.glob(os.path.join(common_path, "*.jar"))

        jars_list = sorted(list(set(jars_list)))
        print(f"Total Jars loaded: {len(jars_list)}")

        # --- 6. Start JVM ---
        if not jpype.isJVMStarted():
            if is_mac:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "Contents", "Home", "lib", "server",
                                        jvm_lib_name)
            else:
                jvm_path = os.path.join(self.comsol_root, "java", arch, "jre", "bin", "server", jvm_lib_name)

            jpype.startJVM(
                jvm_path,
                f"-Djava.class.path={os.path.pathsep.join(jars_list)}",
                "-Xverify:none",  # 核心提速参数
                "-Dcs.standalone=false",
                "-Dcs.display=headless",
                "-Xmx2g",
                convertStrings=True
            )

            # --- 7. Final Connection (Optimized Handshake) ---
            from com.comsol.model.util import ModelUtil
            print(f"Connecting to localhost:{actual_port}...")

            connected = False
            # 最多尝试 20 次，每次间隔 0.1s，总计 2s
            for i in range(20):
                try:
                    ModelUtil.connect("localhost", actual_port)
                    connected = True
                    break
                except:
                    time.sleep(0.1)

            if not connected:
                raise RuntimeError(f"Failed to connect to COMSOL at port {actual_port} after 2s.")

            self.ModelUtil = ModelUtil
            ComsolClient._is_started = True
            print(">>> Connection Successful! <<<")

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

