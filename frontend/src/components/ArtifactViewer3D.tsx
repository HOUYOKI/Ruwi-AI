import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export default function ArtifactViewer3D({ imageUrl, alt }: { imageUrl: string; alt: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewerFailed, setViewerFailed] = useState(false);

  useEffect(() => {
    setViewerFailed(false);
  }, [imageUrl]);

  useEffect(() => {
    if (viewerFailed) return;
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0b);

    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      100,
    );
    camera.position.set(0, 0, 3.2);

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch (error) {
      console.error("Ruwi: WebGL is unavailable; using the artifact image", error);
      setViewerFailed(true);
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const keyLight = new THREE.DirectionalLight(0xfff2d9, 1.1);
    keyLight.position.set(2, 3, 4);
    scene.add(keyLight);
    const rimLight = new THREE.DirectionalLight(0xc084fc, 0.4);
    rimLight.position.set(-3, -1, -2);
    scene.add(rimLight);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 1.5;
    controls.maxDistance = 6;
    controls.enablePan = false;

    let mesh: THREE.Mesh | null = null;
    let objectUrl: string | null = null;
    const abortController = new AbortController();

    // Fetch the PNG as a blob and load the texture from a same-origin blob:
    // URL rather than the cross-origin backend URL directly. This avoids a
    // browser cache-partitioning footgun: an <img> tag elsewhere on the page
    // may have already cached this same URL as an opaque (no-cors) response,
    // and WebGL's texImage2D requires a CORS-validated load — reusing that
    // opaque cache entry silently fails with a generic error event.
    fetch(imageUrl, { signal: abortController.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch artifact image (${res.status})`);
        return res.blob();
      })
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        new THREE.TextureLoader().load(
          objectUrl,
          (texture) => {
            texture.colorSpace = THREE.SRGBColorSpace;
            const aspect = texture.image.width / texture.image.height;
            const height = 2.2;
            const geometry = new THREE.PlaneGeometry(height * aspect, height);
            const material = new THREE.MeshStandardMaterial({
              map: texture,
              transparent: true,
              side: THREE.DoubleSide,
            });
            mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);
          },
          undefined,
          () => setViewerFailed(true),
        );
      })
      .catch((err) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        console.error("Ruwi: failed to load artifact texture", err);
        setViewerFailed(true);
      });

    let frameId: number;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      if (mesh) mesh.rotation.y += 0.0025;
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      abortController.abort();
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", handleResize);
      controls.dispose();
      renderer.dispose();
      mesh?.geometry.dispose();
      if (mesh?.material) {
        const material = mesh.material as THREE.MeshStandardMaterial;
        material.map?.dispose();
        material.dispose();
      }
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      if (renderer.domElement.parentElement === container) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [imageUrl, viewerFailed]);

  return (
    <div
      ref={containerRef}
      role="img"
      aria-label={alt}
      className="relative aspect-square w-full overflow-hidden rounded-sm border border-neutral-800 bg-neutral-950"
    >
      {viewerFailed && (
        <img
          src={imageUrl}
          alt={alt}
          className="absolute inset-0 h-full w-full object-contain p-6"
        />
      )}
    </div>
  );
}
