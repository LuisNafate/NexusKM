"""Create a shareable package from Git's non-ignored project files."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "entrega/NexusKM_entrega.zip"


def main():
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    excluded = {"entrega/NexusKM_entrega.zip", "entrega/SHA256SUMS.txt"}
    paths = sorted({path for path in listed if path and path not in excluded})
    forbidden = {".env", ".git", ".venv", ".runtime", "__pycache__", "node_modules", ".taste-skill"}
    manifest = []
    DESTINATION.parent.mkdir(exist_ok=True)
    with ZipFile(DESTINATION, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in paths:
            path = ROOT / relative
            if not path.is_file():
                continue
            if any(part in forbidden for part in Path(relative).parts):
                raise ValueError("Private or generated file would enter the package.")
            content = path.read_bytes()
            manifest.append({"path": relative, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
            archive.writestr("NexusKM/" + relative, content)
        archive.writestr("NexusKM/MANIFEST-SHA256.json", json.dumps({
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "Project source, documents, evidence and final artifacts; excludes credentials, local dependencies and this archive",
            "files": manifest,
        }, ensure_ascii=False, indent=2) + "\n")
    with ZipFile(DESTINATION) as archive:
        assert archive.testzip() is None
        for record in manifest:
            assert hashlib.sha256(archive.read("NexusKM/" + record["path"])).hexdigest() == record["sha256"]
    artifacts = [ROOT / "entrega" / name for name in (
        "NexusKM_informe_integrado.docx", "NexusKM_informe_integrado.pdf",
        "NexusKM_presentacion_integrada.pptx", "NexusKM_presentacion_integrada.pdf", "NexusKM_entrega.zip",
    )]
    (ROOT / "entrega/SHA256SUMS.txt").write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts
    ), encoding="utf-8", newline="\n")
    print(json.dumps({"archive": str(DESTINATION), "files": len(manifest), "bytes": DESTINATION.stat().st_size}))


if __name__ == "__main__":
    main()
