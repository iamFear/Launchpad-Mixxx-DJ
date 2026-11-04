import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Frame, PadGrid, Deck, clamp } from "./design";
import { Narration } from "./Narration";
export const Transition = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const v = interpolate(t, [3.5, 5.5], [0, 100], clamp);
  return (
    <Frame
      n="04"
      title="Hold to make the handoff."
      note="Crossfader full sweep / approximately 2 seconds"
    >
      <Narration id="transition" />
      <div style={{ position: "absolute", left: 30, top: 0 }}>
        <PadGrid
          scale={0.94}
          presses={[{ row: 7, col: 4, start: 3.5, end: 5.5 }]}
        />
      </div>
      <div style={{ position: "absolute", left: 810, top: 5, width: 880 }}>
        <div style={{ display: "flex", gap: 20 }}>
          <div style={{ flex: 1, opacity: 1 - v / 150 }}>
            <Deck deck="A" status="PLAYING" playing color={C.green} />
          </div>
          <div style={{ flex: 1, opacity: 0.4 + v / 167 }}>
            <Deck deck="B" status="PLAYING" playing color={C.blue} />
          </div>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: 32,
            marginTop: 22,
          }}
        >
          <span style={{ color: C.green }}>DECK A</span>
          <span style={{ color: C.blue }}>DECK B</span>
        </div>
        <div
          style={{
            margin: "35px 15px",
            height: 22,
            background: "linear-gradient(90deg,#8ffc9d,#6dbdff)",
            position: "relative",
            borderRadius: 12,
          }}
        >
          <div
            style={{
              position: "absolute",
              left: `${v}%`,
              top: -19,
              width: 34,
              height: 60,
              borderRadius: 8,
              background: C.white,
              translate: "-50% 0",
              boxShadow: "0 0 30px #fff4",
            }}
          />
        </div>
        <div style={{ fontSize: 66, fontWeight: 600, color: C.blue }}>
          {Math.round(v)}%{" "}
          <span style={{ fontSize: 28, color: C.muted, fontWeight: 400 }}>
            toward Deck B
          </span>
        </div>
      </div>
    </Frame>
  );
};
