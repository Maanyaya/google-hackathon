import { useEffect, useRef } from "react";

let observer;

function getObserver() {
  if (observer) return observer;
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("in-view");
        observer.unobserve(entry.target);
      }
    },
    { rootMargin: "-40px 0px", threshold: 0.06 },
  );
  return observer;
}

/** Lightweight scroll reveal — one shared observer, CSS transitions. */
export function Reveal({ children, className = "", delay = 0, as: Tag = "div", ...rest }) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (delay) el.style.setProperty("--reveal-delay", `${delay}ms`);
    const io = getObserver();
    io.observe(el);
    return () => io.unobserve(el);
  }, [delay]);

  return (
    <Tag ref={ref} className={`reveal ${className}`.trim()} {...rest}>
      {children}
    </Tag>
  );
}

/** Stagger via CSS nth-child delays on direct .reveal children. */
export function RevealGroup({ children, className = "", ...rest }) {
  return (
    <div className={`reveal-group ${className}`.trim()} {...rest}>
      {children}
    </div>
  );
}

/** Hook for count-up / one-shot effects when element enters view. */
export function useInViewOnce(ref, onEnter) {
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          onEnter();
          io.disconnect();
        }
      },
      { threshold: 0.2 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [ref, onEnter]);
}
