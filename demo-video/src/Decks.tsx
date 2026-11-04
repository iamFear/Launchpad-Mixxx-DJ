import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, Frame, PadGrid, Deck } from "./design";
import { Narration } from "./Narration";
export const Decks = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  return (
    <Frame
      n="02"
      title="Load. Cue. Sync. Play."
      note="USER 2 / Deck A on the left · Deck B on the right"
    >
      <Narration id="decks" />
      <div style={{ position: "absolute", left: 30, top: 0 }}>
        <PadGrid
          scale={0.94}
          presses={[
            { row: 0, col: 0, start: 3, end: 3.55 },
            { row: 0, col: 1, start: 4, end: 4.55 },
            { row: 0, col: 4, start: 5.7, end: 6.2 },
            { row: 0, col: 6, start: 6.5, end: 7 },
            { row: 0, col: 7, start: 7.2, end: 7.7 },
            { row: 0, col: 5, start: 8, end: 8.55 },
          ]}
        />
      </div>
      <div style={{ position: "absolute", left: 810, top: 5, width: 880 }}>
        <Deck
          deck="A"
          status={t < 3 ? "SELECT TRACK" : t < 4 ? "LOADED" : "PLAYING"}
          playing={t >= 4}
          color={C.green}
        />
        <Deck
          deck="B"
          status={
            t < 5.7
              ? "NEXT TRACK"
              : t < 6.5
                ? "LOADED"
                : t < 7.2
                  ? "CUED"
                  : t < 8
                    ? "SYNCED"
                    : "PLAYING"
          }
          playing={t >= 8}
          color={C.blue}
        />
        <div style={{ fontSize: 24, color: C.muted, marginTop: 28 }}>
          Illustrative deck view · actual project pad mapping
        </div>
      </div>
    </Frame>
  );
};
