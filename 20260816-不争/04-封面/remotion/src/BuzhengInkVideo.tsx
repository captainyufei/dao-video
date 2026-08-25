import {Audio} from '@remotion/media';
import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const CANVAS_WIDTH = 1920;
const CANVAS_HEIGHT = 1080;
const HORIZON = 715;
const TITLE_MIRROR_LINE = 620;
const TILE_WIDTH = 2087;
const MANUSCRIPT_HEIGHT = 1000;
const RED = '#ff1744';
const PALE = '#f4f0e7';
const BACK_RED = '#ed3b2f';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

export type CaptionPhrase = {text: string; red: number[]; reveal: number};
export type CaptionGroup = {from: number; to: number; phrases: CaptionPhrase[]; explanation: string};

export const DRAFT_CAPTION_GROUPS: CaptionGroup[] = [
  {
    from: 0,
    to: 81,
    phrases: [
      {text: '争则气浮', red: [0, 3], reveal: 0},
      {text: '静则神定', red: [0, 3], reveal: 0},
    ],
    explanation: '一味争强，最先扰乱的是自己的心。',
  },
  {
    from: 81,
    to: 191,
    phrases: [
      {text: '心乱事难明', red: [1, 4], reveal: 81},
      {text: '虑清行有方', red: [1, 4], reveal: 136},
    ],
    explanation: '心静下来，判断才会清楚，行动才有方向。',
  },
  {
    from: 191,
    to: 267,
    phrases: [
      {text: '不争口舌', red: [1, 3], reveal: 191},
      {text: '非为怯懦', red: [1, 3], reveal: 229},
    ],
    explanation: '不与无谓的是非纠缠，是在保护自己的心力。',
  },
  {
    from: 267,
    to: 345,
    phrases: [
      {text: '不逐虚名', red: [1, 3], reveal: 267},
      {text: '非无志向', red: [1, 3], reveal: 306},
    ],
    explanation: '不被外界评价牵着走，才能守住真正要走的路。',
  },
  {
    from: 345,
    to: 415,
    phrases: [
      {text: '水居其下', red: [0, 3], reveal: 345},
      {text: '润物无声', red: [0, 3], reveal: 380},
    ],
    explanation: '水不抢先，却能顺势绕过阻挡，抵达更远处。',
  },
  {
    from: 415,
    to: 510,
    phrases: [
      {text: '藏锋守拙', red: [0, 3], reveal: 415},
      {text: '长久之安', red: [0, 3], reveal: 449},
    ],
    explanation: '放下一时输赢，是为了守住长久的清醒与力量。',
  },
];

export const PACED_CAPTION_GROUPS: CaptionGroup[] = [
  {
    from: 0,
    to: 119,
    phrases: [
      {text: '争则气浮', red: [0, 3], reveal: 0},
      {text: '静则神定', red: [0, 3], reveal: 0},
    ],
    explanation: '一味争强，最先扰乱的是自己的心。',
  },
  {
    from: 119,
    to: 245,
    phrases: [
      {text: '心乱事难明', red: [1, 4], reveal: 119},
      {text: '虑清行有方', red: [1, 4], reveal: 168},
    ],
    explanation: '心静下来，判断才会清楚，行动才有方向。',
  },
  {
    from: 245,
    to: 358,
    phrases: [
      {text: '不争口舌', red: [1, 3], reveal: 245},
      {text: '非为怯懦', red: [1, 3], reveal: 288},
    ],
    explanation: '不与无谓的是非纠缠，是在保护自己的心力。',
  },
  {
    from: 358,
    to: 463,
    phrases: [
      {text: '不逐虚名', red: [1, 3], reveal: 358},
      {text: '非无志向', red: [1, 3], reveal: 396},
    ],
    explanation: '不被外界评价牵着走，才能守住真正要走的路。',
  },
  {
    from: 463,
    to: 569,
    phrases: [
      {text: '水居其下', red: [0, 3], reveal: 463},
      {text: '润物无声', red: [0, 3], reveal: 502},
    ],
    explanation: '水不抢先，却能顺势绕过阻挡，抵达更远处。',
  },
  {
    from: 569,
    to: 720,
    phrases: [
      {text: '藏锋守拙', red: [0, 3], reveal: 569},
      {text: '长久之安', red: [0, 3], reveal: 610},
    ],
    explanation: '放下一时输赢，是为了守住长久的清醒与力量。',
  },
];

const grayGlyphs = [
  {text: '将', x: 115, y: 165, size: 152},
  {text: '进', x: 480, y: 165, size: 152},
  {text: '酒', x: 845, y: 165, size: 152},
  {text: '莫', x: 1210, y: 165, size: 152},
  {text: '停', x: 1575, y: 165, size: 152},
];

const blackGlyphs = [
  {text: '君不见黄河', x: 455, y: 0, size: 138},
  {text: '人生得意', x: 1630, y: -10, size: 145},
  {text: '天生我材', x: 170, y: 225, size: 126},
  {text: '与尔同销', x: 1810, y: 145, size: 128},
];

const BackgroundGlyphs: React.FC<{travel: number}> = ({travel}) => (
  <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
    {grayGlyphs.map((item) => (
      <span
        key={`${item.text}-${item.x}`}
        style={{
          position: 'absolute', left: item.x, top: item.y, color: '#46483f', opacity: 0.82,
          fontFamily: 'BackgroundBrush, Kaiti SC, STKaiti, serif', fontSize: item.size,
          lineHeight: 1, letterSpacing: 18, writingMode: 'vertical-rl',
        }}
      >
        {item.text}
      </span>
    ))}
    {blackGlyphs.map((item) => (
      <span
        key={`${item.text}-${item.x}`}
        style={{
          position: 'absolute', left: item.x - 100 + travel * 180, top: item.y, color: '#000', opacity: 0.92,
          fontFamily: 'BackgroundBrush, Kaiti SC, STKaiti, serif', fontSize: item.size,
          lineHeight: 1, letterSpacing: 20, writingMode: 'vertical-rl',
        }}
      >
        {item.text}
      </span>
    ))}
  </div>
);

const SceneSource: React.FC<{travel: number; reflection?: boolean}> = ({travel, reflection = false}) => {
  const manuscriptX = -400 + travel * 320;
  return (
    <div style={{position: 'relative', width: CANVAS_WIDTH, height: HORIZON, overflow: 'hidden'}}>
      {Array.from({length: 4}).map((_, index) => (
        <div
          key={index}
          style={{
            position: 'absolute', left: manuscriptX + index * TILE_WIDTH, top: 0,
            width: TILE_WIDTH, height: MANUSCRIPT_HEIGHT, overflow: 'hidden',
          }}
        >
          <Img
            src={staticFile('backgrounds/将进酒-书法底图-ai-v7-十九列上下裁剪正式版.png')}
            style={{
              position: 'absolute', inset: 0, width: TILE_WIDTH, height: MANUSCRIPT_HEIGHT,
              objectFit: 'cover', opacity: reflection ? 0.96 : 1,
            }}
          />
        </div>
      ))}
      <BackgroundGlyphs travel={travel} />
    </div>
  );
};

const WaterReflection: React.FC<{frame: number; travel: number}> = ({frame, travel}) => {
  const phase = (frame / 150) * Math.PI * 4;
  const noiseShift = (frame * 0.9) % 320;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: HORIZON, bottom: 0, overflow: 'hidden', backgroundColor: '#b9b095'}}>
      <svg width="0" height="0" style={{position: 'absolute'}}>
        <filter id="buzhengSceneWater" x="-15%" y="-15%" width="130%" height="130%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency={`${0.0032 + Math.sin(phase) * 0.00035} 0.035`}
            numOctaves="2"
            seed="43"
            result="noise"
          />
          <feOffset in="noise" dx={noiseShift} dy={Math.sin(phase) * 3.5} result="movingNoise" />
          <feDisplacementMap
            in="SourceGraphic" in2="movingNoise" scale={24 + Math.sin(phase * 1.35) * 7}
            xChannelSelector="R" yChannelSelector="B"
          />
        </filter>
      </svg>
      <div
        style={{
          position: 'absolute', left: 0, top: 0, width: CANVAS_WIDTH, height: HORIZON, overflow: 'hidden',
          transform: `translateY(${HORIZON * 0.72 - 8}px) scaleY(-0.72)`, transformOrigin: 'center top',
          filter: 'url(#buzhengSceneWater)', opacity: 0.96,
        }}
      >
        <SceneSource travel={travel} reflection />
      </div>
      <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(216,201,168,0), rgba(118,102,76,.2) 100%)'}} />
      {Array.from({length: 18}).map((_, index) => (
        <div
          key={index}
          style={{
            position: 'absolute', left: `${-8 + ((index * 27) % 108)}%`, top: 8 + index * 20,
            width: 160 + ((index * 73) % 420), height: index % 5 === 0 ? 3 : 1,
            backgroundColor: '#4b4436',
            opacity: 0.05 + (index % 4) * 0.025,
            translate: `${Math.sin(phase * 2 + index * 0.85) * 58}px 0`,
          }}
        />
      ))}
    </div>
  );
};

const RearTitle: React.FC<{frame: number}> = ({frame}) => {
  const phase = (frame / 150) * Math.PI * 4;
  const reflectionScale = 0.78;
  const reflectionGap = 10;
  const reflectionTranslate = TITLE_MIRROR_LINE * (1 + reflectionScale) + reflectionGap;
  return (
    <svg width={CANVAS_WIDTH} height={CANVAS_HEIGHT} viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`} style={{position: 'absolute', inset: 0}}>
      <defs>
        <clipPath id="buzhengTitleReflectionClip">
          <rect x="0" y={TITLE_MIRROR_LINE + reflectionGap} width={CANVAS_WIDTH} height={CANVAS_HEIGHT - TITLE_MIRROR_LINE - reflectionGap} />
        </clipPath>
        <linearGradient id="buzhengTitleReflectionFade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="white" stopOpacity="0.08" />
          <stop offset="0.07" stopColor="white" stopOpacity="0.72" />
          <stop offset="0.18" stopColor="white" stopOpacity="1" />
          <stop offset="1" stopColor="white" stopOpacity="1" />
        </linearGradient>
        <mask id="buzhengTitleReflectionMask">
          <rect x="0" y={TITLE_MIRROR_LINE + reflectionGap} width={CANVAS_WIDTH} height={CANVAS_HEIGHT - TITLE_MIRROR_LINE - reflectionGap} fill="url(#buzhengTitleReflectionFade)" />
        </mask>
        <filter id="buzhengTitleWater" x="-20%" y="-20%" width="140%" height="140%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency={`${0.0048 + Math.sin(phase) * 0.00045} 0.078`}
            numOctaves="2"
            seed="71"
            result="titleNoise"
          />
          <feDisplacementMap in="SourceGraphic" in2="titleNoise" scale="50" xChannelSelector="R" yChannelSelector="B" />
        </filter>
      </defs>
      <text
        x={CANVAS_WIDTH / 2} y={TITLE_MIRROR_LINE} textAnchor="middle" fill={BACK_RED} fillOpacity="0.22"
        fontFamily="HeiZhaoBangShu, Kaiti SC, STKaiti, serif" fontSize="340" letterSpacing="10"
      >
        不争
      </text>
      <g
        clipPath="url(#buzhengTitleReflectionClip)" mask="url(#buzhengTitleReflectionMask)"
        filter="url(#buzhengTitleWater)" opacity="0.22"
      >
        <text
          x={CANVAS_WIDTH / 2} y={TITLE_MIRROR_LINE} textAnchor="middle" fill={BACK_RED}
          fontFamily="HeiZhaoBangShu, Kaiti SC, STKaiti, serif" fontSize="340" letterSpacing="10"
          transform={`translate(0 ${reflectionTranslate}) scale(1 -${reflectionScale})`}
        >
          不争
        </text>
      </g>
    </svg>
  );
};

const MainCaptions: React.FC<{frame: number; groups: CaptionGroup[]}> = ({frame, groups}) => {
  const group = groups.find((item) => frame >= item.from && frame < item.to);
  if (!group) return null;
  const groupOpacity = group.from === 0
    ? interpolate(frame, [0, Math.max(6, group.to - 6), group.to], [1, 1, 0], clamp)
    : interpolate(
        frame,
        [group.from, group.from + 5, Math.max(group.from + 6, group.to - 6), group.to],
        [0.25, 1, 1, 0],
        clamp,
      );
  const explanationLength = [...group.explanation].length;
  const explanationFontSize = explanationLength >= 24 ? 39 : explanationLength >= 20 ? 42 : 46;

  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: groupOpacity}}>
      <div
        style={{
          position: 'absolute', left: 260, top: 470, width: 1400, display: 'flex', justifyContent: 'center',
          gap: 76, alignItems: 'center',
        }}
      >
        {group.phrases.map((item) => {
          const length = [...item.text].length;
          const fontSize = length >= 6 ? 96 : length === 5 ? 112 : 132;
          return (
            <div
              key={item.text}
              style={{
                width: 650, fontFamily: 'WeibeiSC, serif', fontSize, fontWeight: 700, lineHeight: 1,
                letterSpacing: length >= 6 ? 7 : 10, whiteSpace: 'nowrap', textAlign: 'center',
                textShadow: '0 4px 14px rgba(0,0,0,.88)',
                opacity: item.reveal === 0 ? 1 : interpolate(frame, [item.reveal, item.reveal + 5], [0, 1], clamp),
              }}
            >
              {[...item.text].map((char, index) => (
                <span key={`${char}-${index}`} style={{color: item.red.includes(index) ? RED : PALE}}>{char}</span>
              ))}
            </div>
          );
        })}
      </div>
      <div
        style={{
          position: 'absolute', left: 150, right: 150, top: 650, color: '#f0eadf',
          fontFamily: 'FZCuJinLing, STSong, serif', fontSize: explanationFontSize, fontWeight: 700,
          lineHeight: 1.25, letterSpacing: 2, display: 'flex', justifyContent: 'center', alignItems: 'center',
          gap: 20, whiteSpace: 'nowrap', textShadow: '0 3px 12px rgba(0,0,0,.92)',
        }}
      >
        <span>丨</span><span>{group.explanation}</span><span>丨</span>
      </div>
    </AbsoluteFill>
  );
};

const Seal: React.FC = () => (
  <div
    style={{
      position: 'absolute', top: 44, right: 58, width: 70, height: 120,
      display: 'flex', alignItems: 'center', justifyContent: 'center', rotate: '2deg',
    }}
  >
    <svg width="70" height="120" viewBox="0 0 68 116" style={{position: 'absolute', inset: 0}}>
      <defs>
        <filter id="videoSealRoughness" x="-15%" y="-10%" width="130%" height="120%">
          <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="18" result="sealNoise" />
          <feDisplacementMap in="SourceGraphic" in2="sealNoise" scale="2.4" xChannelSelector="R" yChannelSelector="B" />
        </filter>
      </defs>
      <path
        d="M18 4 C29 0 46 2 55 8 C64 18 64 35 63 51 L62 86 C59 101 50 111 35 113 C20 111 9 104 6 89 L5 31 C7 16 11 8 18 4 Z"
        fill="#b8332a" filter="url(#videoSealRoughness)"
      />
      <path
        d="M20 8 C32 5 45 6 53 12 C59 23 59 41 58 58 L57 85 C54 98 47 105 35 107 C22 105 14 99 11 87 L10 31 C12 19 15 11 20 8 Z"
        fill="#c23b30" opacity="0.34"
      />
    </svg>
    <span
      style={{
        position: 'relative', color: '#f2e6cf', fontFamily: 'Kaiti SC, STKaiti, serif',
        fontSize: 22, lineHeight: 1.05, letterSpacing: 5, writingMode: 'vertical-rl',
      }}
    >
      青云观
    </span>
  </div>
);

export type BuzhengInkVideoProps = {groups?: CaptionGroup[]; voiceFile?: string; bgmFile?: string};

export const BuzhengInkVideo: React.FC<BuzhengInkVideoProps> = ({groups = DRAFT_CAPTION_GROUPS, voiceFile, bgmFile}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const travel = (1 - Math.cos((frame / durationInFrames) * Math.PI * 2)) / 2;

  return (
    <AbsoluteFill style={{backgroundColor: '#080a07', overflow: 'hidden'}}>
      {bgmFile ? (
        <Audio
          src={staticFile(bgmFile)}
          volume={(audioFrame) => interpolate(
            audioFrame,
            [0, 18, Math.max(19, durationInFrames - 30), durationInFrames],
            [0, 0.36, 0.36, 0],
            clamp,
          )}
        />
      ) : null}
      {voiceFile ? <Audio src={staticFile(voiceFile)} /> : null}
      <AbsoluteFill style={{filter: 'brightness(0.08) contrast(0.84) saturate(0.68) sepia(0.12) blur(0.5px)'}}>
        <SceneSource travel={travel} />
        <WaterReflection frame={frame} travel={travel} />
        <AbsoluteFill style={{pointerEvents: 'none', background: 'rgba(22,25,12,.18)', mixBlendMode: 'multiply'}} />
        <AbsoluteFill
          style={{
            pointerEvents: 'none',
            background: 'radial-gradient(ellipse 68% 62% at 50% 47%, rgba(0,0,0,0) 18%, rgba(0,0,0,.14) 54%, rgba(0,0,0,.68) 100%)',
          }}
        />
      </AbsoluteFill>
      <div
        style={{
          position: 'absolute', left: 410, top: 280, width: 1100, height: 610, pointerEvents: 'none',
          background: 'radial-gradient(ellipse at center, rgba(0,0,0,.3) 0%, rgba(0,0,0,.18) 48%, rgba(0,0,0,0) 78%)',
        }}
      />
      <RearTitle frame={frame} />
      <MainCaptions frame={frame} groups={groups} />
      <Seal />
      <svg width={CANVAS_WIDTH} height={CANVAS_HEIGHT} style={{position: 'absolute', inset: 0, opacity: 0.055}}>
        <filter id="videoPaperNoise"><feTurbulence type="fractalNoise" baseFrequency="0.72" numOctaves="3" seed="29" /></filter>
        <rect width={CANVAS_WIDTH} height={CANVAS_HEIGHT} filter="url(#videoPaperNoise)" />
      </svg>
    </AbsoluteFill>
  );
};
