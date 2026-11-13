"""Which music variant to build. VARIANT=v2 (default) or VARIANT=v3.

Each variant has its own song, stems, mixes and timeline; the voice lines and visuals are shared.
v2 keeps its files where they were first made, so earlier renders stay reproducible.
"""
import os
from pathlib import Path

HERE = Path(__file__).parent
V = os.environ.get("VARIANT", "v2")
AUDIO = HERE / "assets" / "audio" if V == "v2" else HERE / "assets" / "audio" / V
TIMELINE = HERE / ("timeline.json" if V == "v2" else f"timeline-{V}.json")
