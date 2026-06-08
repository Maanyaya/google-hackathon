import { useCallback } from "react";
import "./index.css";
import { useDashboardData } from "./hooks";
import { Shell, TopBar } from "./components/layout/Shell";
import { HeroMetrics, ArchitectureFlow } from "./components/sections/HeroMetrics";
import { AgentConstellation } from "./components/sections/AgentConstellation";
import { PipelineHealth } from "./components/sections/PipelineHealth";
import { MemoryFeed } from "./components/sections/MemoryFeed";
import { AnalyticsCharts } from "./components/sections/AnalyticsCharts";
import { MissionDeck } from "./components/sections/MissionDeck";

export default function App() {
  const { data: overview } = useDashboardData("/api/dashboard/overview");
  const { data: topology, loading: topoLoading } = useDashboardData("/api/dashboard/topology");
  const { data: pipelines, loading: pipeLoading } = useDashboardData("/api/dashboard/pipelines", 60000);
  const { data: freshness, loading: freshLoading } = useDashboardData("/api/dashboard/freshness", 60000);
  const { data: memory, loading: memLoading } = useDashboardData("/api/dashboard/memory", 30000);
  const { data: eventsChart, loading: chartLoading } = useDashboardData("/api/dashboard/charts/activities");
  const { data: toolsChart } = useDashboardData("/api/dashboard/charts/class-levels");
  const { data: decisionsChart } = useDashboardData("/api/dashboard/charts/states");
  const { data: timeline } = useDashboardData("/api/dashboard/timeline", 60000);

  const scrollTo = useCallback((id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const metricsLoading = freshLoading && !freshness;

  return (
    <Shell>
      <TopBar overview={overview} onNav={scrollTo} />

      <main className="ui-main">
        <HeroMetrics overview={overview} freshness={freshness} memory={memory} loading={metricsLoading} />
        <ArchitectureFlow overview={overview} />
        <AgentConstellation agents={topology?.agents} loading={topoLoading} />
        <PipelineHealth
          pipelines={pipelines}
          highlightId={overview?.fivetran_modex_connection}
          timeline={timeline}
          loading={pipeLoading}
        />
        <MemoryFeed data={memory} loading={memLoading} />
        <AnalyticsCharts events={eventsChart} tools={toolsChart} decisions={decisionsChart} loading={chartLoading} />
        <MissionDeck />
      </main>

      <footer className="ui-footer">
        <span>MoDeX · Memory of Codex</span>
        <span className="ui-footer-dot" />
        <span>Fivetran Track</span>
        <span className="ui-footer-dot" />
        <span className="font-mono text-[0.65rem] opacity-60">{overview?.cloud_run_url ? "live" : "local"}</span>
      </footer>
    </Shell>
  );
}
