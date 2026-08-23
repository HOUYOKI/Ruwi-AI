import { useEffect, useState } from "react";

// Several artifact PNGs render a faint soft shadow beneath the object (alpha ~11-49) that
// extends well past the object itself. A low threshold picks up that halo and inflates the
// crop right back to nearly the original dead space. 50 was verified (by scanning real
// assets at several thresholds) as the point where the box stabilizes on the actual object.
const ALPHA_THRESHOLD = 50;
const SAMPLE_STEP = 2;
const PADDING_FRACTION = 0.04;

interface CroppedImage {
  src: string;
  aspect: number;
}

function findContentBox(ctx: CanvasRenderingContext2D, width: number, height: number) {
  const { data } = ctx.getImageData(0, 0, width, height);
  let minX = width;
  let minY = height;
  let maxX = 0;
  let maxY = 0;

  for (let y = 0; y < height; y += SAMPLE_STEP) {
    for (let x = 0; x < width; x += SAMPLE_STEP) {
      const alpha = data[(y * width + x) * 4 + 3];
      if (alpha > ALPHA_THRESHOLD) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }

  if (maxX <= minX || maxY <= minY) return null;
  return { minX, minY, maxX, maxY };
}

/**
 * Some artifact PNGs carry large transparent margins around the actual photo
 * (measured: real content can be as little as ~20% of the canvas), which left
 * a lot of dead space inside the image frame no matter how the frame itself
 * was sized. This crops to the artifact's real alpha bounding box once per
 * load. Falls back to the original, uncropped image (and its full aspect
 * ratio) if the canvas read fails for any reason (CORS, decode error, a
 * fully-transparent frame) rather than showing nothing.
 */
export function useCroppedArtifactImage(imageUrl: string): CroppedImage {
  const [result, setResult] = useState<CroppedImage>({ src: imageUrl, aspect: 1 });

  useEffect(() => {
    let cancelled = false;
    setResult({ src: imageUrl, aspect: 1 });

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      if (cancelled) return;
      const fallbackAspect = img.naturalWidth / img.naturalHeight;

      try {
        const canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("2d context unavailable");
        ctx.drawImage(img, 0, 0);

        const box = findContentBox(ctx, canvas.width, canvas.height);
        if (!box) throw new Error("no opaque content found");

        const padX = (box.maxX - box.minX) * PADDING_FRACTION;
        const padY = (box.maxY - box.minY) * PADDING_FRACTION;
        const cropX = Math.max(0, box.minX - padX);
        const cropY = Math.max(0, box.minY - padY);
        const cropWidth = Math.min(canvas.width, box.maxX + padX) - cropX;
        const cropHeight = Math.min(canvas.height, box.maxY + padY) - cropY;

        const cropped = document.createElement("canvas");
        cropped.width = cropWidth;
        cropped.height = cropHeight;
        const croppedCtx = cropped.getContext("2d");
        if (!croppedCtx) throw new Error("2d context unavailable");
        croppedCtx.drawImage(canvas, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);

        if (!cancelled) {
          setResult({ src: cropped.toDataURL("image/png"), aspect: cropWidth / cropHeight });
        }
      } catch {
        if (!cancelled) setResult({ src: imageUrl, aspect: fallbackAspect || 1 });
      }
    };
    img.onerror = () => {
      if (!cancelled) setResult({ src: imageUrl, aspect: 1 });
    };
    // A separate cache key from the plain <img> tag showing this same URL elsewhere on the
    // page: reusing that tag's cached non-CORS response here would taint the canvas read above.
    img.src = imageUrl + (imageUrl.includes("?") ? "&" : "?") + "crop-probe=1";

    return () => {
      cancelled = true;
    };
  }, [imageUrl]);

  return result;
}
