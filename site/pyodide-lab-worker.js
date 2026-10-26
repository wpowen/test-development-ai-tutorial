const PYODIDE_INDEX = "https://cdn.jsdelivr.net/pyodide/v314.0.4/full/";
const PYODIDE_MODULE = "https://cdn.jsdelivr.net/pyodide/v314.0.4/full/pyodide.mjs";
let runtimePromise;

async function runtime() {
  if (!runtimePromise) runtimePromise = (async () => {
    const { loadPyodide } = await import(PYODIDE_MODULE);
    return loadPyodide({ indexURL: PYODIDE_INDEX });
  })();
  return runtimePromise;
}

const pythonRunner = String.raw`
import contextlib, hashlib, io, json, os, runpy, shlex, sys, traceback

commands = json.loads(__course_commands)
workspace = __course_workspace
expected_artifacts = json.loads(__course_expected_artifacts)

def snapshot():
    files = {}
    for root, _, names in os.walk(workspace):
        for name in names:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, workspace)
            with open(path, "rb") as handle:
                files[rel] = hashlib.sha256(handle.read()).hexdigest()
    return files

before = snapshot()

stdout = io.StringIO()
stderr = io.StringIO()
exit_code = 0
results = []
os.chdir(workspace)
sys.path.insert(0, workspace)

for command in commands:
    parts = shlex.split(command)
    if len(parts) < 2 or parts[0] not in ("python", "python3"):
        exit_code = 126
        stderr.write(f"浏览器沙箱只支持 python3 命令：{command}\\n")
        break
    script, args = parts[1], parts[2:]
    source = open(script, encoding="utf-8").read()
    if "import subprocess" in source or "from subprocess" in source:
        exit_code = 125
        stderr.write("该脚本依赖 subprocess，浏览器 WebAssembly 环境不能启动子进程。\\n")
        break
    old_argv = sys.argv[:]
    sys.argv = [script, *args]
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            runpy.run_path(script, run_name="__main__")
        results.append({"command": command, "exit_code": 0})
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
        results.append({"command": command, "exit_code": code})
        if code != 0:
            exit_code = code
            break
    except Exception:
        exit_code = 1
        traceback.print_exc(file=stderr)
        results.append({"command": command, "exit_code": 1})
        break
    finally:
        sys.argv = old_argv

after = snapshot()
changed = []
for root, _, files in os.walk(workspace):
    for name in files:
        path = os.path.join(root, name)
        rel = os.path.relpath(path, workspace)
        if before.get(rel) == after.get(rel):
            continue
        item = {"path": rel, "bytes": os.path.getsize(path), "change": "updated" if rel in before else "created"}
        if item["bytes"] <= 100000:
            try:
                item["content"] = open(path, encoding="utf-8").read()
            except Exception:
                pass
        changed.append(item)

artifact_checks = [
    {"path": path, "exists": path in after, "changed": path in after and before.get(path) != after.get(path)}
    for path in expected_artifacts
]

json.dumps({
    "exit_code": exit_code,
    "stdout": stdout.getvalue(),
    "stderr": stderr.getvalue(),
    "commands": results,
    "changed": changed[:50],
    "artifact_checks": artifact_checks,
    "evidence_boundary": "fixture-tested browser execution; not a real model, enterprise integration, or production run",
})
`;

self.onmessage = async (event) => {
  const { id, spec } = event.data;
  try {
    self.postMessage({ id, type: "progress", message: "正在加载浏览器 Python 环境…" });
    const pyodide = await runtime();
    self.postMessage({ id, type: "progress", message: "正在加载本页已验证材料包…" });
    const response = await fetch(spec.archiveUrl, { cache: "force-cache" });
    if (!response.ok) throw new Error(`材料包加载失败：HTTP ${response.status}`);
    const bytes = new Uint8Array(await response.arrayBuffer());
    const root = `/course-labs/${id}`;
    pyodide.FS.mkdirTree(root);
    pyodide.unpackArchive(bytes, "zip", { extractDir: root });
    const workspace = `${root}/${spec.workingDirectory}`;
    const commands = spec.command.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    pyodide.globals.set("__course_commands", JSON.stringify(commands));
    pyodide.globals.set("__course_workspace", workspace);
    pyodide.globals.set("__course_expected_artifacts", JSON.stringify(spec.expectedArtifacts));
    self.postMessage({ id, type: "progress", message: "正在执行课程夹具…" });
    const raw = await pyodide.runPythonAsync(pythonRunner);
    self.postMessage({ id, type: "result", result: JSON.parse(raw) });
  } catch (error) {
    self.postMessage({ id, type: "error", message: error instanceof Error ? error.message : String(error) });
  }
};
