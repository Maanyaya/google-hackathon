import { Panel, Skeleton } from "../ui/Panel";
import { TOKENS, CHART_TOOLTIP } from "../../lib/theme";
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Area, AreaChart,
} from "recharts";

function ChartShell({ title, subtitle, loading, empty, children }) {
  return (
    <Panel title={title} subtitle={subtitle}>
      {loading ? <Skeleton className="h-56 rounded-xl" /> : empty ? (
        <p className="ui-empty">No chart data</p>
      ) : children}
    </Panel>
  );
}

export function AnalyticsCharts({ events, tools, decisions, loading }) {
  const eventsData = events?.data ?? [];
  const toolsData = tools?.data ?? [];
  const decisionsData = decisions?.data ?? [];

  return (
    <section className="ui-chart-grid animate-in delay-5">
      <ChartShell title="Event taxonomy" subtitle="What agents log" loading={loading && !events} empty={!eventsData.length}>
        {eventsData.length > 0 && (
          <div className="ui-chart-h">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={eventsData} margin={{ top: 12, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="gEvents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={TOKENS.memory} stopOpacity={0.35} />
                    <stop offset="100%" stopColor={TOKENS.memory} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="label" tick={{ fill: "#8892A8", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#8892A8", fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip contentStyle={CHART_TOOLTIP} />
                <Area type="monotone" dataKey="value" stroke={TOKENS.memory} fill="url(#gEvents)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </ChartShell>

      <ChartShell title="Agent tools" subtitle="Cursor vs Antigravity" loading={loading && !tools} empty={!toolsData.length}>
        {toolsData.length > 0 && (
          <div className="ui-chart-h ui-chart-donut">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={toolsData} dataKey="value" nameKey="label" cx="50%" cy="50%" innerRadius={58} outerRadius={88} paddingAngle={3}>
                  {toolsData.map((_, i) => (
                    <Cell key={i} fill={TOKENS.chart[i % TOKENS.chart.length]} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP} />
              </PieChart>
            </ResponsiveContainer>
            <div className="ui-donut-legend">
              {toolsData.map((d, i) => (
                <span key={d.label}><i style={{ background: TOKENS.chart[i % TOKENS.chart.length] }} />{d.label} ({d.value})</span>
              ))}
            </div>
          </div>
        )}
      </ChartShell>

      <ChartShell title="Engineering decisions" subtitle="Logged reasoning" loading={loading && !decisions} empty={!decisionsData.length}>
        {decisionsData.length > 0 && (
          <div className="ui-chart-h">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={decisionsData} margin={{ top: 8, right: 8, left: -16, bottom: 40 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="label" tick={{ fill: "#8892A8", fontSize: 9 }} angle={-25} textAnchor="end" interval={0} height={50} />
                <YAxis tick={{ fill: "#8892A8", fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip contentStyle={CHART_TOOLTIP} cursor={{ fill: "rgba(232,163,23,0.06)" }} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={36}>
                  {decisionsData.map((_, i) => (
                    <Cell key={i} fill={TOKENS.chart[i % TOKENS.chart.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </ChartShell>
    </section>
  );
}
