# 新项目首次启用(Bootstrap)

> 在一个**没有 docs/specs 约定**的项目里首次用本 skill 时,先跑这步把「规格系统」装上;装好后该项目的后续会话自动沿用,无需再 bootstrap。
> 已存在 `docs/specs/INDEX.md` → 跳过本步,直接进主流程。

## 是否需要 bootstrap
- 存在 `docs/specs/INDEX.md` → 已装好,跳过。
- 否则 → 执行下面 1~5。

## 步骤
1. **定位项目根**:`ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || ROOT=$(pwd)`(失败=非 git,退码 128,fallback 当前目录)。monorepo 默认用仓库根,除非用户指定子包。下文路径相对 `$ROOT`。
2. **建目录**:`docs/specs/<需求名>/{source,handoff,notes}`(`mkdir -p`)。
   - **需求名规范**:用短横线 kebab、无空格、无斜杠;中文需求名亦可但须与 INDEX 行、handoff 文件名完全一致。名字默认取 PRD 标题;PRD 有内部代号时以代号为准(防标题改动时目录漂移)。
3. **不进 git(默认,贴合「PRD 不入仓库」偏好)**:
   - git 项目:写 `docs/specs/.gitignore`,内容仅一行 `*`(自忽略整目录、含它自己)。**这是普通文件写入,不碰 `.git/`**,不污染团队 `.gitignore`,**跨平台可用**(命令示例为 POSIX shell;Windows PowerShell 用 `New-Item -ItemType Directory -Force` / `Set-Content` 等价)。**优先用此法**(`.git/info/exclude` 常被沙箱禁写)。
   - 非 git 项目:跳过(无需忽略)。
   - 若该项目希望规格**进 git**(团队共享):**先问用户**;要进 git 就不写这个 `.gitignore`。默认不进 git。
   - **写前先判存在**:`[ -f docs/specs/.gitignore ] || printf '*\n' > docs/specs/.gitignore`;INDEX 同理,存在则只追加当前需求行,不重写(防重跑静默覆盖)。
   - **已被跟踪的例外**:gitignore 只对**未跟踪**文件生效。若 `git ls-files docs/specs/` 非空(此前已 add/commit),写 `.gitignore` 不会让其脱离跟踪——需 `git rm -r --cached docs/specs/` 后再依赖忽略,此操作改索引,**先问用户**。
   - **进/不进 git 何时问**:检测到 remote 且非个人仓库时,当场用 AskUserQuestion 问一次;个人/无 remote 直接默认不进。
4. **建 INDEX**:**复制 `references/index-template.md`** 到 `docs/specs/INDEX.md`(该模板文件已存在,勿自创格式),把当前需求加一行。模板内含:需求总目录表(需求/文件夹/入口/状态)+ 4 类文档约定(SPEC.md / source / handoff / notes)+「新增需求脚手架」步骤(含「PRD/纪要原件先丢 `<需求>/source/`」)。
5. **写项目路由指针(让该项目未来会话自动发现)**——指针放进**运行所在 harness 的「会话启动必读」指令文件**,且**载体与 §3「进/不进 git」一致**(指针进 git 而 specs 不进则自相矛盾)。写任何**跟踪**指令文件前先 `git ls-files --error-unmatch <该文件>` 判,被跟踪=团队文件、默认别动。
   - **先跟 harness 选文件**:Claude Code→`CLAUDE.md`(本地变体 `CLAUDE.local.md` / 项目记忆);Codex→`AGENTS.md`;Gemini→`GEMINI.md`;Copilot→`.github/copilot-instructions.md`;Cursor→`.cursor/rules`。多工具协作优先中立的 `AGENTS.md`(被多家读取)。
   - **specs 不进 git(默认)→ 指针也必须本地、不进 git**:
     - Claude Code:写一条**项目级记忆**(本地、随项目、不入 git)——用现成写记忆机制,**别手拼 `~/.claude/projects/<编码cwd>/memory/` 路径**(编码有损、worktree 隔离,不可靠)。
     - 跨 harness / 想要文件锚点:写 **`CLAUDE.local.md`**(本地覆盖文件;须确认它被 gitignore,否则在本地 exclude 里加一行)。
     - 其它 harness:用其本地变体,无本地变体则把该指令文件 gitignore 后再写。
     - ⛔ **不要把指针写进已被跟踪的指令文件**(`CLAUDE.md` / `AGENTS.md` 等)——会进版本控制、被 push。
   - **specs 进 git(团队共享)→ 写进该 harness 的跟踪指令文件**(`CLAUDE.md` / `AGENTS.md` / …;无则建)。
   - **指针内容(一条,静态)**:本项目一需求一文件夹 `docs/specs/<需求>/`;总目录 `docs/specs/INDEX.md`;源/规格两层,`SPEC.md` 为执行契约;接手任一需求先读其 `SPEC.md §0` + handoff;PM 稿更新丢 source/ 跑 `/prd-to-spec` 折入。
   - **职责分工(防双写漂移)**:指针只存这**一条静态指向**(去 INDEX 找),永不列具体需求;需求清单只在 INDEX。
   - ⚠️ 记忆是 harness 私有、非通用前提;无记忆的环境出 git 用 `CLAUDE.local.md`、进 git 用 `CLAUDE.md`。无写记忆权(子代理、CI)时只写对应文件锚点,不尝试写记忆。

## 之后
该项目任何新会话:经路由指针(该 harness 的指令文件 / 本地变体 / 记忆,视所选载体)即知去 `docs/specs/INDEX.md` 找;或你直接说需求名,按 INDEX 定位读 `SPEC.md §0`。

## 可移植性边界(诚实)
- **skill 本身全局可移植**:任何项目/会话都可用,原则与流程不变。
- **约定脚手架 + 路由指针是项目级**:每个新项目靠本 bootstrap 装一次(一步、可重复;指针首选 CLAUDE.md、记忆可选叠加),装好后「新会话自动知道 PRD 在哪」在该项目内成立。
- 边界处理:`docs/` 已有跟踪内容 → 只新增 `docs/specs/` 子目录、不动 `docs/` 根忽略;monorepo → 放仓库根的 `docs/specs/`(除非用户指定子包);非 git → 只是没有忽略,结构照建。

## 收尾自检(bootstrap 完成前过一遍)
- [ ] `docs/specs/INDEX.md` 存在且由模板生成
- [ ] 路由指针已写入(出 git:记忆 / `CLAUDE.local.md`;进 git:`CLAUDE.md`),且**未**污染被跟踪的 `CLAUDE.md`
- [ ] 当前需求已在 INDEX 登记一行
- [ ] PRD/纪要原件已放入 `<需求>/source/`
- [ ] (git 项目)`git status` 仅显示原始 PRD,`docs/specs/` 被 `*` 忽略
