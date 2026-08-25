import React from 'react';
import {AbsoluteFill, Img, staticFile, useVideoConfig} from 'remotion';

const TITLE = '不争';
const RED = '#d3241d';
const BACK_RED = '#7e201b';
const IVORY = '#f4efe5';

type CoverLayout = {
  backTop: number;
  backFontSize: number;
  waterline: number;
  reflectionDepth: number;
  frontTop: number;
  frontFontSize: number;
  explanationTop: number;
  explanationFontSize: number;
};

const Seal: React.FC<{portrait: boolean}> = ({portrait}) => {
  const width = portrait ? 68 : 62;
  const height = portrait ? 116 : 106;
  const id = portrait ? 'portrait' : 'horizontal';

  return (
    <div
      style={{
        position: 'absolute',
        top: portrait ? 44 : 36,
        right: portrait ? 46 : 52,
        width,
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        rotate: '2deg',
      }}
    >
      <svg width={width} height={height} viewBox="0 0 68 116" style={{position: 'absolute', inset: 0}}>
        <defs>
          <filter id={`sealEdgeRoughness-${id}`} x="-15%" y="-10%" width="130%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="18" result="sealNoise" />
            <feDisplacementMap in="SourceGraphic" in2="sealNoise" scale="2.4" xChannelSelector="R" yChannelSelector="B" />
          </filter>
          <filter id={`sealPigmentTexture-${id}`} x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.22" numOctaves="3" seed="33" result="pigment" />
            <feComposite in="pigment" in2="SourceGraphic" operator="in" result="texture" />
            <feBlend in="SourceGraphic" in2="texture" mode="multiply" />
          </filter>
        </defs>
        <path
          d="M18 4 C29 0 46 2 55 8 C64 18 64 35 63 51 L62 86 C59 101 50 111 35 113 C20 111 9 104 6 89 L5 31 C7 16 11 8 18 4 Z"
          fill="#b8332a"
          filter={`url(#sealEdgeRoughness-${id})`}
        />
        <path
          d="M20 8 C32 5 45 6 53 12 C59 23 59 41 58 58 L57 85 C54 98 47 105 35 107 C22 105 14 99 11 87 L10 31 C12 19 15 11 20 8 Z"
          fill="#c23b30"
          opacity="0.38"
          filter={`url(#sealPigmentTexture-${id})`}
        />
      </svg>
      <span
        style={{
          position: 'relative',
          color: '#f2e6cf',
          fontFamily: 'Kaiti SC, STKaiti, serif',
          fontSize: portrait ? 22 : 20,
          lineHeight: 1.05,
          letterSpacing: 5,
          writingMode: 'vertical-rl',
        }}
      >
        青云观
      </span>
    </div>
  );
};

const ReflectedTitle: React.FC<{
  width: number;
  height: number;
  layout: CoverLayout;
  portrait: boolean;
}> = ({width, height, layout, portrait}) => {
  const id = portrait ? 'portrait' : 'horizontal';
  const reflectedScale = 0.78;
  const reflectedTranslateY = layout.waterline * (1 + reflectedScale);

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{position: 'absolute', inset: 0}}>
      <defs>
        <clipPath id={`titleReflectionClip-${id}`}>
          <rect x="0" y={layout.waterline} width={width} height={layout.reflectionDepth} />
        </clipPath>
        <linearGradient id={`reflectionFade-${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="white" stopOpacity="1" />
          <stop offset="0.72" stopColor="white" stopOpacity="0.38" />
          <stop offset="1" stopColor="white" stopOpacity="0" />
        </linearGradient>
        <mask id={`reflectionMask-${id}`}>
          <rect
            x="0"
            y={layout.waterline}
            width={width}
            height={layout.reflectionDepth}
            fill={`url(#reflectionFade-${id})`}
          />
        </mask>
        <filter id={`titleWater-${id}`} x="-20%" y="-20%" width="140%" height="140%">
          <feTurbulence type="fractalNoise" baseFrequency="0.0048 0.078" numOctaves="2" seed="71" result="titleNoise" />
          <feDisplacementMap in="SourceGraphic" in2="titleNoise" scale="50" xChannelSelector="R" yChannelSelector="B" />
        </filter>
      </defs>
      <g
        clipPath={`url(#titleReflectionClip-${id})`}
        mask={`url(#reflectionMask-${id})`}
        filter={`url(#titleWater-${id})`}
        opacity="0.42"
      >
        <text
          x={width / 2}
          y={layout.waterline}
          textAnchor="middle"
          fill={BACK_RED}
          fontFamily="HeiZhaoBangShu, Kaiti SC, STKaiti, serif"
          fontSize={layout.backFontSize}
          letterSpacing="5"
          transform={`translate(0 ${reflectedTranslateY}) scale(1 -${reflectedScale})`}
        >
          {TITLE}
        </text>
      </g>
    </svg>
  );
};

export const BuzhengCover: React.FC = () => {
  const {width, height} = useVideoConfig();
  const portrait = height > width;
  const layout: CoverLayout = portrait
    ? {
        backTop: 505,
        backFontSize: 258,
        waterline: 735,
        reflectionDepth: 330,
        frontTop: 642,
        frontFontSize: 156,
        explanationTop: 818,
        explanationFontSize: 38,
      }
    : {
        backTop: 318,
        backFontSize: 250,
        waterline: 540,
        reflectionDepth: 285,
        frontTop: 448,
        frontFontSize: 150,
        explanationTop: 616,
        explanationFontSize: 36,
      };

  return (
    <AbsoluteFill style={{backgroundColor: '#060706', overflow: 'hidden', fontSynthesis: 'none'}}>
      <Img
        src={staticFile('backgrounds/ink-calligraphy-clean-v2.png')}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center',
          transform: portrait ? 'scale(1.22)' : 'scale(1.03)',
          filter: 'grayscale(.95) contrast(1.08) brightness(.64)',
          opacity: 0.88,
        }}
      />

      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: portrait
            ? 'radial-gradient(circle at 50% 46%, rgba(44,47,40,.22), rgba(2,3,2,.9) 75%)'
            : 'radial-gradient(ellipse at 50% 47%, rgba(44,47,40,.2), rgba(2,3,2,.9) 76%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          boxShadow: portrait
            ? 'inset 0 0 170px 65px rgba(0,0,0,.88)'
            : 'inset 0 0 160px 58px rgba(0,0,0,.88)',
        }}
      />

      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: layout.backTop,
          color: BACK_RED,
          opacity: 1,
          fontFamily: 'HeiZhaoBangShu, Kaiti SC, STKaiti, serif',
          fontSize: layout.backFontSize,
          lineHeight: 1,
          letterSpacing: 5,
          textAlign: 'center',
          whiteSpace: 'nowrap',
          textShadow: 'none',
        }}
      >
        {TITLE}
      </div>

      <ReflectedTitle width={width} height={height} layout={layout} portrait={portrait} />

      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: layout.frontTop,
          textAlign: 'center',
          fontFamily: 'WeibeiSC, serif',
          fontWeight: 700,
          fontSize: layout.frontFontSize,
          lineHeight: 1,
          letterSpacing: 2,
          textShadow: 'none',
          whiteSpace: 'nowrap',
        }}
      >
        <span style={{color: IVORY}}>不</span>
        <span style={{color: RED}}>争</span>
      </div>

      <div
        style={{
          position: 'absolute',
          left: portrait ? 70 : 90,
          right: portrait ? 70 : 90,
          top: layout.explanationTop,
          color: '#eee8dc',
          fontFamily: 'FZCuJinLing, Songti SC, STSong, serif',
          fontSize: layout.explanationFontSize,
          fontWeight: 700,
          letterSpacing: portrait ? 4 : 5,
          textAlign: 'center',
          whiteSpace: 'nowrap',
          textShadow: '0 4px 14px #000',
        }}
      >
        ｜不争一时之胜，方得长久之安｜
      </div>

      <Seal portrait={portrait} />

      <svg width={width} height={height} style={{position: 'absolute', inset: 0, opacity: 0.08}}>
        <filter id={`coverPaperNoise-${portrait ? 'portrait' : 'horizontal'}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.72" numOctaves="3" seed="29" />
        </filter>
        <rect width={width} height={height} filter={`url(#coverPaperNoise-${portrait ? 'portrait' : 'horizontal'})`} />
      </svg>
    </AbsoluteFill>
  );
};
