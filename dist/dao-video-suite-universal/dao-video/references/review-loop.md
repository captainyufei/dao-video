# Post-publication review loop

## Purpose

Turn each published episode into a controlled learning cycle:

```text
publish → capture metrics → compare baseline → diagnose funnel → choose one change → publish next test → verify
```

Do not optimize from a single metric or one unusually strong/weak post.

## Checkpoints

Use the configured checkpoints, defaulting to:

- 24 hours: early distribution, hook, and initial engagement
- 72 hours: stable completion and interaction pattern
- 168 hours: long-tail reach, saves, follows, and delayed distribution

Record the exact observation time and elapsed hours. Never replace an earlier snapshot with a later one.

## Metrics

Collect every metric the platform exposes, without inventing missing values:

- impressions or recommendation exposure
- plays/views
- 2-second and 5-second retention when available
- average watch time
- completion rate
- likes
- comments
- shares
- saves/favorites
- profile visits
- new followers attributed to the work

Derived rates may be calculated only when denominators are known:

- like rate = likes / views
- comment rate = comments / views
- share rate = shares / views
- save rate = saves / views
- follow conversion = new followers / views

Do not combine Douyin and WeChat Channels into one number. Platform distributions are separate experiments.

## Data collection

When the user requests automatic review:

1. Read the local project state and confirmed publish time.
2. Use Ego Lite only when the user has already logged into the relevant creator center.
3. Read visible analytics without changing account settings, deleting content, replying to comments, or publishing anything.
4. If login, verification, or a platform challenge appears, hand control to the user.
5. Save the raw snapshot with `scripts/review_metrics.py`; include unavailable fields as absent, not zero.

Manual screenshots or copied numbers are equally valid inputs. Preserve their source path or note.

## Diagnosis order

Diagnose the funnel from earliest to latest:

1. **Distribution** — low exposure with otherwise strong retention may indicate account/topic fit, packaging, or insufficient sample size.
2. **Hook** — weak 2-second/5-second retention points first to the opening sentence, first frame, or opening BGM/pace.
3. **Body** — acceptable opening but low average watch/completion points to pacing, repetition, scene duration, or narration density.
4. **Interaction** — strong completion but weak likes/comments/shares/saves points to emotional payoff, usefulness, distinctiveness, or call-to-reflection.
5. **Conversion** — strong interaction but weak follows points to unclear account promise, inconsistent series identity, or weak profile continuity.

Never claim causation from correlation. Write `hypothesis`, not `cause`, until a follow-up test supports it.

## Baseline

- Compare against the median of the previous configured number of comparable episodes, default 5.
- Prefer median over average to reduce the impact of one viral outlier.
- Match platform and checkpoint. When possible, also match video duration and topic category.
- If fewer than 3 comparable episodes exist, label the baseline `insufficient` and make only conservative changes.

## One-variable experiment

Choose one primary variable for the next episode:

- hook wording
- first-frame composition
- opening BGM level or intro duration
- narration speed
- total duration
- scene-change frequency
- subtitle density
- title
- cover composition
- topic angle
- closing payoff or interaction prompt

Keep other settings stable. Record:

- hypothesis
- changed variable
- old value or pattern
- new value or pattern
- target metric
- expected direction
- evaluation checkpoint
- rollback condition

## Determine whether an adjustment worked

At the matching checkpoint, compare the test episode with its baseline and the immediately preceding episode:

- `effective`: target metric improved materially without unacceptable decline in guardrail metrics
- `neutral`: difference is small or sample is insufficient
- `harmful`: target metric worsened materially or guardrails deteriorated
- `inconclusive`: platform distribution or topic changed too much for a fair comparison

Do not define “material” universally. Use the project's historical volatility; until enough history exists, require a clear directional improvement across at least two comparable tests before making the change permanent.

## Files

Store:

```text
06-复盘/
├── metrics.jsonl
├── YYYYMMDD-标题-24h.md
├── YYYYMMDD-标题-72h.md
├── YYYYMMDD-标题-168h.md
└── experiments.md
```

Use `scripts/review_metrics.py` to append snapshots and generate a concise Markdown review. Never store cookies, account IDs, phone numbers, private comments, or creator-center screenshots containing unrelated personal information in the repository.
