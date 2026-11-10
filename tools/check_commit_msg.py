"""检查提交信息的格式。由 .githooks/commit-msg 调用。

第一行：<类型>(<论断编号>): <确立了什么>，或 setup: <说明>
类型：check derive deadend errata notation fix
deadend 的正文必须写错因。
公式写成 LaTeX 源码，如 4t^2/U，不用 ²、→ 这类字符。
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lint import forbidden, suggestion  # noqa: E402

SUBJECT = re.compile(r"^(?:(check|derive|deadend|errata|notation|fix)\([^()\s]+\)|setup): \S")
EXEMPT = ("Merge ", "Revert ", "Initial commit", "fixup! ", "squash! ")


def check(message):
    lines = [l for l in message.splitlines() if not l.startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return ["提交信息为空"]
    subject = lines[0]
    if subject.startswith(EXEMPT):
        return []

    errors = []
    m = SUBJECT.match(subject)
    if not m:
        errors.append("第一行格式应为 <类型>(<论断编号>): <确立了什么>，例如 derive(eq12): 计入两个中间态，得到 4t^2/U\n"
                      "  类型：check derive deadend errata notation fix；整理仓库用 setup: <说明>")
    if m and m.group(1) == "deadend" and "错因" not in message:
        errors.append("deadend 提交的正文要写一行「错因：……」")
    if subject.strip().lower() in ("update", "fix", "wip"):
        errors.append("第一行要写明这一步确立了什么")
    for ch in sorted(set(c for c in message if forbidden(c))):
        errors.append(f"Unicode 数学字符 '{ch}'，提交信息中写 LaTeX 源码：{suggestion(ch)}")
    return errors


def main():
    errors = check(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for e in errors:
        print("提交信息：" + e)
    if errors:
        print("提交已取消，原信息保存在 .git/COMMIT_EDITMSG。格式见 GUIDE.md 附录。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
