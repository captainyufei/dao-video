<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="DAO VIDEO：从文案、画面、配音、剪辑、封面到等待人工确认发布的完整流程">
</p>

<h1 align="center">DAO VIDEO</h1>

<p align="center">
  把选题、文案、AI 画面、复刻配音、字幕、BGM、双封面和平台待发布表单连成一条可恢复、可配置的短视频生产线。
</p>

> 当前仓库保持私有。自动发布只负责上传和填写，永远停在最终发布按钮之前。

## 能做什么

- 从主题生成原创中文哲思、传统文化或节气口播文案
- 把确认后的文案拆成分镜，生成静帧和动态视频
- 使用 MiniMax 账号内音色完成配音并导出同次生成的字幕时间戳
- 使用 FFmpeg 合成画面、字幕、品牌包装和手工 BGM 音量包络
- 从同一视频原帧制作 `3:4` 与 `4:3` 两张封面
- 打包抖音、视频号所需的视频、封面、标题和话题
- 使用 Ego Lite 上传并填写两个平台，最后交回用户确认发布
- 记录每一期的确认状态，随时从现有项目继续生产

## 安装

需要 macOS 或 Linux、Python 3、FFmpeg、Node.js、npm 和 npx。剪映草稿与 Ego Lite 发布属于 macOS 可选能力。

```bash
git clone git@github.com:captainyufei/dao-video.git ~/.codex/skills/dao-video
cd ~/.codex/skills/dao-video
python3 -m pip install -r requirements.txt
```

由于仓库目前是 Private，克隆前需要让 GitHub CLI 或 SSH Key 登录到有权限的账号。

## 首次配置

### 先了解费用

这不是完全免费的本地工具。完整流程会调用第三方付费 API：

- **MiniMax**：音色快速复刻和文本转语音按平台规则收费。账户需要先开通 API、创建 Key，并保持可用余额；试听也可能产生语音合成费用。
- **火山方舟**：文案、Seedream 生图和 Seedance 视频生成按模型实际调用计费。视频生成通常是整条流程中成本最高的步骤。
- **Ego Lite**：浏览器本身当前可以免费安装，但抖音、视频号账号、登录验证以及平台规则由用户自己负责。

价格和模型权限可能变化。运行付费生成前，先在对应控制台查看当日价格、余额和模型开通状态；Skill 不会承诺固定单价，也不会在权限失败时擅自切换模型。

### 一、配置 MiniMax 配音

1. 注册并登录 [MiniMax 开放平台](https://platform.minimaxi.com/)，在“接口密钥”中创建 API Key，并按平台提示充值或购买可用额度。
2. 准备一段**你本人或已取得明确授权**的干净人声：`mp3`、`m4a` 或 `wav`，时长 10 秒–5 分钟，文件不超过 20 MB。避免背景音乐、混响、多人对话和明显噪声。
3. 自定义一个仅属于自己账号的 Voice ID：长度 8–256，以英文字母开头，只使用字母、数字、`-`、`_`，末尾不能是 `-` 或 `_`。
4. 导出环境变量，并用项目脚本上传音频、克隆音色和生成第一次测试旁白：

```bash
export MINIMAX_API_KEY="你的 MiniMax API Key"

python3 scripts/minimax_tts.py \
  --ref-audio "/path/to/authorized-voice.wav" \
  --voice-id "my-dao-voice-01" \
  --text "/path/to/test-narration.txt" \
  --output "/path/to/test-narration.wav" \
  --emotion calm \
  --speed 0.9 \
  --subtitle
```

5. 确认测试音频正常后，把同一个 Voice ID 写入本地 `config.yaml`：

```yaml
voice:
  provider: "minimax"
  voice_id: "my-dao-voice-01"
  emotion: "calm"
  speed: 0.9
```

仓库**不提供也不分发维护者的复刻音色文件或 Voice ID**。音色通常绑定创建它的 MiniMax 账号；其他用户不能假设可直接使用。根据 MiniMax 当前文档，复刻音色若创建后 7 天内没有正式调用，可能被删除，因此首次克隆后应及时完成一次正式合成。

### 二、配置火山方舟、Seedream 和 Seedance

1. 注册并登录[火山方舟控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/overview)。
2. 完成平台要求的认证、开通计费并确保账户有可用额度。
3. 在[API Key 页面](https://console.volcengine.com/ark/region:ark+cn-beijing/apikey)创建 Key。
4. 确认自己的账号可以调用配置文件中的文案模型、Seedream 生图模型和 Seedance 视频模型。只有 API Key 不代表已经获得全部模型权限。
5. 设置凭证：

```bash
export ARK_API_KEY="你的火山方舟 API Key"
```

本项目使用火山方舟直调 API 和模型 ID，不要求创建 `ep-...` 推理接入点。若某个默认模型对你的账号不可用，在控制台选择已开通的兼容模型，再修改 `config.yaml`；不要在不知情的情况下自动换模型并产生不同费用。

### 三、安装 Ego Lite（需要自动填写发布页面时）

Ego Lite 只在“上传视频、填写标题话题和封面、停在发布前”这一步需要；不使用自动发布准备时可以不安装。

1. 按 [Ego Lite 官方 Quick Start](https://www.egolite.app/document/en/docs/quick-start) 下载 macOS 应用并放入 Applications。
2. 打开 Ego Lite 完成首次设置；如希望沿用浏览器登录状态，可在其引导中选择迁移 Chrome 数据。
3. 应用通常会自动安装 `ego-browser` Skill；也可以单独执行：

```bash
npx skills add citrolabs/ego-lite
```

4. 在 Ego Lite 中分别登录自己的抖音和视频号账号。登录状态与 Space 只保存在本机，不会从本仓库同步。
5. 运行 `python3 scripts/doctor.py --publishing` 验证安装。即使验证通过，最终发布按钮仍必须由用户亲自点击。

### 四、生成本地配置

先生成一份不会进入 Git 的本地配置：

```bash
python3 scripts/init_config.py --output config.yaml
```

至少填写以下内容：

```yaml
project:
  root: "/path/to/video-project"

voice:
  voice_id: "your-minimax-voice-id"

audio:
  bgm_path: "/path/to/licensed-bgm.mp3"
```

再提供服务凭证：

```bash
export ARK_API_KEY="..."
export MINIMAX_API_KEY="..."
export DAO_VIDEO_CONFIG="$PWD/config.yaml"
```

方舟凭证也可以由已经登录的 arkcli 当前 Profile 提供。不要把 API Key、Cookie、浏览器目录、付费账户信息或复刻音色源文件提交到仓库。

## 环境预检

```bash
python3 scripts/doctor.py
```

需要准备平台发布时：

```bash
python3 scripts/doctor.py --publishing
```

预检会检查命令行工具、Python 包、凭证、本地项目、音色、BGM、Ego Lite 和“发布前停止”开关。模型权限与平台登录仍需在首次实际调用时确认。

## 日常工作流

```text
选题与来源
    ↓
原创文案 → 用户确认
    ↓
分镜静帧 → 用户确认
    ↓
配音 → 图生视频 → 字幕与剪辑
    ↓
3:4 / 4:3 封面 → 用户确认
    ↓
发布包 → Ego Lite 上传填写
    ↓
等待用户亲自点击发布
```

在 Codex 中可以直接说：

```text
使用 $dao-video 检查配置并继续生成今天的视频。
```

或者从已有项目恢复：

```text
使用 $dao-video 读取项目状态，从上次确认的位置继续，不要重复生成已确认素材。
```

## 核心命令

```bash
# 文案
python3 scripts/ark_llm.py --topic "主题" --out narration.txt

# 黑金国风分镜静帧
python3 scripts/ark_images.py --prompts prompts.txt --outdir assets --scene 围合

# 图生视频
python3 scripts/ark_video.py \
  --images assets/img-01.png,assets/img-02.png \
  --outdir video

# MiniMax 配音与同次字幕时间戳
python3 scripts/minimax_tts.py \
  --text narration.txt \
  --output assets/narration.wav \
  --subtitle
```

模型 ID、音色、情绪、语速、品牌、BGM 和发布 Space 都可以在 `config.yaml` 中调整。完整 Agent 工作规范见 [`SKILL.md`](./SKILL.md)。

## 音频规则

默认不是自动闪避：

- 开头 BGM 较大
- 正文切入后降到恒定音量
- 结尾逐渐升高
- 最后淡出
- 默认删除生成视频的环境音

每一期的语义切点记录在该期 `audio-config.json`，避免只按固定秒数机械处理。

## 发布安全线

- 抖音与视频号在一个长期 Ego Lite Space 的两个标签页中处理
- 两个平台都必须上传正式封面，并以发布主表单缩略图为最终验收依据
- 视频号位置固定为“不显示位置”
- 不自动修改原创声明、可见范围、商业内容、定时发布等不确定开关
- 不点击“发布”“确认发布”“立即发布”“提交发布”或任何等价控件
- 页面准备好后交回用户，由用户完成最终发布

## 可移植性说明

以下内容不会随仓库自动转移：

- MiniMax 复刻音色：音色 ID 通常属于创建它的账号
- BGM 与字体：需要使用者提供有权使用的本地文件
- Ego Lite 登录状态和 Space：每台电脑、每个账号需要单独登录
- 火山模型权限：不同账号需要分别开通对应模型
- 剪映草稿目录：仅在兼容的 macOS 剪映专业版环境中可用

## 仓库结构

```text
dao-video/
├── SKILL.md                 # Agent 核心工作规范
├── config.example.yaml      # 可分享的匿名配置模板
├── requirements.txt
├── agents/openai.yaml       # Skill UI 元数据
├── assets/readme/           # 仓库展示素材
├── references/
│   ├── setup.md             # 安装与可移植性
│   ├── workflow.md          # 制作细节与实测约束
│   ├── ego-publish.md       # 发布前自动化与停止线
│   └── project-state.example.md
└── scripts/                 # 生成、配音、字幕、剪辑、封面与预检工具
```

本地 `config.yaml`、`references/project-state.md`、密钥、浏览器状态以及音视频文件均由 `.gitignore` 排除。

## 当前状态

- 已在青云观实际生产流程中验证文案、黑金分镜、Seedance、MiniMax 复刻音色、字幕、BGM、双封面和 Ego Lite 待发布流程
- 当前默认预设偏向中文传统文化横屏短视频
- 其他品牌可以通过配置复用通用流水线，但需要自行提供视觉预设、音色、BGM 和平台账号
