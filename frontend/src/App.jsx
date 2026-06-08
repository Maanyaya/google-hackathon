import { lazy, Suspense, useCallback, useState } from "react";
import { useDashboardBundle, syncData } from "./hooks";
import { Nav } from "./components/Nav";
import { Hero } from "./components/sections/Hero";
import { Problem } from "./components/sections/Problem";
import { Architecture } from "./components/sections/Architecture";

const Setup = lazy(() =>
  import("./components/sections/Setup").then((m) => ({ default: m.Setup })),
);
const MemoryGraph = lazy(() =>
  import("./components/sections/MemoryGraph").then((m) => ({ default: m.MemoryGraph })),
);
const ContextPack = lazy(() =>
  import("./components/sections/ContextPack").then((m) => ({ default: m.ContextPack })),
);
const Decisions = lazy(() =>
  import("./components/sections/Decisions").then((m) => ({ default: m.Decisions })),
);
const Impact = lazy(() =>
  import("./components/sections/Impact").then((m) => ({ default: m.Impact })),
);
const Agents = lazy(() =>
  import("./components/sections/Agents").then((m) => ({ default: m.Agents })),
);
const Pipelines = lazy(() =>
  import("./components/sections/Pipelines").then((m) => ({ default: m.Pipelines })),
);
const Mission = lazy(() =>
  import("./components/sections/Mission").then((m) => ({ default: m.Mission })),
);
const Footer = lazy(() =>
  import("./components/sections/Footer").then((m) => ({ default: m.Footer })),
);

function SectionFallback({ min = 320 }) {
  return <div className="section-fallback" style={{ minHeight: min }} aria-hidden />;
}

export default function App() {
  const {
    overview,
    topology,
    pack,
    decisions,
    impact,
    pipelines,
    freshness,
    setup,
    packLoading,
    topoLoading,
    decisionsLoading,
    refresh,
  } = useDashboardBundle();

  const [syncing, setSyncing] = useState(false);

  const onNav = useCallback((id) => {
    if (id === "top") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const onSync = useCallback(async () => {
    if (syncing) return;
    setSyncing(true);
    try {
      await syncData();
    } catch {
      // Fivetran sync may be unavailable; still refresh from BigQuery below.
    }
    try {
      await refresh();
    } finally {
      setSyncing(false);
    }
  }, [syncing, refresh]);

  return (
    <>
      <Nav onNav={onNav} githubSource={overview?.github_source} onSync={onSync} syncing={syncing} />
      <Hero overview={overview} decisions={decisions} impact={impact} onNav={onNav} />
      <Problem />
      <Architecture />
      <Suspense fallback={<SectionFallback min={400} />}>
        <Setup setup={setup} loading={!setup && packLoading} />
      </Suspense>

      <Suspense fallback={<SectionFallback min={480} />}>
        <MemoryGraph decisions={decisions} />
      </Suspense>
      <Suspense fallback={<SectionFallback min={520} />}>
        <ContextPack pack={pack} loading={packLoading} />
      </Suspense>
      <Suspense fallback={<SectionFallback min={400} />}>
        <Decisions decisions={decisions} loading={decisionsLoading} />
      </Suspense>
      <Suspense fallback={<SectionFallback min={420} />}>
        <Impact impact={impact} />
      </Suspense>
      <Suspense fallback={<SectionFallback min={360} />}>
        <Agents topology={topology} loading={topoLoading} />
      </Suspense>
      <Suspense fallback={<SectionFallback min={320} />}>
        <Pipelines pipelines={pipelines} freshness={freshness} />
      </Suspense>
      <Suspense fallback={<SectionFallback min={380} />}>
        <Mission />
      </Suspense>
      <Suspense fallback={null}>
        <Footer overview={overview} onNav={onNav} />
      </Suspense>
    </>
  );
}
