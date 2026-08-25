# Dao Video Suite 安装与使用

这是一个由三个 Agent Skills 组成的套件：

- `dao-video`：总流程、项目状态、配音、字幕、BGM、发布准备与复盘。
- `dao-blackgold-video`：黑金国风视觉分支。
- `dao-ink-video`：水墨书法视觉分支。

三个目录需要一起安装，目录名不可修改。

## 通用安装方法

1. 解压本压缩包。
2. 找到目标 Agent 支持的 Skills、Extensions、Rules 或能力包管理入口。
3. 将以下三个完整目录导入该入口：

   ```text
   dao-video/
   dao-blackgold-video/
   dao-ink-video/
   ```

4. 重新加载或重启目标 Agent，使其重新扫描技能。
5. 让 Agent 读取 `dao-video/SKILL.md`，再根据风格加载另外一个分支。

不同 Agent 的安装目录和导入命令并不统一。不要默认使用 `~/.codex/skills/`；应以目标 Agent 自己的技能文档或技能管理器为准。若目标 Agent 不原生支持 `SKILL.md`，可将三个 `SKILL.md` 作为项目规则/系统说明导入，并保持 `references/`、`scripts/` 与其相对路径不变。

## 首次配置

复制 `dao-video/config.example.yaml` 为目标项目的本地 `config.yaml`，填写自己的配置，不要修改并重新分发示例文件：

- 项目根目录与品牌名称
- MiniMax API Key、自有或获授权的 Voice ID、余额
- 火山方舟 API Key、模型权限与余额（仅使用 Ark 的分支需要）
- BGM、字体、封面框等本地素材路径
- 发布平台及浏览器自动化配置

如需自动填写发布页面，还需安装 Ego Lite 或替换为目标 Agent 可用的浏览器自动化能力。所有发布流程必须停在最终发布按钮前，由用户亲自确认。

## 建议测试

在正式生成前执行：

```bash
python3 dao-video/scripts/doctor.py --config /absolute/path/to/config.yaml
```

需要测试发布依赖时再追加 `--publishing`。测试通过不代表相关第三方模型已经开通或账户余额充足。

## 调用示例

```text
使用 dao-video 创建一条传统文化短视频，选择 dao-blackgold-video 风格。
```

```text
使用 dao-video 继续上一次项目，选择 dao-ink-video 风格，发布前停下等待确认。
```

## 隐私与费用

- 包内不包含维护者的 API Key、Voice ID、登录状态、本机配置或个人项目数据。
- MiniMax、火山方舟及其他生成服务可能收费，调用前确认价格、权限与余额。
- 只能使用自己拥有或明确获授权的声音、音乐、字体和视觉素材。
