import React, { Suspense } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import DetectionScene from '../components/three/DetectionScene';
import './LandingPage.css';

const steps = [
  {
    title: '1. Upload site photos',
    description:
      'Drag in photos from any construction site - building facades, parking structures, tunnels, bridges. They are stored and queued automatically.',
  },
  {
    title: '2. SAM3 segments every defect',
    description:
      'A SAM3 model fine-tuned on construction defects scans each photo and segments the exact area of every issue it finds.',
  },
  {
    title: '3. Get instant results',
    description:
      'Each photo is tagged with detected defect classes, coverage and confidence - searchable and ready for reporting.',
  },
];

const defectGroups = [
  {
    title: 'Concrete damage',
    items: ['Crack', 'Spalling', 'Efflorescence', 'Exposed rebar', 'Cavity', 'Rockpocket', 'Hollow areas'],
  },
  {
    title: 'Surface & material issues',
    items: ['Rust', 'Weathering', 'Graffiti', 'Wet spots'],
  },
  {
    title: 'Structural elements',
    items: ['Bearings', 'Drainage', 'Expansion joints', 'Protective equipment'],
  },
];

const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <span className="landing-logo">AI Site Monitor</span>
        <Link to={isAuthenticated ? '/dashboard' : '/login'} className="landing-nav-cta">
          {isAuthenticated ? 'Go to Dashboard' : 'Sign in'}
        </Link>
      </nav>

      <header className="landing-hero">
        <div className="landing-hero-text">
          <h1>
            Construction site defects,
            <br />
            <span className="landing-highlight">found and segmented by AI</span>
          </h1>
          <p>
            Upload site photos and a SAM3 model fine-tuned on construction
            defects finds and outlines every crack, rust patch and weak spot
            across buildings, bridges and parking structures - so your team
            can focus on fixing problems, not searching for them.
          </p>
          <Link to={isAuthenticated ? '/dashboard' : '/login'} className="landing-cta">
            {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
          </Link>
        </div>
        <div className="landing-hero-scene">
          <Suspense fallback={<div className="landing-scene-fallback" />}>
            <DetectionScene />
          </Suspense>
        </div>
      </header>

      <section className="landing-steps">
        <h2>How it works</h2>
        <div className="landing-steps-grid">
          {steps.map((step) => (
            <div key={step.title} className="landing-step-card">
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-defects">
        <h2>What it detects</h2>
        <p className="landing-defects-intro">
          The model was trained to recognize and segment 19 defect classes
          across concrete construction sites - not just one type of structure.
        </p>
        <div className="landing-defects-grid">
          {defectGroups.map((group) => (
            <div key={group.title} className="landing-defect-group">
              <h3>{group.title}</h3>
              <ul>
                {group.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <footer className="landing-footer">
        <p>AI Object Detection &mdash; construction site defect segmentation, powered by SAM3.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
