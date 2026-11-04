import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Frame, PadGrid, clamp } from "./design";
import { Narration } from "./Narration";
export const Intro = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame
      n="01"
      title="One grid. A complete DJ setup."
      note="Two decks + mixer + FX · Built for the Meta hackathon"
    >
      <Narration id="intro" />
      <div style={{ position: "absolute", left: 0, top: 70, width: 850 }}>
        <div
          style={{
            fontSize: 112,
            fontWeight: 750,
            lineHeight: 1.05,
            letterSpacing: -6,
          }}
        >
          LAUNCHPAD
          <br />
          <span style={{ color: C.green }}>× MIXXX</span>
        </div>
        <div
          style={{
            fontSize: 37,
            lineHeight: 1.45,
            color: C.muted,
            marginTop: 34,
            width: 720,
          }}
        >
          Turn a Novation Launchpad MK2
          <br />
          into a two-deck DJ controller.
        </div>
        <div style={{ marginTop: 42, display: "flex", gap: 14 }}>
          {["TWO DECKS", "MIXER", "EFFECTS"].map((x, i) => (
            <div
              key={x}
              style={{
                fontSize: 22,
                padding: "15px 22px",
                border: "1px solid #496051",
                borderRadius: 30,
                opacity: interpolate(
                  f,
                  [(1.2 + i * 0.35) * fps, (1.6 + i * 0.35) * fps],
                  [0, 1],
                  clamp,
                ),
                color: C.green,
              }}
            >
              {x}
            </div>
          ))}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 1030,
          top: 40,
          rotate: `${interpolate(f, [0, 9 * fps], [-8, -3], clamp)}deg`,
          scale: interpolate(f, [0, 1.5 * fps], [0.85, 0.93], clamp),
        }}
      >
        <PadGrid
          presses={[
            { row: 0, col: 1, start: 1.5, end: 2.2 },
            { row: 0, col: 5, start: 3, end: 3.6 },
            { row: 7, col: 4, start: 5, end: 7 },
          ]}
        />
      </div>
    </Frame>
  );
};
