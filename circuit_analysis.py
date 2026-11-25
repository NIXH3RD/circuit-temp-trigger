"""
DC Circuit Analysis (Modified Nodal Analysis) + node graph + verification.

Requirements: pip install numpy networkx matplotlib

Netlist format: (name, type, node1, node2, value)
  R : resistor, ohms
  V : voltage source, volts, node1 is the + terminal
  I : current source, amps, current flows node1 -> node2 INSIDE the source
Ground node is "0".
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# ---------------- Edit your circuit here ----------------
NETLIST = [
    ("V1", "V", "1", "0", 10.0),     # 10 V
    ("R1", "R", "1", "2", 1000.0),   # 1 kOhm
    ("R2", "R", "2", "0", 2000.0),   # 2 kOhm
    ("R3", "R", "2", "3", 1000.0),   # 1 kOhm
    ("R4", "R", "3", "0", 2000.0),   # 2 kOhm
    ("I1", "I", "0", "3", 0.002),    # 2 mA pushed into node 3
]
# --------------------------------------------------------


def solve(netlist):
    nodes = sorted({n for _, _, a, b, _ in netlist for n in (a, b)} - {"0"})
    idx = {n: i for i, n in enumerate(nodes)}
    vsrc = [c for c in netlist if c[1] == "V"]
    N, M = len(nodes), len(vsrc)
    A = np.zeros((N + M, N + M))
    b = np.zeros(N + M)

    for name, typ, n1, n2, val in netlist:
        i1, i2 = idx.get(n1), idx.get(n2)
        if typ == "R":
            g = 1.0 / val
            for p, q, s in ((i1, i1, 1), (i2, i2, 1), (i1, i2, -1), (i2, i1, -1)):
                if p is not None and q is not None:
                    A[p, q] += s * g
        elif typ == "I":
            if i1 is not None:
                b[i1] -= val
            if i2 is not None:
                b[i2] += val
    for k, (name, _, n1, n2, val) in enumerate(vsrc):
        row = N + k
        for n, s in ((n1, 1), (n2, -1)):
            if n in idx:
                A[idx[n], row] += s
                A[row, idx[n]] += s
        b[row] = val

    x = np.linalg.solve(A, b)
    v = {"0": 0.0, **{n: x[idx[n]] for n in nodes}}
    ivs = {c[0]: x[N + k] for k, c in enumerate(vsrc)}  # current into + terminal
    return v, ivs


def element_results(netlist, v, ivs):
    res = {}
    for name, typ, n1, n2, val in netlist:
        vd = v[n1] - v[n2]
        if typ == "R":
            i = vd / val
        elif typ == "I":
            i = val
        else:
            i = ivs[name]
        res[name] = dict(type=typ, V=vd, I=i, P_abs=vd * i)  # P>0 absorbed
    return res


def verify(netlist, v, res):
    print("\n--- KCL check (sum of currents leaving each node) ---")
    for n in [n for n in v if n != "0"]:
        total = 0.0
        for name, typ, a, b_, _ in netlist:
            if a == n:
                total += res[name]["I"]
            elif b_ == n:
                total -= res[name]["I"]
        print(f"Node {n}: {total:+.3e} A")
    p_sum = sum(r["P_abs"] for r in res.values())
    print(f"\n--- Power balance ---\nSum of absorbed power = {p_sum:+.3e} W (should be ~0)")


def draw_graph(netlist, v, res, filename="circuit_graph.png"):
    G = nx.MultiGraph()
    for name, typ, a, b_, val in netlist:
        G.add_edge(a, b_, key=name)
    pos = nx.spring_layout(G, seed=3)
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {"R": "tab:blue", "V": "tab:red", "I": "tab:green"}
    for k, (name, typ, a, b_, val) in enumerate(netlist):
        (x1, y1), (x2, y2) = pos[a], pos[b_]
        rad = 0.15 * (k % 3 - 1)
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=colors[typ],
                                    connectionstyle=f"arc3,rad={rad}", lw=2))
        unit = {"R": "Ω", "V": "V", "I": "A"}[typ]
        r = res[name]
        ax.text((x1 + x2) / 2 + rad * (y2 - y1) * 0.6,
                (y1 + y2) / 2 - rad * (x2 - x1) * 0.6,
                f"{name}={val:g}{unit}\nI={r['I']*1e3:.3f} mA",
                fontsize=8, ha="center",
                bbox=dict(fc="white", ec=colors[typ], alpha=0.9))
    nx.draw_networkx_nodes(G, pos, node_size=900, node_color="lightyellow",
                           edgecolors="black", ax=ax)
    nx.draw_networkx_labels(G, pos, {n: f"{n}\n{v[n]:.3f}V" for n in G.nodes}, font_size=8, ax=ax)
    ax.set_title("Circuit node graph (arrow = reference current direction)")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"\nSaved graph: {filename}")
    plt.show()


if __name__ == "__main__":
    v, ivs = solve(NETLIST)
    res = element_results(NETLIST, v, ivs)

    print("--- Node voltages (ground = 0) ---")
    for n, val in v.items():
        print(f"V({n}) = {val:.4f} V")

    print("\n--- Element results (V = V(n1)-V(n2), I = n1 -> n2) ---")
    for name, r in res.items():
        state = "absorbs" if r["P_abs"] >= 0 else "delivers"
        print(f"{name}: V={r['V']:+.4f} V, I={r['I']*1e3:+.4f} mA, "
              f"P={abs(r['P_abs'])*1e3:.4f} mW ({state})")

    verify(NETLIST, v, res)
    draw_graph(NETLIST, v, res)
