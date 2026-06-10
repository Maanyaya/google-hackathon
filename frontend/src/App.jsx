import { lazy, Suspense, useCallback, useState } from "react";
import { useDashboardBundle, syncData } from "./hooks";
import { Nav } from "./components/Nav";
import { Hero } from "./components/sections/Hero";
import { Problem } from "./components/sections/Problem";
import { Architecture } from "./components/sections/Architecture";

const Submission = lazy(() =>
  import("./components/sections/Submission").then((m) => ({ default: m.Submission })),
);
const AskGuide = lazy(() =>
  import("./components/sections/AskGuide").then((m) => ({ default: m.AskGuide })),
);
const FivetranHub = lazy(() =>
  import("./components/sections/FivetranHub").then((m) => ({ default: m.FivetranHub })),
);
const Stack = lazy(() =>
  import("./components/sections/Stack").then((m) => ({ default: m.Stack })),
);
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
const FlowDiagram = lazy(() =>
  import("./components/sections/FlowDiagram").then((m) => ({ default: m.FlowDiagram })),
);
const DemoVideo = lazy(() =>
  import("./components/sections/DemoVideo").then((m) => ({ default: m.DemoVideo })),
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
    fivetranHub,
    setup,
    packLoading,
    topoLoading,
    decisionsLoading,
    refresh,
  } = useDashboardBundle();

  const [syncing, setSyncing] = useState(false);

  const onNav = useCallback((id) => {
    if (id === "top") {
      window.scrollTo({ top: 0, behavior: "instant" });
      return;
    }
    document.getElementById(id)?.scrollIntoView({ behavior: "instant", block: "start" });
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

      <Suspense fallback={<SectionFallback min={360} />}>
        <Submission />
      </Suspense>

      <Problem />
      <Architecture />

      {/* Fivetran track centerpiece */}
      <Suspense fallback={<SectionFallback min={520} />}>
        <FivetranHub hub={fivetranHub} onNav={onNav} />
      </Suspense>

      {/* Stack & integrations */}
      <Suspense fallback={<SectionFallback min={480} />}>
        <Stack />
      </Suspense>

      {/* Face 2 agent console */}
      <Suspense fallback={<SectionFallback min={520} />}>
        <AskGuide />
      </Suspense>

      <Suspense fallback={<SectionFallback min={600} />}>
        <FlowDiagram />
      </Suspense>
      <Suspense fallback={<SectionFallback min={420} />}>
        <DemoVideo videoUrl={setup?.videos?.handoff_demo} />
      </Suspense>
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
      <Suspense fallback={null}>
        <Footer overview={overview} onNav={onNav} />
      </Suspense>
    </>
  );
}
