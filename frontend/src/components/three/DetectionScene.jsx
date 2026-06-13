import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles, Html, Environment, ContactShadows } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import './DetectionScene.css';

// A building under construction: a finished lower block + an open steel
// frame on top, with rebar still exposed - the kind of structure the
// detector is trained to scan.
const Structure = () => (
  <group position={[-0.6, -0.9, 0]}>
    {/* Finished lower floors */}
    <mesh position={[0, 0.7, 0]}>
      <boxGeometry args={[1.6, 1.4, 1]} />
      <meshStandardMaterial color="#9aa3b2" roughness={0.75} metalness={0.05} />
    </mesh>

    {/* Open steel frame of the floor under construction */}
    <mesh position={[0, 1.85, 0]}>
      <boxGeometry args={[1.6, 0.9, 1]} />
      <meshStandardMaterial color="#cbd5e1" roughness={0.3} metalness={0.6} wireframe />
    </mesh>

    {/* Exposed rebar */}
    {[-0.6, -0.2, 0.2, 0.6].map((x) => (
      <mesh key={x} position={[x, 2.35, 0.35]}>
        <cylinderGeometry args={[0.025, 0.025, 0.7, 8]} />
        <meshStandardMaterial color="#b45309" roughness={0.4} metalness={0.7} />
      </mesh>
    ))}
  </group>
);

// A small tower crane beside the structure.
const Crane = () => (
  <group position={[1.5, -0.9, -0.2]}>
    <mesh position={[0, 1.6, 0]}>
      <cylinderGeometry args={[0.05, 0.05, 3.2, 12]} />
      <meshStandardMaterial color="#f59e0b" roughness={0.4} metalness={0.5} />
    </mesh>
    <mesh position={[-0.85, 3.1, 0]}>
      <boxGeometry args={[1.9, 0.08, 0.08]} />
      <meshStandardMaterial color="#f59e0b" roughness={0.4} metalness={0.5} />
    </mesh>
    <mesh position={[0.4, 3.1, 0]}>
      <boxGeometry args={[0.7, 0.08, 0.08]} />
      <meshStandardMaterial color="#f59e0b" roughness={0.4} metalness={0.5} />
    </mesh>
    <mesh position={[-1.6, 2.85, 0]}>
      <cylinderGeometry args={[0.012, 0.012, 0.5, 6]} />
      <meshStandardMaterial color="#9ca3af" />
    </mesh>
    <mesh position={[-1.6, 2.6, 0]}>
      <boxGeometry args={[0.12, 0.1, 0.12]} />
      <meshStandardMaterial color="#475569" />
    </mesh>
  </group>
);

// A pulsing, labeled marker for one detected damage class.
const DamageMarker = ({ position, color, label, confidence }) => {
  const ref = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    ref.current.scale.setScalar(1 + Math.sin(t * 2.5 + position[0]) * 0.25);
  });
  return (
    <group position={position}>
      <mesh ref={ref}>
        <sphereGeometry args={[0.075, 16, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.4} />
      </mesh>
      <Html distanceFactor={8} center>
        <div className="scene-label" style={{ '--marker-color': color }}>
          <span className="scene-label-dot" />
          {label}
          <em>{confidence}</em>
        </div>
      </Html>
    </group>
  );
};

// The AI "core" - a wireframe icosahedron that hovers above the site,
// representing the segmentation model analyzing every photo.
const AICore = () => {
  const ref = useRef();
  useFrame((_, delta) => {
    ref.current.rotation.x += delta * 0.35;
    ref.current.rotation.y += delta * 0.5;
  });
  return (
    <Float speed={1.2} rotationIntensity={0.2} floatIntensity={0.8}>
      <group ref={ref} position={[0.2, 2.6, 0]}>
        <mesh>
          <icosahedronGeometry args={[0.5, 1]} />
          <meshStandardMaterial
            color="#4f46e5"
            emissive="#6366f1"
            emissiveIntensity={0.6}
            wireframe
          />
        </mesh>
        <mesh>
          <icosahedronGeometry args={[0.26, 0]} />
          <meshStandardMaterial color="#818cf8" emissive="#818cf8" emissiveIntensity={1} />
        </mesh>
      </group>
    </Float>
  );
};

// A scanning plane that sweeps up and down across the structure.
const ScanPlane = () => {
  const ref = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    ref.current.position.y = -1.6 + ((Math.sin(t * 0.6) + 1) / 2) * 3.6;
  });
  return (
    <mesh ref={ref} rotation={[-Math.PI / 2, 0, 0]} position={[-0.6, 0, 0]}>
      <planeGeometry args={[2.4, 1.6]} />
      <meshBasicMaterial color="#22d3ee" transparent opacity={0.18} side={2} />
    </mesh>
  );
};

const Scene = () => {
  const group = useRef();
  useFrame((_, delta) => {
    group.current.rotation.y += delta * 0.1;
  });

  return (
    <group ref={group}>
      <Structure />
      <Crane />
      <DamageMarker position={[-1.3, 0.4, 0.55]} color="#ef4444" label="Crack" confidence="0.94" />
      <DamageMarker position={[-0.05, -0.55, 0.55]} color="#f59e0b" label="Rust" confidence="0.88" />
      <DamageMarker position={[0.55, 0.85, 0.55]} color="#eab308" label="Spalling" confidence="0.91" />
      <DamageMarker position={[-1.2, -0.85, 0.55]} color="#38bdf8" label="Efflorescence" confidence="0.82" />
      <ScanPlane />
      <AICore />
    </group>
  );
};

const DetectionScene = () => (
  <Canvas camera={{ position: [0, 1, 6.5], fov: 38 }} dpr={[1, 1.5]}>
    <ambientLight intensity={0.4} />
    <directionalLight position={[3, 5, 2]} intensity={1.2} />
    <pointLight position={[-3, 2, -2]} intensity={0.5} color="#6366f1" />
    <Environment preset="city" />
    <Sparkles count={40} scale={[7, 5, 7]} size={2} speed={0.3} color="#a5b4fc" />
    <Scene />
    <ContactShadows position={[0, -1.85, 0]} opacity={0.5} scale={10} blur={2.5} far={3} />
    <EffectComposer>
      <Bloom intensity={0.6} luminanceThreshold={0.25} luminanceSmoothing={0.9} mipmapBlur />
      <Vignette eskil={false} offset={0.3} darkness={0.6} />
    </EffectComposer>
  </Canvas>
);

export default DetectionScene;
