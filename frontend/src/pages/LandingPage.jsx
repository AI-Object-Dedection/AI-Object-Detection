import React, { Suspense } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import DetectionScene from '../components/three/DetectionScene';
import './LandingPage.css';

const steps = [
  {
    title: '1. Upload site photos',
    description:
      'Drag in inspection photos from the bridge or job site. They are stored and queued automatically.',
  },
  {
    title: '2. AI analyzes every image',
    description:
      'A fine-tuned SAM3 segmentation model scans each photo for 19 types of structural damage - cracks, rust, spalling and more.',
  },
  {
    title: '3. Get instant results',
    description:
      'Each photo is tagged with detected damage classes, coverage and confidence - searchable and ready for reporting.',
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
            Bridge inspection,
            <br />
            <span className="landing-highlight">analyzed by AI</span>
          </h1>
          <p>
            Upload site photos and let a SAM3-powered detector find structural
            damage automatically - so your team can focus on fixing problems,
            not searching for them.
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

      <footer className="landing-footer">
        <p>AI Object Detection &mdash; bridge damage analysis, powered by SAM3.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
