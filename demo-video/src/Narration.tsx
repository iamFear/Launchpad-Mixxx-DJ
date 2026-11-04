import { Audio } from "@remotion/media";
import { Sequence, staticFile, useVideoConfig } from "remotion";
export const Narration = ({ id }: { id: string }) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence
      from={Math.round(0.3 * fps)}
      premountFor={fps}
      name="Female narration"
    >
      <Audio src={staticFile(`${id}.wav`)} premountFor={fps} />
    </Sequence>
  );
};
