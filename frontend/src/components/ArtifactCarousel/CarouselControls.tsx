interface CarouselControlsProps {
  current: number;
  total: number;
}

export default function CarouselControls({ current, total }: CarouselControlsProps) {
  return (
    <p className="w-20 text-center text-xs tracking-[0.2em] text-text-muted uppercase tabular-nums whitespace-nowrap">
      {current} / {total}
    </p>
  );
}
