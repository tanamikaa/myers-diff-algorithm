KEEP, DELETE, INSERT = "KEEP", "DELETE", "INSERT"


def myers_diff(a, b):
    """Return a minimum edit script turning list a into list b.

    Each operation is a tuple (KEEP | DELETE | INSERT, element).
    """
    n, m = len(a), len(b)
    v = {1: 0}  # V[k] = furthest x reached on diagonal k; V[1] is a sentinel
    trace = []  # trace[d] = copy of V before round d

    for d in range(n + m + 1):
        trace.append(v.copy())
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
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v[k - 1] < v[k + 1]):
            prev_k = k + 1  # arrived by moving down
        else:
            prev_k = k - 1  # arrived by moving right
        prev_x = v[prev_k]
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
