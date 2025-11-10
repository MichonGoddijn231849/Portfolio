// src/components/GrainOverlay.tsx

import React, { useEffect, useRef } from "react";

const GrainOverlay = () => {
  const grainRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let frameId: number;

    const animate = () => {
      if (grainRef.current) {
        const x = Math.random() * 10 - 5;
        const y = Math.random() * 10 - 5;
        grainRef.current.style.transform = `translate(${x}px, ${y}px)`;
      }
      frameId = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(frameId);
  }, []);

  return (
    <div
      ref={grainRef}
      className="fixed inset-0 z-10 pointer-events-none"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='grain'%3E%3CfeTurbulence type='turbulence' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23grain)' opacity='0.35'/%3E%3C/svg%3E")`,
        backgroundSize: "150px 150px",
        opacity: 0.35,
        mixBlendMode: "overlay",
        transition: "transform 0.2s ease-out",
      }}
    />
  );
};

export default GrainOverlay;

