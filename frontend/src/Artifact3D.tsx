import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import type { Artifact } from './types'

type Props = { artifact: Artifact; autoRotate?: boolean; onLoaded?: (ok: boolean) => void }

export default function Artifact3D({ artifact, autoRotate = false, onLoaded }: Props) {
  const host = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = host.current
    if (!el) return
    let disposed = false
    const scene = new THREE.Scene()
    scene.background = new THREE.Color('#0b0e0d')

    const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 100)
    camera.position.set(0, 0.05, 3.2)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.35
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFShadowMap
    el.appendChild(renderer.domElement)

    const hemi = new THREE.HemisphereLight('#fff7df', '#3e5a4d', 3.2)
    scene.add(hemi)
    const key = new THREE.DirectionalLight('#fff2cf', 5.5)
    key.position.set(3, 4, 4)
    key.castShadow = true
    scene.add(key)
    const fill = new THREE.DirectionalLight('#9ac7ae', 2.5)
    fill.position.set(-3, 1, 2)
    scene.add(fill)
    const rim = new THREE.PointLight('#d7c08a', 1.7, 7)
    rim.position.set(-2, 1.2, 2)
    scene.add(rim)

    const stage = new THREE.Mesh(
      new THREE.CylinderGeometry(1.28, 1.45, 0.09, 96),
      new THREE.MeshStandardMaterial({ color: '#151b18', roughness: 0.7, metalness: 0.05 })
    )
    stage.position.y = -1.03
    stage.receiveShadow = true
    scene.add(stage)

    const root = new THREE.Group()
    scene.add(root)
    let baseScale = 1

    const fit = (obj: THREE.Object3D) => {
      const box = new THREE.Box3().setFromObject(obj)
      const size = box.getSize(new THREE.Vector3())
      const center = box.getCenter(new THREE.Vector3())
      obj.position.sub(center)
      const max = Math.max(size.x, size.y, size.z) || 1
      baseScale = 1.65 / max
      obj.scale.setScalar(baseScale)
      obj.traverse((child) => {
        if (!(child instanceof THREE.Mesh)) return
        child.castShadow = true
        child.receiveShadow = true
        const materials = Array.isArray(child.material) ? child.material : [child.material]
        materials.forEach((m) => {
          m.side = THREE.DoubleSide
          m.needsUpdate = true
        })
      })
    }

    const loader = new GLTFLoader()
    loader.load(
      artifact.model,
      (gltf) => {
        if (disposed) return
        root.add(gltf.scene)
        fit(gltf.scene)
        onLoaded?.(true)
      },
      undefined,
      () => {
        if (disposed) return
        const tex = new THREE.TextureLoader().load(artifact.image)
        tex.colorSpace = THREE.SRGBColorSpace
        const mat = new THREE.MeshStandardMaterial({ map: tex, transparent: true, alphaTest: .04, side: THREE.DoubleSide, roughness: .5, metalness: .04 })
        const plane = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 1.82), mat)
        root.add(plane)
        fit(plane)
        onLoaded?.(false)
      }
    )

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.07
    controls.enablePan = false
    controls.minDistance = 0.8
    controls.maxDistance = 6
    controls.rotateSpeed = 0.62
    controls.zoomSpeed = 0.9
    controls.autoRotate = autoRotate
    controls.autoRotateSpeed = 0.3

    const resize = () => {
      const w = Math.max(1, el.clientWidth)
      const h = Math.max(1, el.clientHeight)
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h, false)
    }
    const ro = new ResizeObserver(resize)
    ro.observe(el)
    resize()

    let raf = 0
    const animate = () => {
      if (disposed) return
      raf = requestAnimationFrame(animate)
      root.position.y = Math.sin(performance.now() * 0.0007) * 0.012
      root.scale.setScalar(baseScale * (1 + Math.sin(performance.now() * 0.001) * 0.008))
      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    return () => {
      disposed = true
      cancelAnimationFrame(raf)
      ro.disconnect()
      controls.dispose()
      renderer.dispose()
      if (renderer.domElement.parentNode === el) el.removeChild(renderer.domElement)
      scene.traverse((obj) => {
        if (!(obj instanceof THREE.Mesh)) return
        obj.geometry.dispose()
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material]
        mats.forEach((m) => {
          m.map?.dispose()
          m.dispose()
        })
      })
    }
  }, [artifact, autoRotate, onLoaded])

  return <div ref={host} className="artifactCanvas" aria-label={`عرض ثلاثي الأبعاد: ${artifact.name_ar}`} />
}
