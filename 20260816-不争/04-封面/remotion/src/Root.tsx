import React from 'react';
import {Composition} from 'remotion';
import './fonts';
import {BuzhengCover} from './BuzhengCover';
import {BuzhengInkVideo, PACED_CAPTION_GROUPS} from './BuzhengInkVideo';

export const Root: React.FC = () => (
  <>
    <Composition
      id="BuzhengCoverVertical"
      component={BuzhengCover}
      durationInFrames={1}
      fps={30}
      width={1080}
      height={1440}
    />
    <Composition
      id="BuzhengCoverHorizontal"
      component={BuzhengCover}
      durationInFrames={1}
      fps={30}
      width={1440}
      height={1080}
    />
    <Composition
      id="BuzhengInkVideoDraft"
      component={BuzhengInkVideo}
      durationInFrames={510}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="BuzhengInkVideoFinal"
      component={BuzhengInkVideo}
      defaultProps={{
        voiceFile: 'audio/narration-confirmed-fluent-1.18.wav',
        bgmFile: 'audio/ink-bgm-confirmed.wav',
      }}
      durationInFrames={510}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="BuzhengInkVideoPaced24s"
      component={BuzhengInkVideo}
      defaultProps={{
        groups: PACED_CAPTION_GROUPS,
        voiceFile: 'audio/narration-confirmed-fluent-1.08-paced-24s.wav',
        bgmFile: 'audio/ink-bgm-confirmed.wav',
      }}
      durationInFrames={720}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
);
