import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Frame, PadGrid, clamp } from "./design";
import { Narration } from "./Narration";
export const Outro = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame
      n="06"
      title="No hardware? Start on screen."
      note="Launchpad-Mixxx-DJ · macOS · Mixxx 2.5.x · Python + CoreMIDI"
    >
      <Narration id="outro" />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 760,
          height: 520,
          borderRadius: 22,
          background: "#141b22",
          border: "1px solid #3d4b55",
          padding: 24,
        }}
      >
        <div style={{ fontSize: 24, color: C.muted, marginBottom: 20 }}>
          ● ● ● &nbsp; ON-SCREEN EMULATOR
        </div>
        <div style={{ position: "absolute", left: 25, top: 80 }}>
          <PadGrid
            scale={0.65}
            presses={[
              { row: 0, col: 1, start: 2, end: 2.5 },
              { row: 7, col: 4, start: 3, end: 5 },
            ]}
          />
        </div>
        <div
          style={{
            position: "absolute",
            left: 490,
            top: 110,
            right: 25,
            fontFamily: "monospace",
            fontSize: 19,
            lineHeight: 1.9,
            color: C.green,
          }}
        >
          <div>MIDI COMMANDS</div>
          <div
            style={{
              opacity: interpolate(f, [1 * fps, 1.3 * fps], [0, 1], clamp),
            }}
          >
            [Channel1]
            <br />
            play 1.00
          </div>
          <div
            style={{
              opacity: interpolate(f, [3 * fps, 3.3 * fps], [0, 1], clamp),
              color: C.blue,
            }}
          >
            [Master]
            <br />
            crossfader ↑
          </div>
        </div>
      </div>
      <div style={{ position: "absolute", left: 900, top: 30, width: 810 }}>
        <div style={{ fontSize: 24, color: C.green, letterSpacing: 3 }}>
          THE SIGNAL PATH
        </div>
        <div style={{ fontSize: 46, lineHeight: 1.7, marginTop: 24 }}>
          Launchpad or emulator
          <br />
          <span style={{ color: C.green }}>↓ MIDI bridge</span>
          <br />
          Mixxx handles the audio
        </div>
        <div
          style={{
            marginTop: 38,
            fontSize: 57,
            fontWeight: 650,
            lineHeight: 1.1,
            letterSpacing: -2,
          }}
        >
          Your DJ workflow.
          <br />
          <span style={{ color: C.green }}>One pad grid.</span>
        </div>
        <div style={{ fontSize: 19, color: C.muted, marginTop: 25 }}>
          Generic female narration · AI-generated macOS voice
        </div>
      </div>
    </Frame>
  );
};
