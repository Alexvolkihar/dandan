"""Print how HarfBuzz shapes text with a built font: python scripts/shape.py FONT TEXT [features]."""

import sys

import uharfbuzz as hb


def shape(path: str, text: str, features: dict[str, bool] | None = None) -> list[tuple[int, int]]:
    blob = hb.Blob.from_file_path(path)
    font = hb.Font(hb.Face(blob))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    return [(info.codepoint, info.cluster) for info in buf.glyph_infos]


if __name__ == "__main__":
    feats = {f.lstrip("-+"): not f.startswith("-") for f in sys.argv[3:]}
    print(shape(sys.argv[1], sys.argv[2], feats))
