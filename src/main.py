import sys

from myers_core import DELETE, INSERT, myers_diff


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


def format_lines(ops) -> bytes:
    """Turn Myers operations into the Part A listing, as raw bytes.

    Inside each change block (DELETE/INSERT operations with no KEEP between
    them) all DELETE lines come first, then all INSERT lines.
    """
    out = []
    pending_deletes = []
    pending_inserts = []

    def flush():
        for line in pending_deletes:
            out.append(b"-" + line + b"\n")
        for line in pending_inserts:
            out.append(b"+" + line + b"\n")
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
    if command == "highlight":
        print("error: highlight is not implemented yet", file=sys.stderr)
        return 2
    ops = myers_diff(a_lines, b_lines)
    sys.stdout.buffer.write(format_lines(ops))
    sys.stdout.buffer.flush()
    return 0


raise SystemExit(main())
