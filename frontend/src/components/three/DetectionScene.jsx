import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles, Trail } from '@react-three/drei';

// A simple low-poly bridge: deck + two pillars.
const Bridge = () => (
  <group position={[0, -0.6, 0]}>
    <mesh position={[0, 0, 0]}>
      <boxGeometry args={[4.4, 0.18, 0.9]} />
      <meshStandardMaterial color="#9aa3b2" roughness={0.6} metalness={0.1} />
    </mesh>
    <mesh position={[-1.6, -0.7, 0]}>
      <boxGeometry args={[0.3, 1.3, 0.7]} />
      <meshStandardMaterial color="#7d8696" roughness={0.6} metalness={0.1} />
    </mesh>
    <mesh position={[1.6, -0.7, 0]}>
      <boxGeometry args={[0.3, 1.3, 0.7]} />
      <meshStandardMaterial color="#7d8696" roughness={0.6} metalness={0.1} />
    </mesh>
  </group>
);

// Pulsing markers on the bridge deck representing detected damage classes.
const DamageMarker = ({ position, color }) => {
  const ref = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const scale = 1 + Math.sin(t * 2.5 + position[0]) * 0.25;
    ref.current.scale.setScalar(scale);
  });
  return (
    <mesh ref={ref} position={position}>
      <sphereGeometry args={[0.09, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.2} />
    </mesh>
  );
};

// The AI "core" - a wireframe icosahedron that hovers above the bridge,
// rotating to represent the SAM3 model analyzing the scene.
const AICore = () => {
  const ref = useRef();
  useFrame((_, delta) => {
    ref.current.rotation.x += delta * 0.35;
    ref.current.rotation.y += delta * 0.5;
  });
  return (
    <Float speed={1.2} rotationIntensity={0.2} floatIntensity={0.8}>
      <group ref={ref} position={[0, 1.6, 0]}>
        <mesh>
          <icosahedronGeometry args={[0.55, 1]} />
          <meshStandardMaterial
            color="#4f46e5"
            emissive="#6366f1"
            emissiveIntensity={0.6}
            wireframe
          />
        </mesh>
        <mesh>
          <icosahedronGeometry args={[0.3, 0]} />
          <meshStandardMaterial color="#818cf8" emissive="#818cf8" emissiveIntensity={1} />
        </mesh>
      </group>
    </Float>
  );
};

// A scanning ring that sweeps up and down through the bridge.
const ScanRing = () => {
  const ref = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    ref.current.position.y = -0.6 + Math.sin(t * 0.8) * 1.1;
    ref.current.rotation.z = t * 0.6;
  });
  return (
    <mesh ref={ref} rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[1.9, 0.015, 16, 64]} />
      <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={1.5} transparent opacity={0.7} />
    </mesh>
  );
};

const Scene = () => {
  const group = useRef();
  useFrame((_, delta) => {
    group.current.rotation.y += delta * 0.12;
  });

  return (
    <group ref={group}>
      <Bridge />
      <DamageMarker position={[-1.1, -0.48, 0.3]} color="#ef4444" />
      <DamageMarker position={[0.4, -0.48, -0.25]} color="#f59e0b" />
      <DamageMarker position={[1.3, -0.48, 0.2]} color="#eab308" />
      <ScanRing />
      <AICore />
      <Trail width={1} length={4} color="#22d3ee" attenuation={(t) => t * t}>
        <mesh visible={false} position={[0, 1.6, 0]}>
          <sphereGeometry args={[0.01]} />
        </mesh>
      </Trail>
    </group>
  );
};

const DetectionScene = () => (
  <Canvas camera={{ position: [0, 1.2, 5.2], fov: 42 }} dpr={[1, 1.5]}>
    <ambientLight intensity={0.55} />
    <directionalLight position={[3, 4, 2]} intensity={1.1} />
    <pointLight position={[-3, 2, -2]} intensity={0.6} color="#6366f1" />
    <Sparkles count={40} scale={[6, 4, 6]} size={2} speed={0.3} color="#a5b4fc" />
    <Scene />
  </Canvas>
);

export default DetectionScene;
