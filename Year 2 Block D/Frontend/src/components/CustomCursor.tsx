import React, { useEffect, useRef } from "react";

const CustomCursor = () => {
  const cursorRef = useRef<HTMLDivElement>(null);
  const mouse = useRef({ x: 0, y: 0 });
  const pos = useRef({ x: 0, y: 0 });
  const speed = 0.15; // Smooth movement factor

  useEffect(() => {
    const updateMouse = (e: MouseEvent) => {
      mouse.current.x = e.clientX;
      mouse.current.y = e.clientY;
    };

    // ✅ Attach listener globally to window
    window.addEventListener("mousemove", updateMouse);

    const animate = () => {
      pos.current.x += (mouse.current.x - pos.current.x) * speed;
      pos.current.y += (mouse.current.y - pos.current.y) * speed;

      if (cursorRef.current) {
        cursorRef.current.style.transform = `translate3d(${pos.current.x}px, ${pos.current.y}px, 0)`;
      }
      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("mousemove", updateMouse);
    };
  }, []);

  return (
    <div
      ref={cursorRef}
      className="pointer-events-none fixed top-0 left-0 w-6 h-6 rounded-full bg-gradient-to-br from-primary to-accent opacity-80 mix-blend-difference z-[9999]"
      style={{
        transform: "translate3d(0,0,0)",
        transition: "background 0.2s ease",
        willChange: "transform", // ✅ smoother GPU-accelerated movement
      }}
    ></div>
  );
};

export default CustomCursor;

