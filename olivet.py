import subprocess
from pathlib import Path

# home = Path("/tmp/olivet/Olivet Bible/Worship/Music")
home = Path("/mnt/nas/dump/Olivet Bible/Worship/Music")

target = Path("/home/nic/olivet-music")
# target = Path(home.parent, "instrumental-nic")

for m in home.glob("**/*.mp3"):
    _path = Path(target, m.relative_to(home))
    # p = subprocess.Popen(f"python inference.py --input {m} --tta --gpu 0", shell=True)
    p = subprocess.Popen(
        [
            "python",
            "inference.py",
            "--input",
            str(m),
            "--output_dir",
            str(_path.parent),
            "--tta",
            "--gpu",
            "0",
            "--postprocess",
        ]
    )
    p.wait()
