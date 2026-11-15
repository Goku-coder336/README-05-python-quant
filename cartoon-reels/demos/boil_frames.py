"""Write 3 extra "boil" retraces of a finished drawing: same picture, the ink re-traced through a fresh
small wobble each time. Cycling them every 3 frames makes a held drawing look hand-animated.

python3 boil_frames.py oiseau_tombe.py OUT_PREFIX     -> OUT_PREFIX-b1.jpg .. -b3.jpg
"""
import os
import runpy
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/claude-drawing/lib"))
import cartoon  # noqa: E402

script, prefix = sys.argv[1], sys.argv[2]
_save = cartoon.Cartoon.save


def save(self, path, stages_dir=None, quality=88):
    n = len(self.stages)
    for k in range(1, 4):
        self.composite(None, None, boil=n + 10 + k).convert("RGB").save(f"{prefix}-b{k}.jpg", quality=86)
    return _save(self, path, None, quality)


cartoon.Cartoon.save = save
sys.argv = [script, "/tmp/boil_final.png"]
runpy.run_path(script, run_name="__main__")
