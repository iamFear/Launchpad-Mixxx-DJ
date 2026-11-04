import { Composition, Folder } from "remotion";
import { Demo } from "./Composition";
import { Intro } from "./Intro";
import { Decks } from "./Decks";
import { Controls } from "./Controls";
import { Transition } from "./Transition";
import { Mixer } from "./Mixer";
import { Outro } from "./Outro";
export const RemotionRoot = () => (
  <>
    <Composition
      id="Launchpad-Demo"
      component={Demo}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={1843}
    />
    <Folder name="Scenes">
      <Composition
        id="Intro"
        component={Intro}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={287}
      />
      <Composition
        id="Decks"
        component={Decks}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={303}
      />
      <Composition
        id="Controls"
        component={Controls}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={341}
      />
      <Composition
        id="Transition"
        component={Transition}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={242}
      />
      <Composition
        id="Mixer"
        component={Mixer}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={338}
      />
      <Composition
        id="Emulator"
        component={Outro}
        width={1920}
        height={1080}
        fps={30}
        durationInFrames={332}
      />
    </Folder>
  </>
);
