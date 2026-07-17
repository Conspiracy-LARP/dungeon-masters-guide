"""Generate the Ceefax mock as authentic Mode 7.

Teletext drew graphics with **block mosaics**: each character cell is split into a 2x3
grid of blocks, and a cell is one colour. That constraint is the whole look. Approximating
it with smooth shapes produces something that reads as "retro" rather than as Ceefax, and a
reader who grew up with it feels the wrong note without being able to name it.

The grid is 40x25 cells (`COLS` x `ROWS`), so the mosaic canvas is 80x75 blocks. Art is
authored as strings on that canvas and emitted as `<rect>`s, cell-aligned, because that is
what the hardware could actually do.

Run: `python -m build.artgen.ceefax > src/pack/ceefax-274.svg`. The output is committed;
this module exists so the next artifact is authored rather than hand-typed.
"""

from __future__ import annotations

COLS, ROWS = 40, 25
W, H = 640, 500
CW, CH = W / COLS, H / ROWS
BW, BH = CW / 2, CH / 3

WHITE, YELLOW, CYAN, GREEN, RED, MAGENTA = (
    "#ffffff",
    "#ffff00",
    "#00ffff",
    "#00ff00",
    "#ff0000",
    "#ff00ff",
)

#: A closed eye, drawn on the block grid. Thematic: the page is about eye strain, and the
#: Directorate would have chosen it for exactly that reason and not noticed the joke.
EYE = [
    "......########......",
    "....############....",
    "..####........####..",
    ".###....####....###.",
    "##....########....##",
    "##...##########...##",
    "##....########....##",
    ".###....####....###.",
    "..####........####..",
    "....############....",
    "......########......",
]


def mosaic(art: list[str], ox: int, oy: int, colour: str) -> str:
    """Emit `art` as block rects, with its top-left block at (`ox`, `oy`)."""
    out = []
    for row, line in enumerate(art):
        for col, ch in enumerate(line):
            if ch != "#":
                continue
            x = (ox + col) * BW
            y = (oy + row) * BH
            out.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{BW:.2f}" height="{BH:.2f}" fill="{colour}"/>'
            )
    return "\n    ".join(out)


def bar(row: int, colour: str, cols: range | None = None) -> str:
    """A solid mosaic bar across `cols` of a character row: Ceefax's favourite furniture."""
    span = cols if cols is not None else range(COLS)
    return mosaic(["#" * (len(span) * 2)] * 3, span.start * 2, row * 3, colour)


def cell_text(col: int, row: int, text: str, colour: str, double: bool = False) -> str:
    """Text on the character grid. Baseline sits where Mode 7 put it."""
    size = 39 if double else 19.5
    dy = CH * 1.62 if double else CH * 0.78
    return (
        f'<text x="{col * CW:.1f}" y="{row * CH + dy:.1f}" fill="{colour}" '
        f'font-size="{size}" letter-spacing="{3 if double else 1.6}">{text}</text>'
    )


def render() -> str:
    parts = [
        cell_text(1, 0, "P274", WHITE),
        cell_text(7, 0, "CEEFAX 274", CYAN),
        cell_text(21, 0, "Mon 14 Oct", WHITE),
        cell_text(32, 0, "20:41/32", GREEN),
        bar(2, RED),
        cell_text(4, 4, "READING AND YOU", YELLOW, double=True),
        bar(7, RED),
        mosaic(EYE, 1, 27, CYAN),
        cell_text(13, 10, "A PUBLIC", CYAN),
        cell_text(13, 11, "INFORMATION", CYAN),
        cell_text(13, 12, "MESSAGE", CYAN),
        cell_text(1, 15, "Doctors now advise that prolonged", WHITE),
        cell_text(1, 16, "reading may contribute to:", WHITE),
        cell_text(4, 18, "eye strain and headache", YELLOW),
        cell_text(4, 19, "poor posture", YELLOW),
        cell_text(4, 20, "disturbed sleep", YELLOW),
        cell_text(4, 21, "nervous exhaustion", YELLOW),
        bar(23, MAGENTA, cols=range(0, 13)),
        bar(23, GREEN, cols=range(13, 26)),
        bar(23, CYAN, cols=range(26, 40)),
        cell_text(1, 24, "Health 275", GREEN),
        cell_text(14, 24, "Sport 300", CYAN),
        cell_text(27, 24, "Index 100", YELLOW),
    ]
    desc = (
        "An invented Ceefax teletext page 274, headed READING AND YOU, carrying a public "
        "information message claiming prolonged reading causes eye strain, poor posture, "
        "disturbed sleep and nervous exhaustion, and advising no more than 20 minutes of "
        "reading an evening. Issued by the fictional Directorate of Reading Standards. "
        "Drawn in Mode 7 block mosaics on a 40x25 grid. No such page was ever broadcast; "
        "this image is a fake, generated to show how easily evidence is manufactured."
    )
    body = "\n    ".join(parts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
     aria-labelledby="t d">
  <title id="t">Fabricated screenshot: a Ceefax page that was never broadcast</title>
  <desc id="d">{desc}</desc>
  <rect width="{W}" height="{H}" fill="#000000"/>
  <g font-family="'Courier New', monospace" font-weight="bold">
    {body}
  </g>
</svg>
"""


if __name__ == "__main__":
    print(render(), end="")
