import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import maps from "./pad-maps.json";
export const C = {
  bg: "#080c12",
  white: "#f1f4ed",
  muted: "#8c9ba8",
  green: "#8ffc9d",
  red: "#ff6c65",
  yellow: "#f6d76b",
  blue: "#6dbdff",
};
export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
export const Frame: React.FC<{
  n: string;
  title: string;
  note: string;
  children: React.ReactNode;
}> = ({ n, title, note, children }) => {
  const f = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background: C.bg,
        color: C.white,
        fontFamily: "Helvetica Neue, Arial, sans-serif",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "radial-gradient(ellipse at 35% 55%, #16302a88, transparent 62%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 54,
          left: 90,
          right: 90,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 24,
          letterSpacing: 4,
          color: C.muted,
        }}
      >
        <span>LAUNCHPAD × MIXXX</span>
        <span>META HACKATHON / PROJECT DEMO</span>
      </div>
      <div
        style={{
          position: "absolute",
          top: 125,
          left: 90,
          fontSize: 83,
          fontWeight: 650,
          letterSpacing: -3,
          opacity: interpolate(f, [0, 0.45 * fps], [0, 1], clamp),
          translate: `0 ${interpolate(f, [0, 0.6 * fps], [20, 0], clamp)}px`,
        }}
      >
        <span
          style={{
            fontSize: 28,
            color: C.green,
            verticalAlign: "middle",
            marginRight: 28,
          }}
        >
          {n}
        </span>
        {title}
      </div>
      <div
        style={{
          position: "absolute",
          left: 90,
          top: 270,
          right: 90,
          bottom: 155,
          opacity: interpolate(f, [0, 0.5 * fps], [0, 1], clamp),
        }}
      >
        {children}
      </div>
      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          bottom: 65,
          borderTop: "1px solid #ffffff25",
          paddingTop: 24,
          fontSize: 30,
          color: "#b5c3c8",
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <span>{note}</span>
        <span style={{ fontSize: 18, letterSpacing: 2, color: C.muted }}>
          ANIMATED WALKTHROUGH
        </span>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          height: 5,
          background: C.green,
          width: `${(f / durationInFrames) * 100}%`,
        }}
      />
    </AbsoluteFill>
  );
};
export type Press = { row: number; col: number; start: number; end: number };
export const PadGrid: React.FC<{
  profile?: "decks" | "mixer_fx";
  presses?: Press[];
  scale?: number;
}> = ({ profile = "decks", presses = [], scale = 1 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        width: 650,
        height: 650,
        background: "#141b22",
        padding: 25,
        borderRadius: 30,
        border: "2px solid #34414a",
        boxShadow: "0 35px 80px #0009",
        scale,
        transformOrigin: "top left",
        position: "relative",
      }}
    >
      <div style={{ display: "flex", gap: 10, marginBottom: 22 }}>
        {["SESSION", "USER 1", "USER 2", "MIXER"].map((x, i) => (
          <div
            key={x}
            style={{
              flex: 1,
              borderRadius: 20,
              padding: "12px 0",
              textAlign: "center",
              fontSize: 16,
              fontWeight: 700,
              color: (profile === "decks" ? i === 2 : i === 1) ? C.bg : C.muted,
              background: (profile === "decks" ? i === 2 : i === 1)
                ? C.white
                : "#273039",
            }}
          >
            {x}
          </div>
        ))}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(8, 1fr)",
          gap: 9,
        }}
      >
        {Array.from({ length: 64 }, (_, i) => {
          const row = Math.floor(i / 8),
            col = i % 8;
          const b = maps[profile].find((p) => p.row === row && p.col === col);
          const color = b
            ? C[b.color as "red" | "green" | "yellow"]
            : "#253039";
          const held = presses.some(
            (p) =>
              p.row === row &&
              p.col === col &&
              f / fps >= p.start &&
              f / fps < p.end,
          );
          const words: Record<string, string> = {
            load: "LOAD",
            play: "PLAY",
            cue: "CUE",
            sync: "SYNC",
            pfl: "PFL",
            headmix: "MIX",
            headcue: "CUE",
            mute1: "MUTE",
            mute2: "MUTE",
            enable1: "FX",
            enableA: "→A",
            enableB: "→B",
          };
          const key = b?.control.split(".").pop() || "";
          const label = b
            ? b.role === "inc"
              ? "+"
              : b.role === "dec"
                ? "−"
                : b.role === "reset"
                  ? "•"
                  : words[key] || key
            : "";
          return (
            <div
              key={i}
              style={{
                height: 58,
                borderRadius: 8,
                background: color,
                opacity: b ? (held ? 1 : 0.42) : 0.35,
                boxShadow: held ? `0 0 35px ${color}99` : "none",
                scale: held ? 0.94 : 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#080c12",
                fontWeight: 800,
                fontSize: label.length > 2 ? 13 : 30,
                outline: held ? "3px solid #fff" : "none",
                outlineOffset: 4,
              }}
            >
              {label}
            </div>
          );
        })}
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          paddingTop: 22,
          fontSize: 17,
          letterSpacing: 3,
          color: C.muted,
        }}
      >
        <span>LAUNCHPAD MK2</span>
        <span>{profile === "decks" ? "A ← DECKS → B" : "MIXER + FX"}</span>
      </div>
    </div>
  );
};
export const Wave: React.FC<{
  color: string;
  playing?: boolean;
  seed?: number;
}> = ({ color, playing = true, seed = 1 }) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        position: "relative",
        height: 100,
        overflow: "hidden",
        background: "#080d13",
        borderRadius: 8,
      }}
    >
      <svg
        width="100%"
        height="100"
        viewBox="0 0 700 100"
        preserveAspectRatio="none"
      >
        {Array.from({ length: 130 }, (_, i) => {
          const h =
            8 +
            Math.abs(
              Math.sin((i + (playing ? f / 5 : 0)) * seed * 0.43) *
                Math.cos(i * 0.19),
            ) *
              80;
          return (
            <rect
              key={i}
              x={i * 6 - 40}
              y={50 - h / 2}
              width={3}
              height={h}
              fill={color}
              opacity={0.8}
            />
          );
        })}
      </svg>
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 0,
          height: "100%",
          width: 2,
          background: C.white,
        }}
      />
    </div>
  );
};
export const Deck: React.FC<{
  deck: string;
  status: string;
  playing: boolean;
  color: string;
}> = ({ deck, status, playing, color }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        padding: 26,
        border: "1px solid #34414a",
        borderRadius: 18,
        background: "#121a23",
        marginBottom: 20,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 18,
        }}
      >
        <span style={{ fontSize: 29, color, fontWeight: 600 }}>
          DECK {deck}
        </span>
        <span style={{ fontSize: 20, color: playing ? C.green : C.muted }}>
          {status}
        </span>
      </div>
      <Wave color={color} playing={playing} seed={deck === "A" ? 1 : 1.3} />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: 15,
          color: C.muted,
          fontSize: 22,
        }}
      >
        <span>{playing ? "▶ PLAYING" : "● READY"}</span>
        <span>
          {playing
            ? Math.floor(f / fps)
                .toString()
                .padStart(2, "0")
            : "00"}{" "}
          : 128 BPM · DEMO
        </span>
      </div>
    </div>
  );
};
export const Stat: React.FC<{
  label: string;
  value: string;
  color?: string;
}> = ({ label, value, color = C.green }) => (
  <div style={{ marginBottom: 32 }}>
    <div
      style={{
        fontSize: 22,
        color: C.muted,
        letterSpacing: 3,
        marginBottom: 10,
      }}
    >
      {label}
    </div>
    <div style={{ fontSize: 60, fontWeight: 600, letterSpacing: -2, color }}>
      {value}
    </div>
  </div>
);
