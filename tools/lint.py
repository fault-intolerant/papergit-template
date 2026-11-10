"""检查 Markdown 文件中的公式写法，保证 GitHub 能渲染。

规则：
1. 公式只用 LaTeX：不允许 ²、→、≫、α 这类 Unicode 数学字符（代码中除外）。
2. 单独一行的公式：`$$` 必须位于行首，前后各空一行。
3. 行内公式的 `$` 必须成对，`$` 内侧不能紧挨空格。
4. 行内公式开头的 `$` 前面只能是行首、空格或 ASCII 标点。
   紧挨汉字、全角标点（，：（ 等）或字母时，GitHub 不渲染，例如 `，$x$` 要写成 `， $x$`。

用法：python3 tools/lint.py [--fix] [文件 ...]   不给文件时检查仓库中全部 .md 文件。
--fix 自动在这类 `$` 前补一个空格。
"""

import re
import subprocess
import sys
from pathlib import Path

# Unicode 字符 -> 建议的 LaTeX 写法
SUGGEST = {
    "→": r"\to", "←": r"\leftarrow", "↔": r"\leftrightarrow", "⇒": r"\Rightarrow",
    "⇐": r"\Leftarrow", "⇔": r"\Leftrightarrow", "↑": r"\uparrow", "↓": r"\downarrow",
    "≫": r"\gg", "≪": r"\ll", "≤": r"\le", "≥": r"\ge", "≠": r"\neq", "≈": r"\approx",
    "≃": r"\simeq", "≡": r"\equiv", "∼": r"\sim", "∝": r"\propto", "∞": r"\infty",
    "∑": r"\sum", "∏": r"\prod", "∫": r"\int", "∂": r"\partial", "∇": r"\nabla",
    "√": r"\sqrt{}", "±": r"\pm", "∓": r"\mp", "×": r"\times", "÷": r"\div",
    "ħ": r"\hbar", "∈": r"\in", "∉": r"\notin", "⊂": r"\subset", "⊃": r"\supset",
    "∪": r"\cup", "∩": r"\cap", "∀": r"\forall", "∃": r"\exists", "⟨": r"\langle",
    "⟩": r"\rangle", "†": r"^\dagger", "⊗": r"\otimes", "⊕": r"\oplus", "°": r"^\circ",
}
SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ"
SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓᵢⱼₖₙₘ"
for ch in SUPERSCRIPTS:
    SUGGEST[ch] = "^{...}"
for ch in SUBSCRIPTS:
    SUGGEST[ch] = "_{...}"


def suggestion(ch):
    if ch in SUGGEST:
        return SUGGEST[ch]
    if "Ͱ" <= ch <= "Ͽ":
        return r"\alpha、\Gamma 等"
    return None


def forbidden(ch):
    return suggestion(ch) is not None


def strip_code(lines):
    """把代码块和行内代码替换为空白，保留行号。"""
    out, in_fence = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else re.sub(r"`[^`]*`", "", line))
    return out


def check_unicode(text_lines, errors, where):
    for i, line in enumerate(text_lines, 1):
        for ch in sorted(set(c for c in line if forbidden(c))):
            errors.append(f"{where}:{i}: Unicode 数学字符 '{ch}'，改用 LaTeX：${suggestion(ch)}$")


INLINE = re.compile(r"(?<!\\)\$([^$]+)\$")


def bad_before(ch):
    """行内公式开头的 $ 前面是否为 GitHub 不接受的字符。"""
    return ch.isalnum() or ord(ch) > 127


def fix_markdown(path):
    """在紧挨汉字、全角标点或字母的行内公式前补空格。返回修改的处数。"""
    text = path.read_text(encoding="utf-8")
    out, in_fence, count = [], False, 0
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if in_fence or "$$" in line or line.lstrip().startswith("```"):
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)
        for k in range(0, len(parts), 2):
            def add_space(m, seg=parts[k]):
                nonlocal count
                if m.start() > 0 and bad_before(seg[m.start() - 1]):
                    count += 1
                    return " " + m.group(0)
                return m.group(0)
            parts[k] = INLINE.sub(add_space, parts[k])
        out.append("".join(parts))
    if count:
        path.write_text("\n".join(out), encoding="utf-8")
    return count


def check_markdown(path):
    errors = []
    lines = strip_code(path.read_text(encoding="utf-8").splitlines())
    check_unicode(lines, errors, path)

    in_display = False
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        prev = lines[i - 2].strip() if i > 1 else ""
        nxt = lines[i].strip() if i < len(lines) else ""
        if line.startswith(">"):
            line = line.lstrip("> ").strip()
            prev = prev.lstrip("> ").strip() if prev.startswith(">") else prev
            nxt = nxt.lstrip("> ").strip() if nxt.startswith(">") else nxt

        if "$$" in line:
            if not in_display and not line.startswith("$$"):
                errors.append(f"{path}:{i}: 单独一行的公式，$$ 要放在行首")
            opens = not in_display
            closes = line.count("$$") == 2 if opens else True
            if opens and prev:
                errors.append(f"{path}:{i}: $$ 公式前要空一行")
            if closes and nxt:
                errors.append(f"{path}:{i}: $$ 公式后要空一行")
            in_display = opens and not closes
            continue
        if in_display:
            continue

        body = line.replace(r"\$", "")
        if body.count("$") % 2:
            errors.append(f"{path}:{i}: 行内公式的 $ 不成对")
            continue
        for m in INLINE.finditer(body):
            if m.group(1) != m.group(1).strip():
                errors.append(f"{path}:{i}: 行内公式 ${m.group(1)}$ 的 $ 内侧不能有空格")
            if m.start() > 0 and bad_before(body[m.start() - 1]):
                errors.append(f"{path}:{i}: 行内公式 ${m.group(1)}$ 前面紧挨着「{body[m.start() - 1]}」，"
                              "GitHub 不会渲染，在 $ 前加一个空格（可运行 python3 tools/lint.py --fix）")
    if in_display:
        errors.append(f"{path}: 有 $$ 公式没有闭合")
    return errors


def markdown_files():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
                             capture_output=True, text=True, check=True).stdout.split()
        return [Path(f) for f in out if Path(f).exists()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return sorted(Path(".").rglob("*.md"))


def main(argv):
    fix = "--fix" in argv
    argv = [a for a in argv if a != "--fix"]
    files = [Path(a) for a in argv if a.endswith(".md")] if argv else markdown_files()
    if fix:
        for f in files:
            n = fix_markdown(f)
            if n:
                print(f"{f}: 补了 {n} 处空格")
    errors = [e for f in files for e in check_markdown(f)]
    for e in errors:
        print(e)
    if errors:
        print(f"\n{len(errors)} 处公式写法需要修改。规则见 GUIDE.md 的「公式与格式检查」一节。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
