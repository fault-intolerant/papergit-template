# 给 AI 助手的说明

这个仓库用来读一篇物理论文，做法见 GUIDE.md。
学生负责推导和判断，AI 助手负责 Git 和 GitHub 的操作、检验脚本的样板代码，以及审阅。
回答学生时用中文。

## 初始化

每次会话开始时确认两件事：

1. `gh auth status` 显示已登录。
   未登录时，请学生在自己的终端运行 `gh auth login`，选择 GitHub.com、HTTPS、用浏览器登录，并在问到是否用 GitHub 凭据认证 Git 时选 Yes。
   登录由学生自己完成；不要索取、输入或保存密码和令牌。
2. `git config core.hooksPath` 的输出是 `.githooks`。
   不是时运行 `sh tools/setup.sh`（Windows 上依次运行其中的命令）。

检验用仓库中的虚拟环境运行：`.venv/bin/python -m pytest`（Windows 上是 `.venv\Scripts\python -m pytest`）。

## 不做的事

- 不写 `derivations/` 中的推导，也不直接给出推导步骤的答案。
  学生卡住时，可以指出出错的位置、提出问题、建议一个更小的检验情形。
- 不改写历史：不用 `git commit --amend`（尚未推送的提交除外）、`git rebase`、`git push --force`、squash 合并。
  deadend 提交必须保留。
- 不用 `--no-verify` 跳过检查。检查不通过时，修改内容后重新提交。
- 不替学生决定论断的状态，也不替学生写 deadend 的错因；请学生口述，再整理成文字。

## issue

学生提出一个"易证"的步骤时，用 gap 模板的格式开 issue：

```bash
gh issue create --title "[gap] Eq.(12) \$J = 4t^2/U\$" --body-file <临时文件>
```

正文包含五项：论文怎么说、出发点、目标、验收标准、预计用时。
验收标准由学生给出；学生说不清时，帮学生把问题拆小，不要替学生编。

## 提交

- 一个逻辑步一个提交，提交前运行 `git status` 和 `git diff`，把改动念给学生确认。
- 提交信息的第一行：`<类型>(<论断编号>): <确立了什么>`。
  类型：`check`、`derive`、`deadend`、`errata`、`notation`、`fix`；整理仓库用 `setup: <说明>`。
- 正文写 `How:`、`Check:`、`Refs: #<issue 号>`；deadend 另写 `错因：`。
- AI 参与过的提交，末尾加 `Assisted-by: <工具名>`。
- 提交后运行 `git push`。
- deadend 提交的检验是失败的，GitHub 上显示红叉，这是正常的记录，不要为了消除红叉而修改它。

## 写作格式

- Markdown 中的公式只用 LaTeX：行内 `$4t^2/U$`，单独一行用 `$$...$$` 并前后空行。
  不用 `²`、`→`、`≫`、`α` 这类 Unicode 字符。提交前运行 `python3 tools/lint.py`。
- 提交信息中的公式写 LaTeX 源码，如 `4t^2/U`。
- 推导文件一句一行。
- 检验放在 `checks/`，文件名以 `test_` 开头。
  每个检验都要配一个 `test_mutations`：把结果改错一个因子 2、一个符号、一个幂次，确认检验失败。参考 `examples/hubbard/test_eq12_superexchange.py`。
  检验点不用 0、1 这类特殊值。

## 检验通过之后

1. 在 `CLAIMS.md` 中把论断改为"已验证"，并填上检验文件和 issue 号。
2. 请学生说一句教训，用 `gh issue close <号> --comment "<教训>"` 关闭 issue。
3. 更新 `README.md` 中的进度。

## 和同伴协作时

每个 issue 开一个分支 `<issue 号>-<简称>`，检验通过后用 `gh pr create` 开 PR，合并用 `gh pr merge --merge`。
