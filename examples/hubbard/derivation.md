# eq12：超交换 $J = 4t^2/U$

论文称此式"由二阶微扰直接给出"。
检验：`test_eq12_superexchange.py`。

## 出发点

两格点 Hubbard 模型

$$H = -t\sum_{\sigma}\left(c_{1\sigma}^\dagger c_{2\sigma} + c_{2\sigma}^\dagger c_{1\sigma}\right) + U\sum_{i} n_{i\uparrow} n_{i\downarrow}.$$

半满，两个电子， $U \gg t$。
把跳跃项记为 $T$，相互作用项作为 $H_0$。

## 低能子空间与中间态

每个格点各有一个电子的四个态能量为 $0$，构成低能子空间 $P$。
其中有一个单态 $|S\rangle = (|{\uparrow},{\downarrow}\rangle - |{\downarrow},{\uparrow}\rangle)/\sqrt{2}$ 和三个三重态。
$T$ 把它们连到双占据态 $|D_1\rangle = |{\uparrow\downarrow},0\rangle$ 和 $|D_2\rangle = |0,{\uparrow\downarrow}\rangle$，能量为 $U$。

二阶有效哈密顿量为

$$H_\mathrm{eff} = -\frac{1}{U}\, P\, T\, (1-P)\, T\, P.$$

## 死路：只计入一个中间态

> deadend：只考虑电子从格点 2 跳到格点 1，得到 $|D_1\rangle$。
> $|\langle D_1|T|S\rangle|^2 = 2t^2$，单态能量移动 $-2t^2/U$。
> 三重态与 $|D_1\rangle$ 的矩阵元为零，能量不变。
> 能隙为 $2t^2/U$，检验失败：精确能隙与它的比值趋于 $2$。
>
> 错因：电子也可以从格点 1 跳到格点 2，得到 $|D_2\rangle$，这一项漏掉了。
> 当时以为两个方向的跳跃是同一个过程。

## 计入两个中间态

单态到两个双占据态的矩阵元大小相同， $|\langle D_i|T|S\rangle|^2 = 2t^2$。
两项相加，单态能量移动 $-4t^2/U$。
对三重态，两个自旋构型的跳跃振幅相消，这是 Pauli 原理的结果，三重态能量仍为 $0$。

单态–三重态能隙为

$$J = \frac{4t^2}{U}.$$

检验通过：相对偏差随 $(t/U)^2$ 减小。

## 遗留问题

$t^4/U^3$ 阶修正的符号是什么？
开为下一个 issue。
