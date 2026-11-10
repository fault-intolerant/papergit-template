"""检验 eq12：两格点 Hubbard 模型的超交换 J = 4t²/U。

参照：两格点精确对角化得到的单态–三重态能隙。
J 是 t/U → 0 的领头项，与精确能隙只在极限下一致，
所以不用固定容差比较，而是检查相对偏差随 (t/U)² 减小。
"""

import numpy as np

# 推导得到的公式，见 derivation.md
def J_derived(t, U):
    return 4 * t**2 / U


# ---------- 精确对角化 ----------

# 模式编号：0 = (1,↑)，1 = (1,↓)，2 = (2,↑)，3 = (2,↓)
N_MODES = 4


def annihilation(j):
    """Jordan–Wigner 表示下的湮灭算符 c_j，作用在 2^4 维 Fock 空间上。"""
    a = np.array([[0.0, 1.0], [0.0, 0.0]])  # |0><1|
    z = np.diag([1.0, -1.0])                # 费米符号
    eye = np.eye(2)
    op = np.array([[1.0]])
    for k in range(N_MODES):
        op = np.kron(op, z if k < j else a if k == j else eye)
    return op


c = [annihilation(j) for j in range(N_MODES)]
cd = [m.T for m in c]
n = [cd[j] @ c[j] for j in range(N_MODES)]


def hamiltonian(t, U):
    hop = sum(cd[i] @ c[j] + cd[j] @ c[i] for i, j in [(0, 2), (1, 3)])
    return -t * hop + U * (n[0] @ n[1] + n[2] @ n[3])


def spin_squared():
    sz = 0.5 * (n[0] - n[1] + n[2] - n[3])
    sp = cd[0] @ c[1] + cd[2] @ c[3]
    return sp @ sp.T + sz @ sz - sz


def singlet_triplet_gap(t, U):
    """半满（两个电子）子空间中，最低三重态与最低单态的能量差。"""
    N = sum(n)
    keep = np.isclose(np.diag(N), 2)
    H = hamiltonian(t, U)[np.ix_(keep, keep)]
    S2 = spin_squared()[np.ix_(keep, keep)]
    E, V = np.linalg.eigh(H)
    s2 = np.einsum("ik,ij,jk->k", V, S2, V)   # 每个本征态的 S(S+1)
    E_singlet = E[np.isclose(s2, 0)].min()
    E_triplet = E[np.isclose(s2, 2)].min()
    return E_triplet - E_singlet


# ---------- 检验 ----------

U = 1.7                       # 避开 1，否则 4t/U 与 4t²/U 无法区分
RATIOS = [0.04, 0.02, 0.01]   # t/U


def agrees_with_exact(J):
    """J 是否为精确能隙的领头项：相对偏差小，且按 (t/U)² 减小。"""
    rel = np.array([singlet_triplet_gap(r * U, U) / J(r * U, U) - 1 for r in RATIOS])
    if not np.all(np.isfinite(rel)) or abs(rel[-1]) > 0.01:
        return False
    slope = np.polyfit(np.log(RATIOS), np.log(np.abs(rel)), 1)[0]
    return abs(slope - 2) < 0.1


def test_eq12():
    assert agrees_with_exact(J_derived)


# 检验本身的检验：常见的错误都应当被抓住
MUTANTS = {
    "因子 2（只计一个中间态）": lambda t, U: 2 * t**2 / U,
    "因子 2（多算）": lambda t, U: 8 * t**2 / U,
    "符号": lambda t, U: -4 * t**2 / U,
    "t 的幂次": lambda t, U: 4 * t / U,
    "U 的幂次": lambda t, U: 4 * t**2 / U**2,
}


def test_mutations():
    caught = {name: not agrees_with_exact(J) for name, J in MUTANTS.items()}
    missed = [name for name, ok in caught.items() if not ok]
    assert not missed, f"检验没有抓住：{missed}"
