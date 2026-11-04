import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, Frame, PadGrid, clamp } from "./design";
import { Narration } from "./Narration";
export const Mixer = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const fx = interpolate(t, [6, 7], [50, 100], clamp);
  const level = interpolate(t, [3.5, 4.2], [50, 85], clamp);
  return (
    <Frame
      n="05"
      title="Flip the profile. Shape the mix."
      note="USER 1 / Channel levels · headphones · mixer · FX"
    >
      <Narration id="mixer" />
      <div
        style={{
          position: "absolute",
          left: 30,
          top: 0,
          rotate: `${interpolate(t, [0, 0.6], [3, 0], clamp)}deg`,
        }}
      >
        <PadGrid
          profile="mixer_fx"
          scale={0.94}
          presses={[
            { row: 0, col: 1, start: 3.5, end: 4.2 },
            { row: 6, col: 0, start: 5, end: 5.5 },
            { row: 6, col: 2, start: 5.6, end: 5.9 },
            { row: 4, col: 2, start: 6, end: 7 },
          ]}
        />
      </div>
      <div style={{ position: "absolute", left: 810, top: 5, width: 850 }}>
        <div
          style={{
            display: "flex",
            gap: 60,
            height: 300,
            alignItems: "end",
            padding: "25px 40px",
            background: "#121a23",
            borderRadius: 20,
            border: "1px solid #34414a",
          }}
        >
          {["CHANNEL A", "CHANNEL B"].map((x, i) => (
            <div key={x} style={{ flex: 1 }}>
              <div
                style={{
                  height: 200,
                  background: "#24313a",
                  borderRadius: 10,
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    bottom: 0,
                    width: "100%",
                    height: `${i === 0 ? level : 80}%`,
                    background: i === 0 ? C.green : C.blue,
                  }}
                />
              </div>
              <div style={{ fontSize: 22, color: C.muted, marginTop: 20 }}>
                {x}
              </div>
            </div>
          ))}
        </div>
        <div
          style={{
            marginTop: 28,
            padding: 30,
            borderRadius: 20,
            border: `1px solid ${t >= 5 ? C.green : "#34414a"}`,
            background: "#121a23",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 28,
            }}
          >
            <span>EFFECTS MIX</span>
            <span style={{ color: C.green }}>
              {t >= 5 ? "● ENABLED" : "○ OFF"}
            </span>
          </div>
          <div
            style={{
              marginTop: 28,
              height: 14,
              background: "#24313a",
              borderRadius: 10,
              overflow: "hidden",
            }}
          >
            <div
              style={{ width: `${fx}%`, height: "100%", background: C.yellow }}
            />
          </div>
          <div style={{ fontSize: 50, color: C.yellow, marginTop: 16 }}>
            {Math.round(fx)}%
          </div>
        </div>
      </div>
    </Frame>
  );
};
