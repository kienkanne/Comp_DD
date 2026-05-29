from dataclasses import dataclass
from pathlib import Path

from nexus.dock.utils.matchmixer import matchmixer


@dataclass(frozen=True)
class DummyRecBundle:
    receptor: Path
    vina_config: Path
    name: str


def test_matchmixer_mix_with_receptor_bundles():
    recs = [
        DummyRecBundle(Path("rec1_prepped.pdbqt"), Path("rec1_config.txt"), "rec1"),
        DummyRecBundle(Path("rec2_prepped.pdbqt"), Path("rec2_config.txt"), "rec2"),
    ]
    ligs = [Path("ligA_prepped.pdbqt"), Path("ligB_prepped.pdbqt")]

    pairs = matchmixer(recs, ligs)

    assert len(pairs) == 4
    assert pairs[0] == (recs[0], ligs[0])
    assert pairs[-1] == (recs[1], ligs[1])
