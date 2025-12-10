import React from "react";
import Image from "next/image";

// You can swap this for your preferred hero/digital twin illustration
import digitalTwinBanner from "../public/digital-twin-hero.png";

export default function DigitalTwinSpotlight() {
  return (
    <main className="digital-twin-spotlight" style={{ fontFamily: 'sans-serif', padding: '2rem', background: '#fafdff', color: '#223' }}>
      {/* --- Hero Section --- */}
      <section style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.7rem', fontWeight: 700, color: '#0d74c8', letterSpacing: '-1px' }}>
          Meet Your Digital Twin—<br />Pioneering the Future of HIV Cure & Care
        </h1>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 400, color: '#287', margin: '1rem 0' }}>
          Empower your journey. Accelerate a cure. Inspire global research.
        </h2>
        <div style={{ margin: '2rem auto', maxWidth: 385 }}>
          <Image src={digitalTwinBanner} alt="Digital Twin Illustration" style={{ borderRadius: 18, width: "100%" }} priority />
        </div>
        <a href="#involvement" style={{ background: '#0d74c8', color: '#fff', padding: '1em 2em', borderRadius: 22, fontWeight: 600, fontSize: '1.2rem', textDecoration: 'none', boxShadow: '0 4px 18px #0d74c850' }}>
          Join the Movement
        </a>
      </section>

      {/* --- What is a Digital Twin? --- */}
      <section style={{ margin: '2.4rem 0' }}>
        <h3 style={{ fontWeight: 700, fontSize: '1.5rem', marginBottom: 11 }}>What is a Digital Twin?</h3>
        <p>A digital twin is a secure, virtual model of your unique health story—combining trusted medical data, lifestyle, and treatment inputs with AI-powered prediction and simulation.</p>
        <ul style={{ margin: '1.2em 0 0 1.1em', padding: 0 }}>
          <li style={{ marginBottom: 5 }}><strong>For individuals:</strong> Understand and personalize your health journey, forecast risks, team up with care providers, and participate in research.</li>
          <li style={{ marginBottom: 5 }}><strong>For professionals:</strong> Unlock rich data for research, optimize treatment at scale, and target new cures.</li>
        </ul>
      </section>

      {/* --- Why Digital Twins? --- */}
      <section style={{ margin: '2.4rem 0' }}>
        <h3 style={{ fontWeight: 700, fontSize: '1.5rem', marginBottom: 11 }}>Why Digital Twins? Why Now?</h3>
        <ul style={{ marginLeft: '1.1em', padding: 0, fontSize: '1.1rem' }}>
          <li>Track your full story—not just symptoms or appointments</li>
          <li>Safely test “what if” scenarios with new treatments—before real-world trials</li>
          <li>Give researchers and care teams unparalleled insight—helping accelerate discovery for all</li>
          <li>Every new digital twin powers global progress toward a cure</li>
        </ul>
      </section>

      {/* --- Get Involved --- */}
      <section id="involvement" style={{ margin: '2.6rem 0', backgroundColor: '#e6f5ff', padding: '2.2rem 1.2rem', borderRadius: 18 }}>
        <h3 style={{ fontWeight: 700, fontSize: '1.5rem', marginBottom: 15, textAlign: 'center' }}>How To Get Involved</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '3.2rem 2rem' }}>
          <div style={{ maxWidth: 320 }}>
            <strong>Individuals &amp; Patients</strong>
            <ul>
              <li>Join securely with your consent</li>
              <li>Share real-world aftercare, health & wellness data</li>
              <li>Track your progress, get personalized insights</li>
            </ul>
          </div>
          <div style={{ maxWidth: 320 }}>
            <strong>Clinicians &amp; Providers</strong>
            <ul>
              <li>Integrate EHRs, research & infrastructure via API</li>
              <li>Participate in next-gen studies</li>
              <li>Enable real-time digital collaboration</li>
            </ul>
          </div>
          <div style={{ maxWidth: 320 }}>
            <strong>Industry, Sponsors &amp; Foundations</strong>
            <ul>
              <li>Sponsor the platform or a clinical digital-twin challenge</li>
              <li>Contribute resources/infrastructure</li>
              <li>Partner to advance the cure—open science & impact</li>
            </ul>
          </div>
        </div>
      </section>

      {/* --- Roadmap & Impact --- */}
      <section style={{ margin: '2.4rem 0 3rem 0', textAlign: 'center' }}>
        <h3 style={{ fontWeight: 700, fontSize: '1.5rem', marginBottom: 10 }}>The Roadmap to the Cure—Powered by Digital Twins</h3>
        <p>Every new digital twin brings us closer.<br />Progress bar, testimonials, and real-time stats coming soon!</p>
      </section>
    </main>
  );
}

