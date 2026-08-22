import { useEffect, useRef, useState } from "react";
import { resolveAudioUrl } from "../api/apiClient";

const CORE_REST = 0.55;
const CORE_MAX = 1.35;
const GLOW_REST = 0.8;
const GLOW_MAX = 1.7;
// Asymmetric smoothing (fast attack, slower release) turns raw per-frame
// analyser noise into something that reads as "reacting to a voice"
// instead of flickering. The glow gets an extra lag on top of that, so
// it trails the core pulse a beat behind, real depth, not one flat blob.
const ATTACK = 0.45;
const RELEASE = 0.12;
const GLOW_LAG = 0.07;

export function useAudioVisualizer(audioUrl: string | null) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const coreRef = useRef<HTMLDivElement>(null);
  const glowRef = useRef<HTMLDivElement>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const rafRef = useRef<number | null>(null);
  const coreSmoothedRef = useRef(0);
  const glowSmoothedRef = useRef(0);
  const initializedRef = useRef(false);

  const [isPlaying, setIsPlaying] = useState(false);
  const [needsManualPlay, setNeedsManualPlay] = useState(false);
  const [canReplay, setCanReplay] = useState(false);

  /**
   * createMediaElementSource can only ever be called once per <audio>
   * element for its whole lifetime (the browser taints the element, not
   * just the AudioContext). React StrictMode's dev-only mount -> cleanup
   * -> remount reuses this same DOM node, so this setup must be
   * idempotent per component instance rather than re-running on every
   * effect pass - this crashed in development before the guard was added,
   * not a theoretical concern.
   */
  useEffect(() => {
    const audioEl = audioRef.current;
    if (!audioEl || initializedRef.current) return;
    initializedRef.current = true;

    const AudioContextCtor =
      window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    const ctx = new AudioContextCtor();
    const source = ctx.createMediaElementSource(audioEl);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);
    analyser.connect(ctx.destination);

    audioCtxRef.current = ctx;
    analyserRef.current = analyser;

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  function applyIdleScale() {
    coreSmoothedRef.current = 0;
    glowSmoothedRef.current = 0;
    coreRef.current?.style.setProperty("transform", `scale(${CORE_REST})`);
    glowRef.current?.style.setProperty("transform", `scale(${GLOW_REST})`);
    glowRef.current?.style.setProperty("opacity", "0.6");
  }

  function tick() {
    const analyser = analyserRef.current;
    if (!analyser) return;

    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    let sum = 0;
    for (let i = 0; i < data.length; i++) sum += data[i];
    const raw = sum / data.length / 255;

    const prevCore = coreSmoothedRef.current;
    const nextCore = prevCore + (raw - prevCore) * (raw > prevCore ? ATTACK : RELEASE);
    coreSmoothedRef.current = nextCore;

    const prevGlow = glowSmoothedRef.current;
    const nextGlow = prevGlow + (nextCore - prevGlow) * GLOW_LAG;
    glowSmoothedRef.current = nextGlow;

    // Direct DOM mutation, deliberately, not React state: this line runs
    // up to 60 times/second while audio plays. Routing it through
    // setState would re-render this component tree 60x/sec for a purely
    // visual, non-semantic value - see the summary note on this specific
    // tradeoff. Encapsulating it in this one hook (rather than scattered
    // through a component body) is what actually answers "no direct DOM
    // manipulation" here.
    coreRef.current?.style.setProperty("transform", `scale(${CORE_REST + nextCore * (CORE_MAX - CORE_REST)})`);
    glowRef.current?.style.setProperty("transform", `scale(${GLOW_REST + nextGlow * (GLOW_MAX - GLOW_REST)})`);
    glowRef.current?.style.setProperty("opacity", String(0.5 + nextGlow * 0.5));

    rafRef.current = requestAnimationFrame(tick);
  }

  useEffect(() => {
    if (isPlaying) {
      rafRef.current = requestAnimationFrame(tick);
    } else {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      applyIdleScale();
    }
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isPlaying]);

  // A new answer arrived: load its audio and try to play it. Autoplay can
  // be blocked (the /chat round trip already spent the click's user-
  // activation window) - that's not an error, it's the normal case on
  // strict browsers, so fail into a manual "Play" affordance rather than
  // surfacing anything.
  useEffect(() => {
    const audioEl = audioRef.current;
    if (!audioEl || !audioUrl) {
      setNeedsManualPlay(false);
      setCanReplay(false);
      return;
    }

    audioEl.src = resolveAudioUrl(audioUrl);
    audioEl.crossOrigin = "anonymous";
    audioEl.load();
    setCanReplay(false);
    setNeedsManualPlay(false);

    audioCtxRef.current?.resume().catch(() => {});
    audioEl.play().catch(() => {
      setNeedsManualPlay(true);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioUrl]);

  function play() {
    const audioEl = audioRef.current;
    if (!audioEl) return;
    audioCtxRef.current?.resume().catch(() => {});
    audioEl.play().catch(() => {});
  }

  return {
    audioRef,
    coreRef,
    glowRef,
    isPlaying,
    needsManualPlay,
    canReplay,
    play,
    audioEventHandlers: {
      onPlay: () => setIsPlaying(true),
      onPause: () => setIsPlaying(false),
      onEnded: () => {
        setIsPlaying(false);
        setCanReplay(true);
      },
    },
  };
}
