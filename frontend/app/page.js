"use client";

import React from "react";
import Navbar     from "../components/landing/Navbar/Navbar";
import Hero       from "../components/landing/Hero/Hero";
import OCRPreview from "../components/landing/OCRPreview/OCRPreview";
import Features   from "../components/landing/Features/Features";
import CTASection from "../components/landing/CTASection/CTASection";
import Footer     from "../components/landing/Footer/Footer";

export default function LandingPage() {
  return (
    <main className="relative min-h-screen w-full overflow-x-hidden">

      {/* Ambient background orbs — global utility classes from utilities.css */}
      <div
        className="bg-glow-orb-teal"
        style={{ top: "-100px", right: "-100px" }}
      />
      <div
        className="bg-glow-orb-orange"
        style={{ bottom: "10%", left: "-80px" }}
      />

      <Navbar />
      <Hero />
      <OCRPreview />
      <Features />
      <CTASection />
      <Footer />

    </main>
  );
}
