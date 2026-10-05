import sys
from array import array

KEEP, DELETE, INSERT = "KEEP", "DELETE", "INSERT"


def myers_diff(a, b):
    """Return a minimum edit script turning list a into list b.

    Each operation is a tuple (KEEP | DELETE | INSERT, element).
    """
    n, m = len(a), len(b)
    v = {1: 0}  # V[k] = furthest x reached on diagonal k; V[1] is a sentinel
    trace = []  # trace[d] = compact snapshot of V before round d

    for d in range(n + m + 1):
        # Round d only reads the values round d-1 wrote: keys 1-d, 3-d, ..., d-1
        # (just the sentinel key 1 when d == 0). Store only those, 4 bytes each.
        trace.append(array("i", [v[k] for k in range(1 - d, max(d, 2), 2)]))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                x = v[k + 1]      # move down (INSERT)
            else:
                x = v[k - 1] + 1  # move right (DELETE)
            y = x - k
            while x < n and y < m and a[x] == b[y]:  # snake (KEEP)
                x += 1
                y += 1
            v[k] = x
            if x >= n and y >= m:
                return _backtrack(a, b, trace, d)
    return []


def _backtrack(a, b, trace, d_final):
    """Walk the saved V snapshots from (n, m) back to (0, 0)."""
    x, y = len(a), len(b)
    ops = []

    for d in range(d_final, -1, -1):
        snap = trace[d]
        base = 1 - d  # snap[i] holds V[base + 2 * i]
        k = x - y
        if k == -d or (
            k != d and snap[(k - 1 - base) // 2] < snap[(k + 1 - base) // 2]
        ):
            prev_k = k + 1  # arrived by moving down
        else:
            prev_k = k - 1  # arrived by moving right
        prev_x = snap[(prev_k - base) // 2]
        prev_y = prev_x - prev_k

        while x > prev_x and y > prev_y:  # undo the snake
            ops.append((KEEP, a[x - 1]))
            x -= 1
            y -= 1

        if d > 0:
            if x == prev_x:
                ops.append((INSERT, b[prev_y]))
            else:
                ops.append((DELETE, a[prev_x]))
        x, y = prev_x, prev_y

    ops.reverse()
    return ops


def read_lines(path: str) -> list[bytes]:
    """Read a file as raw bytes and split it into logical lines.

    Only b"\\n" ends a line and it is not part of the line, so a "\\r" before it
    stays in the line. An empty file gives [], and an empty piece after the
    final "\\n" is dropped.
    """
    with open(path, "rb") as f:
        data = f.read()
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def format_ranges(ranges: list[tuple[int, int]]) -> bytes:
    """Format ranges as start-end,start-end (no spaces), or "." if empty.

    The ranges passed in are inclusive (start, last). The official output is
    half-open [start, end), so the printed end is last + 1.
    """
    if not ranges:
        return b"."
    return ",".join(f"{s}-{e + 1}" for s, e in ranges).encode("ascii")


def format_lines(ops, highlight: bool = False) -> bytes:
    """Turn Myers operations into the Part A listing, as raw bytes.

    Inside each change block (DELETE/INSERT operations with no KEEP between
    them) all DELETE lines come first, then all INSERT lines. With highlight,
    the k-th INSERT is paired with the k-th DELETE and followed by a "?" line.
    """
    out = []
    pending_deletes = []
    pending_inserts = []

    def flush():
        for line in pending_deletes:
            out.append(b"-" + line + b"\n")
        for k, line in enumerate(pending_inserts):
            out.append(b"+" + line + b"\n")
            if highlight and k < len(pending_deletes):
                old_r, new_r = char_ranges(pending_deletes[k], line)
                out.append(
                    b"? " + format_ranges(old_r) + b" | " + format_ranges(new_r) + b"\n"
                )
        pending_deletes.clear()
        pending_inserts.clear()

    for op, line in ops:
        if op == DELETE:
            pending_deletes.append(line)
        elif op == INSERT:
            pending_inserts.append(line)
        else:  # KEEP ends the current change block
            flush()
            out.append(b" " + line + b"\n")
    flush()  # the last block has no KEEP after it
    return b"".join(out)


def _to_ranges(indices: list[int]) -> list[tuple[int, int]]:
    """Merge sorted indices into inclusive (start, end) ranges."""
    ranges = []
    for idx in indices:
        if ranges and idx == ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], idx)
        else:
            ranges.append((idx, idx))
    return ranges


def char_ranges(old: bytes, new: bytes):
    """Minimum changed character ranges between two valid UTF-8 lines.

    Characters are Unicode code points counted from 0. Returns
    (old_ranges, new_ranges), each a list of inclusive (start, end) tuples;
    an empty list means that side has no changed characters.
    """
    old_chars = list(old.decode("utf-8"))
    new_chars = list(new.decode("utf-8"))
    old_marked = []
    new_marked = []
    i = j = 0
    for op, _ in myers_diff(old_chars, new_chars):
        if op == DELETE:
            old_marked.append(i)
            i += 1
        elif op == INSERT:
            new_marked.append(j)
            j += 1
        else:  # KEEP
            i += 1
            j += 1
    return _to_ranges(old_marked), _to_ranges(new_marked)


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]
    try:
        a_lines = read_lines(a_path)
        b_lines = read_lines(b_path)
    except OSError as e:
        print(f"error: cannot read file: {e}", file=sys.stderr)
        return 2
    ops = myers_diff(a_lines, b_lines)
    sys.stdout.buffer.write(format_lines(ops, highlight=(command == "highlight")))
    sys.stdout.buffer.flush()
    return 0


raise SystemExit(main())
