# comsol_server.py
import platform, subprocess, re, time, os

class ComsolServer:
    """管理 COMSOL server 进程的启动与停止。"""

    def __init__(self, comsol_root: str):
        self.comsol_root = comsol_root
        self._process = None
        self._arch, self._is_mac = self._detect_platform()

    def _detect_platform(self):
        system = platform.system()
        is_mac = (system == "Darwin")
        if is_mac:
            arch = "macarm64" if platform.machine() == "arm64" else "maci64"
        else:
            arch = "win64"
        return arch, is_mac

    def start(self) -> int:
        """启动 server，返回实际监听端口。"""
        if platform.system() == "Windows":
            os.system("taskkill /F /IM comsolmphserver.exe /T >nul 2>&1")

        bin_path = os.path.join(self.comsol_root, "bin", self._arch)
        exe = "comsol" if self._is_mac else "comsolmphserver.exe"
        exe_path = os.path.join(bin_path, exe)

        if not self._is_mac:
            self._patch_windows_dll_path(bin_path)

        cmd = [exe_path, "server", "-port", "2036"] if self._is_mac else [exe_path, "-port", "2036"]
        self._process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=os.environ.copy(), universal_newlines=True, shell=(not self._is_mac)
        )
        return self._wait_for_port()

    def _patch_windows_dll_path(self, bin_path):
        lib_path = os.path.join(self.comsol_root, "lib", self._arch)
        for p in [bin_path, lib_path]:
            if os.path.exists(p) and p not in os.environ["PATH"]:
                os.environ["PATH"] = p + os.path.pathsep + os.environ["PATH"]
                if hasattr(os, "add_dll_directory"):
                    try: os.add_dll_directory(p)
                    except: pass

    def _wait_for_port(self, timeout=30) -> int:
        start = time.time()
        while time.time() - start < timeout:
            line = self._process.stdout.readline()
            if line:
                m = re.search(r"listening on port\s+(\d+)", line)
                if m:
                    return int(m.group(1))
        return 2036  # fallback

    def stop(self):
        if self._process:
            self._process.kill()
            self._process = None