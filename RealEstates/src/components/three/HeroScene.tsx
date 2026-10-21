import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { useEffect, useMemo, useRef, type MutableRefObject } from 'react'
import * as THREE from 'three'
import { Sky } from 'three/examples/jsm/objects/Sky.js'
import { Villa } from './Villa'

type Props = {
  progress: MutableRefObject<number>
  pointer: MutableRefObject<{ x: number; y: number }>
  active: boolean
  lite: boolean
  onReady?: () => void
}

const v = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z)

// Camera orbits from the front-right, swings across the pool, lines up with the door and walks in.
const camPath = new THREE.CatmullRomCurve3(
  [v(24, 10, 26), v(8, 8.5, 31), v(-14, 6, 24), v(-8, 3, 15.5), v(0, 1.9, 11), v(0, 1.9, 5.6), v(0, 2.15, 1.4)],
  false,
  'centripetal',
)
const lookPath = new THREE.CatmullRomCurve3(
  [v(0, 2.6, 0), v(-1, 2.6, 1), v(-2, 2.2, 2), v(0, 2, 3), v(0, 1.8, 3.5), v(0, 1.8, 0), v(0, 1.75, -9)],
  false,
  'centripetal',
)

const SUN_START = v(28, 55, 30).normalize()
const SUN_END = v(-6, -0.4, -100).normalize()
const sunDay = new THREE.Color('#fff4e2')
const sunGold = new THREE.Color('#ffa25c')
const sunDusk = new THREE.Color('#ff6b3d')
const fogDay = new THREE.Color('#bfd0dc')
const fogDusk = new THREE.Color('#5a4a52')

function Rig({ progress, pointer }: Pick<Props, 'progress' | 'pointer'>) {
  const { camera, scene, gl, size } = useThree()
  const sun = useRef<THREE.DirectionalLight>(null)
  const hemi = useRef<THREE.HemisphereLight>(null)
  const sky = useMemo(() => {
    const s = new Sky()
    s.scale.setScalar(4000)
    const u = s.material.uniforms
    u.mieCoefficient.value = 0.006
    u.mieDirectionalG.value = 0.86
    return s
  }, [])
  const smoothP = useRef(0)
  const look = useMemo(() => new THREE.Vector3(), [])
  const pos = useMemo(() => new THREE.Vector3(), [])
  const sunDir = useMemo(() => new THREE.Vector3(), [])
  const tmp = useMemo(() => new THREE.Color(), [])

  useEffect(() => {
    scene.fog = new THREE.Fog(fogDay, 40, 190)
    return () => {
      scene.fog = null
    }
  }, [scene])

  useFrame((_, dt) => {
    // ease the scroll value so the camera glides even with coarse wheel steps
    smoothP.current = THREE.MathUtils.damp(smoothP.current, progress.current, 4, dt)
    const p = smoothP.current
    camPath.getPointAt(p, pos)
    lookPath.getPointAt(p, look)
    // portrait screens need the camera further back on the exterior shots
    const aspect = size.width / size.height
    if (aspect < 1) pos.multiplyScalar(1 + (1 - aspect) * 0.55 * (1 - THREE.MathUtils.smoothstep(p, 0.55, 0.8)))
    const parallax = 1 - THREE.MathUtils.smoothstep(p, 0.7, 0.9)
    camera.position.set(pos.x + pointer.current.x * 1.2 * parallax, pos.y + pointer.current.y * 0.6 * parallax, pos.z)
    camera.lookAt(look)

    // sun travels from high noon to below the horizon behind the house
    const t = THREE.MathUtils.smoothstep(p, 0.05, 0.95)
    sunDir.copy(SUN_START).lerp(SUN_END, t).normalize()
    if (sun.current) {
      sun.current.position.copy(sunDir).multiplyScalar(60)
      tmp.copy(sunDay).lerp(sunGold, Math.min(1, t * 1.6))
      if (t > 0.6) tmp.lerp(sunDusk, (t - 0.6) / 0.4)
      sun.current.color.copy(tmp)
      sun.current.intensity = THREE.MathUtils.lerp(3.2, 0.5, t)
    }
    if (hemi.current) hemi.current.intensity = THREE.MathUtils.lerp(1.1, 0.35, t)
    const mat = sky.material
    {
      mat.uniforms.sunPosition.value.copy(sunDir)
      mat.uniforms.rayleigh.value = THREE.MathUtils.lerp(2.4, 3.6, t)
      mat.uniforms.turbidity.value = THREE.MathUtils.lerp(3, 9, t)
    }
    if (scene.fog instanceof THREE.Fog) scene.fog.color.copy(fogDay).lerp(fogDusk, t)
    gl.toneMappingExposure = THREE.MathUtils.lerp(0.78, 0.55, t)
  })

  return (
    <>
      <primitive object={sky} />
      <hemisphereLight ref={hemi} args={['#dfe8f0', '#3d3528', 1]} />
      <directionalLight
        ref={sun}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-22}
        shadow-camera-right={22}
        shadow-camera-top={22}
        shadow-camera-bottom={-22}
        shadow-camera-far={140}
        shadow-bias={-0.0004}
      />
    </>
  )
}

export default function HeroScene({ progress, pointer, active, lite, onReady }: Props) {
  return (
    <Canvas
      shadows={!lite}
      dpr={lite ? [1, 1.5] : [1, 2]}
      frameloop={active ? 'always' : 'never'}
      camera={{ fov: lite ? 50 : 38, near: 0.1, far: 5000, position: [24, 10, 26] }}
      gl={{ antialias: !lite, powerPreference: 'high-performance' }}
      onCreated={() => requestAnimationFrame(() => onReady?.())}
      aria-hidden="true"
    >
      <Rig progress={progress} pointer={pointer} />
      <Villa progress={progress} lite={lite} />
    </Canvas>
  )
}
