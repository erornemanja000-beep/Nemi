import { useFrame } from '@react-three/fiber'
import { useMemo, useRef, type MutableRefObject } from 'react'
import * as THREE from 'three'

type BoxProps = {
  size: [number, number, number]
  position: [number, number, number]
  material: THREE.Material
  cast?: boolean
}

function Box({ size, position, material, cast = true }: BoxProps) {
  return (
    <mesh position={position} material={material} castShadow={cast} receiveShadow>
      <boxGeometry args={size} />
    </mesh>
  )
}

const smooth = (a: number, b: number, x: number) => THREE.MathUtils.smoothstep(x, a, b)

/**
 * Stylised modernist villa built from primitives: glazed ground floor (front and back),
 * a cantilevered upper volume, pool, deck and cypress trees. Front faces +z.
 * `progress` (0–1) drives the sliding doors and the dusk lighting inside.
 */
export function Villa({ progress, lite }: { progress: MutableRefObject<number>; lite: boolean }) {
  const mats = useMemo(() => {
    const concrete = new THREE.MeshStandardMaterial({ color: '#d9d4cb', roughness: 0.92 })
    const render = new THREE.MeshStandardMaterial({ color: '#efebe4', roughness: 0.85 })
    const dark = new THREE.MeshStandardMaterial({ color: '#1d1b18', roughness: 0.6, metalness: 0.4 })
    const timber = new THREE.MeshStandardMaterial({ color: '#8a5a3b', roughness: 0.75 })
    const floor = new THREE.MeshStandardMaterial({ color: '#b89a78', roughness: 0.6 })
    const deck = new THREE.MeshStandardMaterial({ color: '#cfc6b6', roughness: 0.95 })
    const lawn = new THREE.MeshStandardMaterial({ color: '#4a4a32', roughness: 1 })
    const glass = lite
      ? new THREE.MeshStandardMaterial({ color: '#8fa6b4', transparent: true, opacity: 0.22, roughness: 0.05, metalness: 0.6 })
      : new THREE.MeshPhysicalMaterial({ color: '#9fb4c0', transparent: true, opacity: 0.2, roughness: 0.04, metalness: 0.15, clearcoat: 1, clearcoatRoughness: 0.05 })
    const water = new THREE.MeshStandardMaterial({ color: '#2c7f8c', roughness: 0.08, metalness: 0.3, emissive: new THREE.Color('#1aa7b8'), emissiveIntensity: 0.05 })
    const windowGlow = new THREE.MeshStandardMaterial({ color: '#2a2622', emissive: new THREE.Color('#ffb36b'), emissiveIntensity: 0, roughness: 0.3 })
    const sofa = new THREE.MeshStandardMaterial({ color: '#d8cdbd', roughness: 0.95 })
    const rug = new THREE.MeshStandardMaterial({ color: '#6b4f3a', roughness: 1 })
    const art = new THREE.MeshStandardMaterial({ color: '#e07a3f', roughness: 0.8, emissive: new THREE.Color('#e07a3f'), emissiveIntensity: 0.1 })
    const bulb = new THREE.MeshStandardMaterial({ color: '#fff1d6', emissive: new THREE.Color('#ffc98a'), emissiveIntensity: 0 })
    const tree = new THREE.MeshStandardMaterial({ color: '#2f3a26', roughness: 1 })
    const trunk = new THREE.MeshStandardMaterial({ color: '#4b3a2b', roughness: 1 })
    return { concrete, render, dark, timber, floor, deck, lawn, glass, water, windowGlow, sofa, rug, art, bulb, tree, trunk }
  }, [lite])

  const doorL = useRef<THREE.Mesh>(null)
  const doorR = useRef<THREE.Mesh>(null)
  const lamps = useRef<THREE.PointLight[]>([])

  useFrame(({ clock }) => {
    const p = progress.current
    const open = smooth(0.62, 0.8, p)
    if (doorL.current) doorL.current.position.x = -0.5 - open * 1.05
    if (doorR.current) doorR.current.position.x = 0.5 + open * 1.05
    const dusk = smooth(0.35, 0.85, p)
    mats.windowGlow.emissiveIntensity = dusk * 2.2
    mats.bulb.emissiveIntensity = 0.3 + dusk * 4
    mats.water.emissiveIntensity = 0.05 + dusk * 0.9
    mats.art.emissiveIntensity = 0.1 + dusk * 0.4
    mats.water.color.setHSL(0.52, 0.5, 0.33 + Math.sin(clock.elapsedTime * 1.4) * 0.015)
    lamps.current.forEach((l) => (l.intensity = 2 + dusk * 45))
  })

  const trees: [number, number, number][] = [
    [-13, 0, -8], [-15, 0, -2], [-12.5, 0, 4], [13, 0, -9], [15.5, 0, -3], [12, 0, 6.5], [-6, 0, -19], [6, 0, -21], [14, 0, -17], [-17, 0, 9],
  ]

  return (
    <group>
      {/* ground, deck and pool */}
      <mesh rotation-x={-Math.PI / 2} receiveShadow material={mats.lawn}>
        <circleGeometry args={[160, 48]} />
      </mesh>
      <Box size={[26, 0.08, 22]} position={[0, 0.04, 2]} material={mats.deck} cast={false} />
      <Box size={[8.6, 0.12, 4.6]} position={[-5, 0.07, 9]} material={mats.dark} cast={false} />
      <mesh position={[-5, 0.135, 9]} rotation-x={-Math.PI / 2} material={mats.water}>
        <planeGeometry args={[8, 4]} />
      </mesh>

      {/* ground floor slab, piers and walls */}
      <Box size={[15, 0.3, 9.6]} position={[0, 0.23, 0]} material={mats.concrete} />
      <Box size={[14.4, 0.02, 9]} position={[0, 0.39, 0]} material={mats.floor} cast={false} />
      <Box size={[0.4, 3.2, 9]} position={[-7.1, 1.9, 0]} material={mats.concrete} />
      <Box size={[0.4, 3.2, 9]} position={[7.1, 1.9, 0]} material={mats.concrete} />
      <Box size={[2.6, 3.2, 0.3]} position={[-5.6, 1.9, 4.45]} material={mats.timber} />
      {[-4.3, -1.2, 1.2, 4.2].map((x) => (
        <Box key={x} size={[0.12, 3.2, 0.12]} position={[x, 1.9, 4.5]} material={mats.dark} />
      ))}
      {[-4.3, 0, 4.2].map((x) => (
        <Box key={`b${x}`} size={[0.12, 3.2, 0.12]} position={[x, 1.9, -4.5]} material={mats.dark} />
      ))}

      {/* front glazing with the sliding entrance at x = 0 */}
      <mesh position={[-2.75, 1.9, 4.5]} material={mats.glass}>
        <planeGeometry args={[3.1, 3.2]} />
      </mesh>
      <mesh position={[2.7, 1.9, 4.5]} material={mats.glass}>
        <planeGeometry args={[3, 3.2]} />
      </mesh>
      <mesh position={[5.65, 1.9, 4.5]} material={mats.glass}>
        <planeGeometry args={[2.9, 3.2]} />
      </mesh>
      <mesh ref={doorL} position={[-0.5, 1.9, 4.56]} material={mats.glass}>
        <planeGeometry args={[1.05, 3.2]} />
      </mesh>
      <mesh ref={doorR} position={[0.5, 1.9, 4.6]} material={mats.glass}>
        <planeGeometry args={[1.05, 3.2]} />
      </mesh>
      {/* back glazing (the sunset view at the end of the camera path) */}
      <mesh position={[0, 1.9, -4.5]} rotation-y={Math.PI} material={mats.glass}>
        <planeGeometry args={[14, 3.2]} />
      </mesh>

      {/* upper slab, cantilevered volume and roof */}
      <Box size={[16.4, 0.42, 10.6]} position={[0, 3.71, 0.4]} material={mats.render} />
      <Box size={[12, 3, 8]} position={[3, 5.42, -0.4]} material={mats.render} />
      <mesh position={[3, 5.2, 3.61]} material={mats.windowGlow}>
        <planeGeometry args={[10, 1.3]} />
      </mesh>
      <mesh position={[9.01, 5.2, -0.4]} rotation-y={Math.PI / 2} material={mats.windowGlow}>
        <planeGeometry args={[6, 1.3]} />
      </mesh>
      <Box size={[12.8, 0.24, 8.8]} position={[3, 7.04, -0.4]} material={mats.concrete} />

      {/* interior */}
      <Box size={[4.4, 0.02, 2.8]} position={[-0.6, 0.41, -1]} material={mats.rug} cast={false} />
      <Box size={[3.2, 0.5, 1]} position={[-0.6, 0.65, -2.4]} material={mats.sofa} />
      <Box size={[3.2, 0.5, 0.3]} position={[-0.6, 1.05, -2.85]} material={mats.sofa} />
      <Box size={[1.4, 0.32, 0.8]} position={[-0.6, 0.56, -0.9]} material={mats.dark} />
      <Box size={[3, 0.95, 1]} position={[4.4, 0.88, -0.4]} material={mats.render} />
      <Box size={[0.08, 2, 3]} position={[-6.86, 1.9, -1]} material={mats.art} />
      {[3.4, 4.4, 5.4].map((x) => (
        <mesh key={x} position={[x, 2.75, -0.4]} material={mats.bulb}>
          <sphereGeometry args={[0.12, 12, 12]} />
        </mesh>
      ))}
      <pointLight ref={(l) => { if (l) lamps.current[0] = l }} position={[4.4, 2.6, -0.4]} color="#ffbe7a" distance={9} decay={2} />
      <pointLight ref={(l) => { if (l) lamps.current[1] = l }} position={[-2.5, 2.8, -0.8]} color="#ffb06b" distance={10} decay={2} />

      {/* cypress trees */}
      {trees.map(([x, , z], i) => {
        const h = 5 + ((i * 37) % 5) * 0.6
        return (
          <group key={i} position={[x, 0, z]}>
            <mesh position={[0, 0.5, 0]} material={mats.trunk} castShadow>
              <cylinderGeometry args={[0.12, 0.15, 1, 6]} />
            </mesh>
            <mesh position={[0, 0.9 + h / 2, 0]} material={mats.tree} castShadow scale={[1, 1, 1]}>
              <coneGeometry args={[0.85, h, lite ? 6 : 10]} />
            </mesh>
          </group>
        )
      })}

      {/* far hills */}
      {[
        [-70, -90, 34],
        [-10, -110, 40],
        [60, -95, 30],
        [110, -40, 26],
      ].map(([x, z, r], i) => (
        <mesh key={i} position={[x, -r * 0.62, z]} material={mats.tree} scale={[1.6, 1, 1]}>
          <sphereGeometry args={[r, 16, 10]} />
        </mesh>
      ))}
    </group>
  )
}
