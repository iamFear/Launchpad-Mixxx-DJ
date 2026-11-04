import { Series, useVideoConfig } from "remotion";
import { Intro } from "./Intro";
import { Decks } from "./Decks";
import { Controls } from "./Controls";
import { Transition } from "./Transition";
import { Mixer } from "./Mixer";
import { Outro } from "./Outro";
export const Demo = () => {
  const { fps } = useVideoConfig();
  return (
    <Series>
      <Series.Sequence name="One grid" durationInFrames={287} premountFor={fps}>
        <Intro />
      </Series.Sequence>
      <Series.Sequence
        name="Prepare two decks"
        durationInFrames={303}
        premountFor={fps}
      >
        <Decks />
      </Series.Sequence>
      <Series.Sequence
        name="Color coded controls"
        durationInFrames={341}
        premountFor={fps}
      >
        <Controls />
      </Series.Sequence>
      <Series.Sequence
        name="Two-track transition"
        durationInFrames={242}
        premountFor={fps}
      >
        <Transition />
      </Series.Sequence>
      <Series.Sequence
        name="Mixer and effects"
        durationInFrames={338}
        premountFor={fps}
      >
        <Mixer />
      </Series.Sequence>
      <Series.Sequence
        name="Hardware-free emulator"
        durationInFrames={332}
        premountFor={fps}
      >
        <Outro />
      </Series.Sequence>
    </Series>
  );
};
