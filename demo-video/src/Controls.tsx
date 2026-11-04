import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Frame, PadGrid, clamp } from "./design";
import { Narration } from "./Narration";
export const Controls = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const value =
    t < 3
      ? 50
      : t < 4.5
        ? interpolate(t, [3, 4], [50, 100], clamp)
        : t < 6.5
          ? interpolate(t, [5, 6.5], [100, 25], clamp)
          : t < 8
            ? 25
            : 50;
  return (
    <Frame
      n="03"
      title="Three colors. Instant control."
      note="1% every 20 ms while held · Release stops the change"
    >
      <Narration id="controls" />
      <div style={{ position: "absolute", left: 30, top: 0 }}>
        <PadGrid
          scale={0.94}
          presses={[
            { row: 3, col: 2, start: 3, end: 4.5 },
            { row: 3, col: 0, start: 5, end: 6.5 },
            { row: 3, col: 1, start: 8, end: 8.45 },
          ]}
        />
      </div>
      <div style={{ position: "absolute", left: 810, top: 5, width: 850 }}>
        <div style={{ fontSize: 24, color: C.muted, letterSpacing: 3 }}>
          DECK A / FILTER
        </div>
        <div
          style={{
            fontSize: 140,
            fontWeight: 650,
            letterSpacing: -6,
            marginTop: 15,
          }}
        >
          {Math.round(value)}
          <span style={{ fontSize: 60, color: C.muted }}>%</span>
        </div>
        <div
          style={{
            height: 12,
            background: "#24313a",
            borderRadius: 12,
            marginTop: 20,
            marginBottom: 58,
            overflow: "hidden",
          }}
        >
          <div
            style={{ width: `${value}%`, height: "100%", background: C.green }}
          />
        </div>
        <div style={{ display: "flex", gap: 28 }}>
          {[
            [C.red, "−", "DECREASE"],
            [C.yellow, "•", "RESET"],
            [C.green, "+", "INCREASE"],
          ].map(([color, label, text]) => (
            <div key={text} style={{ flex: 1 }}>
              <div
                style={{
                  height: 112,
                  background: color,
                  borderRadius: 15,
                  color: C.bg,
                  fontSize: 76,
                  textAlign: "center",
                  lineHeight: "106px",
                }}
              >
                {label}
              </div>
              <div
                style={{
                  fontSize: 19,
                  letterSpacing: 2,
                  color,
                  marginTop: 18,
                  textAlign: "center",
                }}
              >
                {text}
              </div>
            </div>
          ))}
        </div>
        <div style={{ fontSize: 28, color: C.muted, marginTop: 34 }}>
          Yellow buttons fire once per press.
        </div>
      </div>
    </Frame>
  );
};
