import * as React from 'react';
import csvText from '../data/global-data-center-dataset.csv?raw';
import waterBodiesCsvText from '../data/area-wise-waterbodies-count-of-india.csv?raw';
import groundWaterCsvText from '../data/state-ground-water-level-information.csv?raw';
import cubemsSummaryCsvText from '../data/cubems-smart-building-energy-and-iaq-summary.csv?raw';

type PageId = 'home' | 'data-centers' | 'waterbodies' | 'groundwater' | 'cubems';

type DataCenterMetric =
  | 'total_data_centers'
  | 'hyperscale_data_centers'
  | 'colocation_data_centers'
  | 'floor_space_sqft_total'
  | 'power_capacity_MW_total'
  | 'average_renewable_energy_usage_percent'
  | 'internet_penetration_percent'
  | 'avg_latency_to_global_hubs_ms'
  | 'number_of_fiber_connections'
  | 'growth_rate_of_data_centers_percent_per_year';

type VisualizationType =
  | 'bars'
  | 'columns'
  | 'scatter'
  | 'bubble'
  | 'donut'
  | 'radar'
  | 'heatmap'
  | 'treemap'
  | 'rankline'
  | 'table';

type SortDirection = 'desc' | 'asc';

type WaterBodyRow = {
  state: string;
  total: number;
  buckets: Record<string, number>;
};

type GroundWaterRow = {
  state: string;
  stations: number;
  minLevel: number;
  maxLevel: number;
  spread: number;
};

type CubemsRow = {
  file: string;
  floor: string;
  year: string;
  rows: number;
  totalKwMinutes: number;
  lightKwMinutes: number;
  plugKwMinutes: number;
  acKwMinutes: number;
  peakKw: number;
};

type AnalysisMetric = {
  id: string;
  label: string;
  unit?: string;
};

type AnalysisRow = {
  id: string;
  label: string;
  subtitle?: string;
  metrics: Record<string, number>;
};

type AnalysisStat = {
  label: string;
  value: string;
  tone?: 'dark' | 'light';
};

type DataCenterCountry = {
  country: string;
  tier_distribution: string;
  key_operators: string;
  cloud_provider: string;
  cooling_technologies_common: string;
  green_dc_initiatives_description: string;
} & Record<DataCenterMetric, number>;

const metrics: DataCenterMetric[] = [
  'total_data_centers',
  'hyperscale_data_centers',
  'colocation_data_centers',
  'floor_space_sqft_total',
  'power_capacity_MW_total',
  'average_renewable_energy_usage_percent',
  'internet_penetration_percent',
  'avg_latency_to_global_hubs_ms',
  'number_of_fiber_connections',
  'growth_rate_of_data_centers_percent_per_year'
];

const metricLabels: Record<DataCenterMetric, string> = {
  total_data_centers: 'Total data centers',
  hyperscale_data_centers: 'Hyperscale data centers',
  colocation_data_centers: 'Colocation data centers',
  floor_space_sqft_total: 'Floor space',
  power_capacity_MW_total: 'Power capacity',
  average_renewable_energy_usage_percent: 'Renewable usage',
  internet_penetration_percent: 'Internet penetration',
  avg_latency_to_global_hubs_ms: 'Latency',
  number_of_fiber_connections: 'Fiber connections',
  growth_rate_of_data_centers_percent_per_year: 'Growth rate'
};

const metricUnits: Partial<Record<DataCenterMetric, string>> = {
  floor_space_sqft_total: 'sq ft',
  power_capacity_MW_total: 'MW',
  average_renewable_energy_usage_percent: '%',
  internet_penetration_percent: '%',
  avg_latency_to_global_hubs_ms: 'ms',
  growth_rate_of_data_centers_percent_per_year: '%'
};

const viewLabels: Record<VisualizationType, string> = {
  bars: 'Bars',
  columns: 'Columns',
  scatter: 'Scatter',
  bubble: 'Bubble',
  donut: 'Donut',
  radar: 'Radar',
  heatmap: 'Heatmap',
  treemap: 'Treemap',
  rankline: 'Rank line',
  table: 'Table'
};

const palette = ['#F3F0E8', '#D9FF62', '#A7F3D0', '#67E8F9', '#F9A8D4', '#FDBA74', '#C4B5FD', '#FDE047'];

const navItems: { id: PageId; label: string; description: string }[] = [
  { id: 'home', label: 'Home', description: 'Project index' },
  { id: 'data-centers', label: 'Global data centers', description: 'Already-made dashboard' },
  { id: 'waterbodies', label: 'Waterbodies', description: 'India area-wise count' },
  { id: 'groundwater', label: 'Ground water', description: 'State-level station ranges' },
  { id: 'cubems', label: 'CUBEMS energy and IAQ', description: 'Floor-level building energy' }
];

function parseCsvRows(csv: string) {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = '';
  let inQuotes = false;

  for (let index = 0; index < csv.length; index += 1) {
    const char = csv[index];
    const nextChar = csv[index + 1];

    if (char === '"' && inQuotes && nextChar === '"') {
      field += '"';
      index += 1;
      continue;
    }

    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }

    if (char === ',' && !inQuotes) {
      row.push(field.trim());
      field = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && nextChar === '\n') {
        index += 1;
      }
      row.push(field.trim());
      if (row.some(Boolean)) rows.push(row);
      row = [];
      field = '';
      continue;
    }

    field += char;
  }

  row.push(field.trim());
  if (row.some(Boolean)) rows.push(row);
  return rows;
}

function parseNumber(value: string | undefined) {
  const cleaned = value?.replaceAll(',', '').replace(/[><~%+]/g, '').trim() || '';
  const parsed = Number(cleaned);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatCompact(value: number) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 1, notation: value >= 100000 ? 'compact' : 'standard' });
}

function parseDataCenterCsv(csv: string): DataCenterCountry[] {
  const [headers, ...rows] = parseCsvRows(csv);

  return rows.map((row) => {
    const record = Object.fromEntries(headers.map((header, index) => [header, row[index] ?? '']));

    return {
      country: record.country || 'Unknown',
      total_data_centers: parseNumber(record.total_data_centers),
      hyperscale_data_centers: parseNumber(record.hyperscale_data_centers),
      colocation_data_centers: parseNumber(record.colocation_data_centers),
      floor_space_sqft_total: parseNumber(record.floor_space_sqft_total),
      power_capacity_MW_total: parseNumber(record.power_capacity_MW_total),
      average_renewable_energy_usage_percent: parseNumber(record.average_renewable_energy_usage_percent),
      internet_penetration_percent: parseNumber(record.internet_penetration_percent),
      avg_latency_to_global_hubs_ms: parseNumber(record.avg_latency_to_global_hubs_ms),
      number_of_fiber_connections: parseNumber(record.number_of_fiber_connections),
      growth_rate_of_data_centers_percent_per_year: parseNumber(record.growth_rate_of_data_centers_percent_per_year),
      tier_distribution: record.tier_distribution || '',
      key_operators: record.key_operators || '',
      cloud_provider: record.cloud_provider || '',
      cooling_technologies_common: record.cooling_technologies_common || '',
      green_dc_initiatives_description: record.green_dc_initiatives_description || ''
    };
  });
}

function parseWaterBodiesCsv(csv: string): WaterBodyRow[] {
  const [headers, ...rows] = parseCsvRows(csv);
  const bucketHeaders = headers.slice(1);

  return rows.map((row) => {
    const buckets = Object.fromEntries(bucketHeaders.map((header, index) => [header, parseNumber(row[index + 1])]));
    const total = Object.values(buckets).reduce((sum, value) => sum + value, 0);
    return {
      state: row[0] || 'Unknown',
      buckets,
      total
    };
  });
}

function parseGroundWaterCsv(csv: string): GroundWaterRow[] {
  const [, ...rows] = parseCsvRows(csv);

  return rows.map((row) => {
    const minLevel = parseNumber(row[2]);
    const maxLevel = parseNumber(row[3]);
    return {
      state: row[0] || 'Unknown',
      stations: parseNumber(row[1]),
      minLevel,
      maxLevel,
      spread: maxLevel - minLevel
    };
  });
}

function parseCubemsSummaryCsv(csv: string): CubemsRow[] {
  const [, ...rows] = parseCsvRows(csv);

  return rows
    .filter(row => row[0])
    .map((row) => ({
      file: row[0] || '',
      floor: row[1] || 'Unknown',
      year: row[2] || 'Unknown',
      rows: parseNumber(row[3]),
      totalKwMinutes: parseNumber(row[4]),
      lightKwMinutes: parseNumber(row[5]),
      plugKwMinutes: parseNumber(row[6]),
      acKwMinutes: parseNumber(row[7]),
      peakKw: parseNumber(row[8])
    }));
}

function formatMetric(value: number, metric: DataCenterMetric) {
  const unit = metricUnits[metric];

  if (metric === 'floor_space_sqft_total') {
    return `${(value / 1_000_000).toLocaleString(undefined, { maximumFractionDigits: 1 })}M ${unit}`;
  }

  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toLocaleString(undefined, { maximumFractionDigits: 1 })}M${unit ? ` ${unit}` : ''}`;
  }

  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${unit ? ` ${unit}` : ''}`;
}

function getMax(rows: DataCenterCountry[], metric: DataCenterMetric) {
  return Math.max(1, ...rows.map(row => row[metric]));
}

function getColor(index: number) {
  return palette[index % palette.length];
}

function Bars({ rows, metric }: { rows: DataCenterCountry[]; metric: DataCenterMetric }) {
  const maxValue = getMax(rows, metric);

  return (
    <div className="space-y-3">
      {rows.map((row, index) => (
        <div className="group" key={row.country}>
          <div className="mb-1 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.16em] text-stone-400">
            <span className="truncate">{row.country}</span>
            <span>{formatMetric(row[metric], metric)}</span>
          </div>
          <div className="h-4 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full transition-all duration-700 group-hover:brightness-125"
              style={{ width: `${(row[metric] / maxValue) * 100}%`, backgroundColor: getColor(index) }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function Columns({ rows, metric }: { rows: DataCenterCountry[]; metric: DataCenterMetric }) {
  const maxValue = getMax(rows, metric);

  return (
    <div className="flex h-[360px] items-end gap-3 overflow-x-auto border-b border-white/15 pb-4">
      {rows.map((row, index) => (
        <div className="flex min-w-16 flex-1 flex-col items-center gap-3" key={row.country}>
          <div className="text-[10px] text-stone-400">{formatMetric(row[metric], metric)}</div>
          <div
            className="w-full min-w-10 rounded-t-md transition-all duration-700 hover:brightness-125"
            style={{ height: `${Math.max(4, (row[metric] / maxValue) * 290)}px`, backgroundColor: getColor(index) }}
          />
          <div className="w-20 truncate text-center text-xs text-stone-300">{row.country}</div>
        </div>
      ))}
    </div>
  );
}

function Scatter({
  rows,
  xMetric,
  yMetric,
  bubbleMetric
}: {
  rows: DataCenterCountry[];
  xMetric: DataCenterMetric;
  yMetric: DataCenterMetric;
  bubbleMetric?: DataCenterMetric;
}) {
  const maxX = getMax(rows, xMetric);
  const maxY = getMax(rows, yMetric);
  const maxBubble = bubbleMetric ? getMax(rows, bubbleMetric) : 1;

  return (
    <div className="relative h-[420px] overflow-hidden rounded-md border border-white/15 bg-black/20">
      <div className="absolute inset-6 border-l border-b border-white/20" />
      {rows.map((row, index) => {
        const size = bubbleMetric ? 12 + (row[bubbleMetric] / maxBubble) * 42 : 16;
        return (
          <div
            className="group absolute -translate-x-1/2 -translate-y-1/2 rounded-full border border-black/50 shadow-[0_0_30px_rgba(255,255,255,0.16)]"
            key={row.country}
            style={{
              left: `${8 + (row[xMetric] / maxX) * 84}%`,
              top: `${92 - (row[yMetric] / maxY) * 84}%`,
              width: size,
              height: size,
              backgroundColor: getColor(index)
            }}
            title={`${row.country}: ${metricLabels[xMetric]} ${formatMetric(row[xMetric], xMetric)}, ${metricLabels[yMetric]} ${formatMetric(row[yMetric], yMetric)}`}
          >
            <span className="pointer-events-none absolute left-1/2 top-full z-10 mt-2 hidden -translate-x-1/2 whitespace-nowrap rounded bg-stone-950 px-2 py-1 text-xs text-stone-100 group-hover:block">
              {row.country}
            </span>
          </div>
        );
      })}
      <span className="absolute bottom-2 left-6 text-xs uppercase tracking-[0.18em] text-stone-500">{metricLabels[xMetric]}</span>
      <span className="absolute left-2 top-6 origin-left rotate-90 text-xs uppercase tracking-[0.18em] text-stone-500">{metricLabels[yMetric]}</span>
    </div>
  );
}

function Donut({ rows, metric }: { rows: DataCenterCountry[]; metric: DataCenterMetric }) {
  const total = rows.reduce((sum, row) => sum + row[metric], 0) || 1;
  let offset = 0;

  const gradient = rows.map((row, index) => {
    const start = offset;
    offset += (row[metric] / total) * 100;
    return `${getColor(index)} ${start}% ${offset}%`;
  }).join(', ');

  return (
    <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
      <div
        className="mx-auto grid aspect-square w-full max-w-80 place-items-center rounded-full"
        style={{ background: `conic-gradient(${gradient})` }}
      >
        <div className="grid h-40 w-40 place-items-center rounded-full bg-[#10100f] text-center">
          <span className="px-4 text-sm uppercase tracking-[0.2em] text-stone-300">{metricLabels[metric]}</span>
        </div>
      </div>
      <div className="grid content-center gap-3">
        {rows.map((row, index) => (
          <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-2" key={row.country}>
            <span className="flex items-center gap-3 text-sm text-stone-200">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: getColor(index) }} />
              {row.country}
            </span>
            <span className="text-sm text-stone-400">{((row[metric] / total) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Radar({ rows }: { rows: DataCenterCountry[] }) {
  const radarMetrics: DataCenterMetric[] = [
    'total_data_centers',
    'hyperscale_data_centers',
    'colocation_data_centers',
    'power_capacity_MW_total',
    'internet_penetration_percent',
    'growth_rate_of_data_centers_percent_per_year'
  ];
  const size = 360;
  const center = size / 2;
  const radius = 135;

  function point(metric: DataCenterMetric, metricIndex: number, row: DataCenterCountry) {
    const angle = (Math.PI * 2 * metricIndex) / radarMetrics.length - Math.PI / 2;
    const value = row[metric] / getMax(rows, metric);
    return `${center + Math.cos(angle) * radius * value},${center + Math.sin(angle) * radius * value}`;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
      <svg viewBox={`0 0 ${size} ${size}`} className="mx-auto w-full max-w-[380px]">
        {[0.25, 0.5, 0.75, 1].map(scale => (
          <circle key={scale} cx={center} cy={center} r={radius * scale} fill="none" stroke="rgba(255,255,255,.12)" />
        ))}
        {radarMetrics.map((metric, index) => {
          const angle = (Math.PI * 2 * index) / radarMetrics.length - Math.PI / 2;
          const x = center + Math.cos(angle) * radius;
          const y = center + Math.sin(angle) * radius;
          return <line key={metric} x1={center} y1={center} x2={x} y2={y} stroke="rgba(255,255,255,.12)" />;
        })}
        {rows.slice(0, 4).map((row, index) => (
          <polygon
            key={row.country}
            points={radarMetrics.map((metric, metricIndex) => point(metric, metricIndex, row)).join(' ')}
            fill={`${getColor(index)}33`}
            stroke={getColor(index)}
            strokeWidth="2"
          />
        ))}
      </svg>
      <div className="grid content-center gap-3">
        {rows.slice(0, 4).map((row, index) => (
          <div className="rounded-md border border-white/10 bg-white/[0.03] p-4" key={row.country}>
            <div className="mb-2 flex items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: getColor(index) }} />
              <span className="font-medium">{row.country}</span>
            </div>
            <p className="text-sm text-stone-400">{row.key_operators || 'Operator details unavailable'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function Heatmap({ rows }: { rows: DataCenterCountry[] }) {
  const heatMetrics: DataCenterMetric[] = [
    'total_data_centers',
    'hyperscale_data_centers',
    'colocation_data_centers',
    'power_capacity_MW_total',
    'internet_penetration_percent',
    'growth_rate_of_data_centers_percent_per_year'
  ];

  return (
    <div className="overflow-auto">
      <div className="grid min-w-[820px] gap-2" style={{ gridTemplateColumns: `160px repeat(${heatMetrics.length}, minmax(90px, 1fr))` }}>
        <div />
        {heatMetrics.map(metric => <div className="text-xs uppercase tracking-[0.16em] text-stone-500" key={metric}>{metricLabels[metric]}</div>)}
        {rows.map(row => (
          <React.Fragment key={row.country}>
            <div className="py-2 text-sm text-stone-200">{row.country}</div>
            {heatMetrics.map(metric => {
              const intensity = row[metric] / getMax(rows, metric);
              return (
                <div
                  className="rounded px-2 py-3 text-xs text-stone-950"
                  key={metric}
                  style={{ backgroundColor: `color-mix(in srgb, #D9FF62 ${Math.max(10, intensity * 100)}%, #27272a)` }}
                >
                  {formatMetric(row[metric], metric)}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function Treemap({ rows, metric }: { rows: DataCenterCountry[]; metric: DataCenterMetric }) {
  const total = rows.reduce((sum, row) => sum + row[metric], 0) || 1;

  return (
    <div className="flex h-[420px] flex-wrap content-stretch gap-2">
      {rows.map((row, index) => (
        <div
          className="flex min-h-24 flex-col justify-between rounded-md p-4 text-stone-950"
          key={row.country}
          style={{
            flexBasis: `${Math.max(14, (row[metric] / total) * 100)}%`,
            flexGrow: row[metric],
            backgroundColor: getColor(index)
          }}
        >
          <span className="text-sm font-semibold">{row.country}</span>
          <span className="text-xs">{formatMetric(row[metric], metric)}</span>
        </div>
      ))}
    </div>
  );
}

function RankLine({ rows, metric }: { rows: DataCenterCountry[]; metric: DataCenterMetric }) {
  const maxValue = getMax(rows, metric);
  const points = rows.map((row, index) => {
    const x = 40 + (index / Math.max(1, rows.length - 1)) * 720;
    const y = 330 - (row[metric] / maxValue) * 280;
    return { row, x, y };
  });

  return (
    <svg viewBox="0 0 800 380" className="h-[420px] w-full overflow-visible">
      {[0, 1, 2, 3, 4].map(index => (
        <line key={index} x1="40" x2="760" y1={50 + index * 70} y2={50 + index * 70} stroke="rgba(255,255,255,.1)" />
      ))}
      <polyline
        fill="none"
        stroke="#D9FF62"
        strokeWidth="3"
        points={points.map(point => `${point.x},${point.y}`).join(' ')}
      />
      {points.map((point, index) => (
        <g key={point.row.country}>
          <circle cx={point.x} cy={point.y} r="6" fill={getColor(index)} />
          <text x={point.x} y="365" textAnchor="middle" fill="#d6d3d1" fontSize="11">
            {point.row.country.slice(0, 10)}
          </text>
        </g>
      ))}
    </svg>
  );
}

function DataTable({ rows }: { rows: DataCenterCountry[] }) {
  return (
    <div className="overflow-auto">
      <table className="w-full min-w-[900px] text-sm">
        <thead>
          <tr className="border-b border-white/15 text-left text-xs uppercase tracking-[0.16em] text-stone-500">
            <th className="py-3">Country</th>
            <th>Total</th>
            <th>Hyperscale</th>
            <th>Colocation</th>
            <th>Power</th>
            <th>Renewable</th>
            <th>Internet</th>
            <th>Growth</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr className="border-b border-white/10 text-stone-300 hover:bg-white/[0.04]" key={row.country}>
              <td className="py-4 font-medium text-stone-100">{row.country}</td>
              <td>{formatMetric(row.total_data_centers, 'total_data_centers')}</td>
              <td>{formatMetric(row.hyperscale_data_centers, 'hyperscale_data_centers')}</td>
              <td>{formatMetric(row.colocation_data_centers, 'colocation_data_centers')}</td>
              <td>{formatMetric(row.power_capacity_MW_total, 'power_capacity_MW_total')}</td>
              <td>{formatMetric(row.average_renewable_energy_usage_percent, 'average_renewable_energy_usage_percent')}</td>
              <td>{formatMetric(row.internet_penetration_percent, 'internet_penetration_percent')}</td>
              <td>{formatMetric(row.growth_rate_of_data_centers_percent_per_year, 'growth_rate_of_data_centers_percent_per_year')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TopNav({ page, onNavigate }: { page: PageId; onNavigate: (page: PageId) => void }) {
  return (
    <nav className="sticky top-0 z-30 border-b border-white/10 bg-[#10100f]/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-5 py-3 lg:px-8">
        <a className="text-sm font-semibold uppercase tracking-[0.22em] text-[#F3F0E8]" href="#home" onClick={() => onNavigate('home')}>
          DAV Lab
        </a>
        <div className="flex max-w-full gap-2 overflow-x-auto pb-1">
          {navItems.map(item => (
            <a
              className={`shrink-0 rounded-full border px-3 py-2 text-xs transition ${page === item.id ? 'border-[#D9FF62] bg-[#D9FF62] text-stone-950' : 'border-white/15 bg-white/[0.03] text-stone-300 hover:border-white/40'}`}
              href={`#${item.id}`}
              key={item.id}
              onClick={() => onNavigate(item.id)}
            >
              {item.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}

function StatTile({ label, value, tone = 'dark' }: { label: string; value: string; tone?: 'dark' | 'light' }) {
  return (
    <div className={`rounded-md border p-5 ${tone === 'light' ? 'border-[#D9FF62] bg-[#D9FF62] text-stone-950' : 'border-white/10 bg-white/[0.04]'}`}>
      <p className="text-xs uppercase tracking-[0.18em] opacity-70">{label}</p>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
    </div>
  );
}

function SimpleBars({ rows }: { rows: { label: string; value: number; detail?: string }[] }) {
  const maxValue = Math.max(1, ...rows.map(row => row.value));

  return (
    <div className="grid gap-3">
      {rows.map((row, index) => (
        <div key={row.label}>
          <div className="mb-1 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.14em] text-stone-400">
            <span className="truncate">{row.label}</span>
            <span>{row.detail ?? formatCompact(row.value)}</span>
          </div>
          <div className="h-4 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full"
              style={{ width: `${(row.value / maxValue) * 100}%`, backgroundColor: getColor(index) }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function formatAnalysisValue(value: number, metric?: AnalysisMetric) {
  if (metric?.unit === '%') {
    return `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })}%`;
  }

  if (metric?.unit) {
    return `${formatCompact(value)} ${metric.unit}`;
  }

  return formatCompact(value);
}

function getAnalysisMetric(metrics: AnalysisMetric[], metricId: string) {
  return metrics.find(metric => metric.id === metricId) ?? metrics[0];
}

function getAnalysisMax(rows: AnalysisRow[], metricId: string) {
  return Math.max(1, ...rows.map(row => Math.max(0, row.metrics[metricId] ?? 0)));
}

function AnalysisBars({ rows, metric }: { rows: AnalysisRow[]; metric: AnalysisMetric }) {
  const maxValue = getAnalysisMax(rows, metric.id);

  return (
    <div className="space-y-3">
      {rows.map((row, index) => (
        <div className="group" key={row.id}>
          <div className="mb-1 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.16em] text-stone-400">
            <span className="truncate">{row.label}</span>
            <span>{formatAnalysisValue(row.metrics[metric.id] ?? 0, metric)}</span>
          </div>
          <div className="h-4 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full transition-all duration-700 group-hover:brightness-125"
              style={{ width: `${((row.metrics[metric.id] ?? 0) / maxValue) * 100}%`, backgroundColor: getColor(index) }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function AnalysisColumns({ rows, metric }: { rows: AnalysisRow[]; metric: AnalysisMetric }) {
  const maxValue = getAnalysisMax(rows, metric.id);

  return (
    <div className="flex h-[360px] items-end gap-3 overflow-x-auto border-b border-white/15 pb-4">
      {rows.map((row, index) => (
        <div className="flex min-w-16 flex-1 flex-col items-center gap-3" key={row.id}>
          <div className="text-[10px] text-stone-400">{formatAnalysisValue(row.metrics[metric.id] ?? 0, metric)}</div>
          <div
            className="w-full min-w-10 rounded-t-md transition-all duration-700 hover:brightness-125"
            style={{ height: `${Math.max(4, ((row.metrics[metric.id] ?? 0) / maxValue) * 290)}px`, backgroundColor: getColor(index) }}
          />
          <div className="w-20 truncate text-center text-xs text-stone-300">{row.label}</div>
        </div>
      ))}
    </div>
  );
}

function AnalysisScatter({
  rows,
  xMetric,
  yMetric,
  bubbleMetric
}: {
  rows: AnalysisRow[];
  xMetric: AnalysisMetric;
  yMetric: AnalysisMetric;
  bubbleMetric?: AnalysisMetric;
}) {
  const maxX = getAnalysisMax(rows, xMetric.id);
  const maxY = getAnalysisMax(rows, yMetric.id);
  const maxBubble = bubbleMetric ? getAnalysisMax(rows, bubbleMetric.id) : 1;

  return (
    <div className="relative h-[420px] overflow-hidden rounded-md border border-white/15 bg-black/20">
      <div className="absolute inset-6 border-l border-b border-white/20" />
      {rows.map((row, index) => {
        const size = bubbleMetric ? 12 + ((row.metrics[bubbleMetric.id] ?? 0) / maxBubble) * 42 : 16;
        return (
          <div
            className="group absolute -translate-x-1/2 -translate-y-1/2 rounded-full border border-black/50 shadow-[0_0_30px_rgba(255,255,255,0.16)]"
            key={row.id}
            style={{
              left: `${8 + ((row.metrics[xMetric.id] ?? 0) / maxX) * 84}%`,
              top: `${92 - ((row.metrics[yMetric.id] ?? 0) / maxY) * 84}%`,
              width: size,
              height: size,
              backgroundColor: getColor(index)
            }}
            title={`${row.label}: ${xMetric.label} ${formatAnalysisValue(row.metrics[xMetric.id] ?? 0, xMetric)}, ${yMetric.label} ${formatAnalysisValue(row.metrics[yMetric.id] ?? 0, yMetric)}`}
          >
            <span className="pointer-events-none absolute left-1/2 top-full z-10 mt-2 hidden -translate-x-1/2 whitespace-nowrap rounded bg-stone-950 px-2 py-1 text-xs text-stone-100 group-hover:block">
              {row.label}
            </span>
          </div>
        );
      })}
      <span className="absolute bottom-2 left-6 text-xs uppercase tracking-[0.18em] text-stone-500">{xMetric.label}</span>
      <span className="absolute left-2 top-6 origin-left rotate-90 text-xs uppercase tracking-[0.18em] text-stone-500">{yMetric.label}</span>
    </div>
  );
}

function AnalysisDonut({ rows, metric }: { rows: AnalysisRow[]; metric: AnalysisMetric }) {
  const total = rows.reduce((sum, row) => sum + Math.max(0, row.metrics[metric.id] ?? 0), 0) || 1;
  let offset = 0;
  const gradient = rows.map((row, index) => {
    const start = offset;
    offset += (Math.max(0, row.metrics[metric.id] ?? 0) / total) * 100;
    return `${getColor(index)} ${start}% ${offset}%`;
  }).join(', ');

  return (
    <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
      <div className="mx-auto grid aspect-square w-full max-w-80 place-items-center rounded-full" style={{ background: `conic-gradient(${gradient})` }}>
        <div className="grid h-40 w-40 place-items-center rounded-full bg-[#10100f] text-center">
          <span className="px-4 text-sm uppercase tracking-[0.2em] text-stone-300">{metric.label}</span>
        </div>
      </div>
      <div className="grid content-center gap-3">
        {rows.map((row, index) => (
          <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-2" key={row.id}>
            <span className="flex min-w-0 items-center gap-3 text-sm text-stone-200">
              <span className="h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: getColor(index) }} />
              <span className="truncate">{row.label}</span>
            </span>
            <span className="text-sm text-stone-400">{(((row.metrics[metric.id] ?? 0) / total) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalysisHeatmap({ rows, metrics }: { rows: AnalysisRow[]; metrics: AnalysisMetric[] }) {
  const heatMetrics = metrics.slice(0, 6);

  return (
    <div className="overflow-auto">
      <div className="grid min-w-[820px] gap-2" style={{ gridTemplateColumns: `160px repeat(${heatMetrics.length}, minmax(90px, 1fr))` }}>
        <div />
        {heatMetrics.map(metric => <div className="text-xs uppercase tracking-[0.16em] text-stone-500" key={metric.id}>{metric.label}</div>)}
        {rows.map(row => (
          <React.Fragment key={row.id}>
            <div className="py-2 text-sm text-stone-200">{row.label}</div>
            {heatMetrics.map(metric => {
              const intensity = (row.metrics[metric.id] ?? 0) / getAnalysisMax(rows, metric.id);
              return (
                <div
                  className="rounded px-2 py-3 text-xs text-stone-950"
                  key={metric.id}
                  style={{ backgroundColor: `color-mix(in srgb, #D9FF62 ${Math.max(10, intensity * 100)}%, #27272a)` }}
                >
                  {formatAnalysisValue(row.metrics[metric.id] ?? 0, metric)}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function AnalysisTreemap({ rows, metric }: { rows: AnalysisRow[]; metric: AnalysisMetric }) {
  const total = rows.reduce((sum, row) => sum + Math.max(0, row.metrics[metric.id] ?? 0), 0) || 1;

  return (
    <div className="flex h-[420px] flex-wrap content-stretch gap-2">
      {rows.map((row, index) => (
        <div
          className="flex min-h-24 min-w-28 flex-col justify-between rounded-md p-4 text-stone-950"
          key={row.id}
          style={{
            flexBasis: `${Math.max(14, (Math.max(0, row.metrics[metric.id] ?? 0) / total) * 100)}%`,
            flexGrow: Math.max(1, row.metrics[metric.id] ?? 0),
            backgroundColor: getColor(index)
          }}
        >
          <span className="text-sm font-semibold">{row.label}</span>
          <span className="text-xs">{formatAnalysisValue(row.metrics[metric.id] ?? 0, metric)}</span>
        </div>
      ))}
    </div>
  );
}

function AnalysisRankLine({ rows, metric }: { rows: AnalysisRow[]; metric: AnalysisMetric }) {
  const maxValue = getAnalysisMax(rows, metric.id);
  const points = rows.map((row, index) => {
    const x = 40 + (index / Math.max(1, rows.length - 1)) * 720;
    const y = 330 - ((row.metrics[metric.id] ?? 0) / maxValue) * 280;
    return { row, x, y };
  });

  return (
    <svg viewBox="0 0 800 380" className="h-[420px] w-full overflow-visible">
      {[0, 1, 2, 3, 4].map(index => (
        <line key={index} x1="40" x2="760" y1={50 + index * 70} y2={50 + index * 70} stroke="rgba(255,255,255,.1)" />
      ))}
      <polyline fill="none" stroke="#D9FF62" strokeWidth="3" points={points.map(point => `${point.x},${point.y}`).join(' ')} />
      {points.map((point, index) => (
        <g key={point.row.id}>
          <circle cx={point.x} cy={point.y} r="6" fill={getColor(index)} />
          <text x={point.x} y="365" textAnchor="middle" fill="#d6d3d1" fontSize="11">
            {point.row.label.slice(0, 10)}
          </text>
        </g>
      ))}
    </svg>
  );
}

function AnalysisTable({ rows, metrics }: { rows: AnalysisRow[]; metrics: AnalysisMetric[] }) {
  return (
    <div className="overflow-auto">
      <table className="w-full min-w-[900px] text-sm">
        <thead>
          <tr className="border-b border-white/15 text-left text-xs uppercase tracking-[0.16em] text-stone-500">
            <th className="py-3">Name</th>
            {metrics.map(metric => <th key={metric.id}>{metric.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr className="border-b border-white/10 text-stone-300 hover:bg-white/[0.04]" key={row.id}>
              <td className="py-4 font-medium text-stone-100">
                {row.label}
                {row.subtitle && <span className="block text-xs font-normal text-stone-500">{row.subtitle}</span>}
              </td>
              {metrics.map(metric => <td key={metric.id}>{formatAnalysisValue(row.metrics[metric.id] ?? 0, metric)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AnalysisExplorer({
  kicker,
  title,
  description,
  rows,
  metrics,
  stats,
  note,
  initialMetric
}: {
  kicker: string;
  title: string;
  description: string;
  rows: AnalysisRow[];
  metrics: AnalysisMetric[];
  stats: AnalysisStat[];
  note: string;
  initialMetric: string;
}) {
  const [view, setView] = React.useState<VisualizationType>('bars');
  const [selectedMetric, setSelectedMetric] = React.useState(initialMetric);
  const [xMetric, setXMetric] = React.useState(metrics[1]?.id ?? initialMetric);
  const [yMetric, setYMetric] = React.useState(initialMetric);
  const [bubbleMetric, setBubbleMetric] = React.useState(metrics[2]?.id ?? initialMetric);
  const [selectedRow, setSelectedRow] = React.useState('All');
  const [topN, setTopN] = React.useState(Math.min(10, Math.max(5, rows.length)));
  const [sortDirection, setSortDirection] = React.useState<SortDirection>('desc');

  const metric = getAnalysisMetric(metrics, selectedMetric);
  const filteredRows = selectedRow === 'All' ? rows : rows.filter(row => row.id === selectedRow);
  const sortedRows = [...filteredRows]
    .sort((a, b) => sortDirection === 'desc' ? (b.metrics[selectedMetric] ?? 0) - (a.metrics[selectedMetric] ?? 0) : (a.metrics[selectedMetric] ?? 0) - (b.metrics[selectedMetric] ?? 0))
    .slice(0, topN);
  const leader = [...rows].sort((a, b) => (b.metrics[selectedMetric] ?? 0) - (a.metrics[selectedMetric] ?? 0))[0];

  function renderVisualization() {
    if (view === 'bars') return <AnalysisBars rows={sortedRows} metric={metric} />;
    if (view === 'columns') return <AnalysisColumns rows={sortedRows} metric={metric} />;
    if (view === 'scatter') return <AnalysisScatter rows={sortedRows} xMetric={getAnalysisMetric(metrics, xMetric)} yMetric={getAnalysisMetric(metrics, yMetric)} />;
    if (view === 'bubble') return <AnalysisScatter rows={sortedRows} xMetric={getAnalysisMetric(metrics, xMetric)} yMetric={getAnalysisMetric(metrics, yMetric)} bubbleMetric={getAnalysisMetric(metrics, bubbleMetric)} />;
    if (view === 'donut') return <AnalysisDonut rows={sortedRows} metric={metric} />;
    if (view === 'heatmap') return <AnalysisHeatmap rows={sortedRows} metrics={metrics} />;
    if (view === 'treemap') return <AnalysisTreemap rows={sortedRows} metric={metric} />;
    if (view === 'rankline') return <AnalysisRankLine rows={sortedRows} metric={metric} />;
    if (view === 'radar') return <AnalysisHeatmap rows={sortedRows} metrics={metrics} />;
    return <AnalysisTable rows={sortedRows} metrics={metrics} />;
  }

  return (
    <main className="min-h-screen bg-[#10100f] text-[#f3f0e8]">
      <section className="relative overflow-hidden border-b border-white/10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(217,255,98,0.14),transparent_28%),linear-gradient(120deg,rgba(255,255,255,0.07),transparent_45%)]" />
        <div className="relative mx-auto grid max-w-7xl gap-10 px-5 py-8 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-12">
          <div className="flex min-h-[320px] flex-col justify-between">
            <div className="flex items-center gap-3 text-xs uppercase tracking-[0.24em] text-stone-400">
              <span className="h-2 w-2 rounded-full bg-[#D9FF62]" />
              {kicker}
            </div>
            <div>
              <h1 className="max-w-4xl text-6xl font-semibold leading-[0.9] tracking-normal text-[#F3F0E8] md:text-8xl">{title}</h1>
              <p className="mt-6 max-w-2xl text-base leading-7 text-stone-400">{description}</p>
            </div>
          </div>
          <div className="grid content-end gap-3">
            <div className="grid grid-cols-2 gap-3">
              {stats.map((stat, index) => <StatTile key={stat.label} label={stat.label} value={stat.value} tone={stat.tone ?? (index === 1 ? 'light' : 'dark')} />)}
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-stone-500">Current leader</p>
              <p className="mt-3 text-3xl font-semibold">{leader?.label}</p>
              <p className="mt-2 text-sm text-stone-400">{metric.label} · {formatAnalysisValue(leader?.metrics[selectedMetric] ?? 0, metric)}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-6 lg:px-8">
        <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
          <div className="flex flex-wrap gap-2">
            {(Object.keys(viewLabels) as VisualizationType[]).map(option => (
              <button
                className={`rounded-full border px-4 py-2 text-sm transition ${view === option ? 'border-[#D9FF62] bg-[#D9FF62] text-stone-950' : 'border-white/15 bg-white/[0.03] text-stone-300 hover:border-white/40'}`}
                key={option}
                onClick={() => setView(option)}
                type="button"
              >
                {viewLabels[option]}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex">
            <select className="rounded-md border border-white/15 bg-[#171715] px-3 py-2 text-sm" value={selectedMetric} onChange={(event) => setSelectedMetric(event.target.value)}>
              {metrics.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
            <select className="rounded-md border border-white/15 bg-[#171715] px-3 py-2 text-sm" value={selectedRow} onChange={(event) => setSelectedRow(event.target.value)}>
              <option value="All">All rows</option>
              {rows.map(row => <option key={row.id} value={row.id}>{row.label}</option>)}
            </select>
          </div>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Top N
            <input className="accent-[#D9FF62]" max={Math.max(5, rows.length)} min="1" onChange={(event) => setTopN(Number(event.target.value))} step="1" type="range" value={topN} />
            <span className="text-sm normal-case tracking-normal text-stone-200">{topN} rows</span>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Sort
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={sortDirection} onChange={(event) => setSortDirection(event.target.value as SortDirection)}>
              <option value="desc">Highest first</option>
              <option value="asc">Lowest first</option>
            </select>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            X metric
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={xMetric} onChange={(event) => setXMetric(event.target.value)}>
              {metrics.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Y metric
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={yMetric} onChange={(event) => setYMetric(event.target.value)}>
              {metrics.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Bubble size
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={bubbleMetric} onChange={(event) => setBubbleMetric(event.target.value)}>
              {metrics.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-5 pb-12 lg:grid-cols-[1fr_320px] lg:px-8">
        <div className="rounded-md border border-white/10 bg-[#151513] p-5 shadow-2xl shadow-black/40">
          <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-stone-500">{viewLabels[view]}</p>
              <h2 className="mt-2 text-3xl font-semibold">{metric.label}</h2>
            </div>
            <p className="max-w-md text-sm leading-6 text-stone-400">
              Showing {sortedRows.length} of {filteredRows.length} rows. Scatter and bubble views use the X, Y, and size controls.
            </p>
          </div>
          {renderVisualization()}
        </div>
        <aside className="grid gap-5">
          <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-stone-500">Top rows</p>
            <div className="mt-4 grid gap-3">
              {sortedRows.slice(0, 5).map((row, index) => (
                <div className="flex items-center justify-between gap-3" key={row.id}>
                  <span className="flex min-w-0 items-center gap-2 text-sm">
                    <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-white/10 text-xs">{index + 1}</span>
                    <span className="truncate">{row.label}</span>
                  </span>
                  <span className="text-sm text-stone-400">{formatAnalysisValue(row.metrics[selectedMetric] ?? 0, metric)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-md border border-white/10 bg-[#D9FF62] p-5 text-stone-950">
            <p className="text-xs uppercase tracking-[0.2em]">Dataset notes</p>
            <p className="mt-3 text-sm leading-6">{note}</p>
          </div>
        </aside>
      </section>
    </main>
  );
}

function HomePage({ onNavigate }: { onNavigate: (page: PageId) => void }) {
  const dataCenters = React.useMemo(() => parseDataCenterCsv(csvText), []);
  const waterBodies = React.useMemo(() => parseWaterBodiesCsv(waterBodiesCsvText), []);
  const groundWater = React.useMemo(() => parseGroundWaterCsv(groundWaterCsvText), []);
  const cubems = React.useMemo(() => parseCubemsSummaryCsv(cubemsSummaryCsvText), []);

  const siteCards = [
    {
      id: 'data-centers' as PageId,
      title: 'Global data center dashboard',
      copy: 'Explore infrastructure scale, power, connectivity, sustainability, and growth across countries.',
      stat: `${dataCenters.length} countries`
    },
    {
      id: 'waterbodies' as PageId,
      title: 'Area-wise waterbodies count of India',
      copy: 'Compare how waterbodies are distributed by size class across Indian states and territories.',
      stat: `${waterBodies.length} states`
    },
    {
      id: 'groundwater' as PageId,
      title: 'State ground water level information',
      copy: 'Inspect monitored stations, observed ranges, and states with the widest water-level spread.',
      stat: `${groundWater.reduce((sum, row) => sum + row.stations, 0).toLocaleString()} stations`
    },
    {
      id: 'cubems' as PageId,
      title: 'CUBEMS smart building energy and IAQ data',
      copy: 'Compare floor-level energy channels across the available 2018 and 2019 smart-building files.',
      stat: `${cubems.reduce((sum, row) => sum + row.rows, 0).toLocaleString()} readings`
    }
  ];

  return (
    <main className="min-h-screen bg-[#10100f] text-[#f3f0e8]">
      <section className="border-b border-white/10">
        <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8 lg:py-14">
          <div className="max-w-4xl">
            <p className="text-xs uppercase tracking-[0.24em] text-stone-400">Data analytics and visualization lab</p>
            <h1 className="mt-5 text-5xl font-semibold leading-none tracking-normal md:text-7xl">
              Environmental and infrastructure analysis hub.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-stone-400">
              Open the existing dashboard or jump into the new analysis pages for Indian waterbodies, state ground water levels, and smart-building energy data.
            </p>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-4 px-5 py-8 md:grid-cols-2 lg:px-8">
        {siteCards.map((card, index) => (
          <a
            className="group rounded-md border border-white/10 bg-white/[0.04] p-5 transition hover:border-[#D9FF62]"
            href={`#${card.id}`}
            key={card.id}
            onClick={() => onNavigate(card.id)}
          >
            <div className="flex items-start justify-between gap-4">
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full text-sm font-semibold text-stone-950" style={{ backgroundColor: getColor(index + 1) }}>
                {index + 1}
              </span>
              <span className="text-right text-sm text-stone-400">{card.stat}</span>
            </div>
            <h2 className="mt-8 text-2xl font-semibold">{card.title}</h2>
            <p className="mt-3 text-sm leading-6 text-stone-400">{card.copy}</p>
            <p className="mt-6 text-sm font-medium text-[#D9FF62]">Open analysis</p>
          </a>
        ))}
      </section>
    </main>
  );
}

function WaterBodiesDashboard() {
  const rows = React.useMemo(() => parseWaterBodiesCsv(waterBodiesCsvText), []);
  const buckets = React.useMemo(() => Object.keys(rows[0]?.buckets ?? {}), [rows]);
  const totalWaterBodies = rows.reduce((sum, row) => sum + row.total, 0);
  const largestBucket = buckets
    .map(bucket => ({ bucket, value: rows.reduce((sum, row) => sum + (row.buckets[bucket] ?? 0), 0) }))
    .sort((a, b) => b.value - a.value)[0];
  const metrics: AnalysisMetric[] = [
    { id: 'total', label: 'Total waterbodies' },
    ...buckets.map(bucket => ({ id: bucket, label: bucket }))
  ];
  const analysisRows: AnalysisRow[] = rows.map(row => ({
    id: row.state,
    label: row.state,
    metrics: {
      total: row.total,
      ...row.buckets
    }
  }));

  return (
    <AnalysisExplorer
      description="Compare state and territory waterbody counts across all area classes, then switch views to inspect ranks, shares, bucket patterns, and filtered state details."
      initialMetric="total"
      kicker="Area-wise-waterbodies-count-of-India"
      metrics={metrics}
      note="Numerical values come from the area-wise waterbodies CSV. Bucket metrics are area classes in hectares; totals are summed at runtime."
      rows={analysisRows}
      stats={[
        { label: 'States and UTs', value: rows.length.toLocaleString() },
        { label: 'Total waterbodies', value: totalWaterBodies.toLocaleString(), tone: 'light' },
        { label: 'Area buckets', value: buckets.length.toLocaleString() },
        { label: 'Largest bucket', value: largestBucket?.bucket ?? 'n/a' }
      ]}
      title="India waterbody atlas."
    />
  );
}

function GroundWaterDashboard() {
  const rows = React.useMemo(() => parseGroundWaterCsv(groundWaterCsvText), []);
  const totalStations = rows.reduce((sum, row) => sum + row.stations, 0);
  const lowest = [...rows].sort((a, b) => a.minLevel - b.minLevel)[0];
  const highest = [...rows].sort((a, b) => b.maxLevel - a.maxLevel)[0];
  const metrics: AnalysisMetric[] = [
    { id: 'stations', label: 'Monitored stations' },
    { id: 'minLevelAbs', label: 'Minimum level magnitude' },
    { id: 'maxLevel', label: 'Maximum level' },
    { id: 'spread', label: 'Observed spread' }
  ];
  const analysisRows: AnalysisRow[] = rows.map(row => ({
    id: row.state,
    label: row.state,
    subtitle: `${row.minLevel.toLocaleString()} to ${row.maxLevel.toLocaleString()}`,
    metrics: {
      stations: row.stations,
      minLevelAbs: Math.abs(row.minLevel),
      maxLevel: row.maxLevel,
      spread: row.spread
    }
  }));

  return (
    <AnalysisExplorer
      description="Explore monitored station coverage and observed water-level ranges by state, with sortable views for stations, maximums, minimum magnitude, and range spread."
      initialMetric="stations"
      kicker="State-ground-water-level-information"
      metrics={metrics}
      note="Observed minimum values can be negative in the source; the minimum metric uses absolute magnitude so it remains comparable in charts."
      rows={analysisRows}
      stats={[
        { label: 'States', value: rows.length.toLocaleString() },
        { label: 'Stations', value: totalStations.toLocaleString(), tone: 'light' },
        { label: 'Lowest min', value: `${lowest?.state ?? 'n/a'} ${lowest ? lowest.minLevel.toLocaleString() : ''}` },
        { label: 'Highest max', value: `${highest?.state ?? 'n/a'} ${highest ? highest.maxLevel.toLocaleString() : ''}` }
      ]}
      title="Ground water monitor."
    />
  );
}

function CubemsDashboard() {
  const rows = React.useMemo(() => parseCubemsSummaryCsv(cubemsSummaryCsvText), []);
  const totalReadings = rows.reduce((sum, row) => sum + row.rows, 0);
  const totalEnergy = rows.reduce((sum, row) => sum + row.totalKwMinutes, 0);
  const peakRow = [...rows].sort((a, b) => b.peakKw - a.peakKw)[0];
  const metrics: AnalysisMetric[] = [
    { id: 'totalKwMinutes', label: 'Total energy', unit: 'kW-min' },
    { id: 'lightKwMinutes', label: 'Lighting', unit: 'kW-min' },
    { id: 'plugKwMinutes', label: 'Plug load', unit: 'kW-min' },
    { id: 'acKwMinutes', label: 'AC load', unit: 'kW-min' },
    { id: 'peakKw', label: 'Peak demand', unit: 'kW' },
    { id: 'rows', label: 'Minute readings' }
  ];
  const analysisRows: AnalysisRow[] = rows.map(row => ({
    id: `${row.year}-floor-${row.floor}`,
    label: `${row.year} floor ${row.floor}`,
    subtitle: row.file,
    metrics: {
      totalKwMinutes: row.totalKwMinutes,
      lightKwMinutes: row.lightKwMinutes,
      plugKwMinutes: row.plugKwMinutes,
      acKwMinutes: row.acKwMinutes,
      peakKw: row.peakKw,
      rows: row.rows
    }
  }));

  return (
    <AnalysisExplorer
      description="Inspect floor-level smart-building energy channels for the available CUBEMS files, including total energy, lighting, plug load, AC load, peak demand, and reading volume."
      initialMetric="totalKwMinutes"
      kicker="Cubems-smart-building-energy-and-IAQ-data"
      metrics={metrics}
      note="The local CUBEMS files expose energy meter channels for Light, Plug, and AC. No IAQ sensor columns were present in the CSV headers inspected."
      rows={analysisRows}
      stats={[
        { label: 'Files', value: rows.length.toLocaleString() },
        { label: 'Minute readings', value: totalReadings.toLocaleString(), tone: 'light' },
        { label: 'Total kW-minutes', value: formatCompact(totalEnergy) },
        { label: 'Peak floor', value: peakRow ? `${peakRow.year} F${peakRow.floor}` : 'n/a' }
      ]}
      title="Smart-building energy."
    />
  );
}

function DataCenterDashboard() {
  const data = React.useMemo(() => parseDataCenterCsv(csvText), []);
  const [view, setView] = React.useState<VisualizationType>('bars');
  const [selectedMetric, setSelectedMetric] = React.useState<DataCenterMetric>('total_data_centers');
  const [xMetric, setXMetric] = React.useState<DataCenterMetric>('internet_penetration_percent');
  const [yMetric, setYMetric] = React.useState<DataCenterMetric>('total_data_centers');
  const [bubbleMetric, setBubbleMetric] = React.useState<DataCenterMetric>('power_capacity_MW_total');
  const [selectedCountry, setSelectedCountry] = React.useState('All');
  const [topN, setTopN] = React.useState(10);
  const [sortDirection, setSortDirection] = React.useState<SortDirection>('desc');

  const filteredData = selectedCountry === 'All'
    ? data
    : data.filter(row => row.country === selectedCountry);

  const sortedData = [...filteredData]
    .sort((a, b) => sortDirection === 'desc' ? b[selectedMetric] - a[selectedMetric] : a[selectedMetric] - b[selectedMetric])
    .slice(0, topN);

  const totalDataCenters = data.reduce((sum, row) => sum + row.total_data_centers, 0);
  const totalPower = data.reduce((sum, row) => sum + row.power_capacity_MW_total, 0);
  const totalFloorSpace = data.reduce((sum, row) => sum + row.floor_space_sqft_total, 0);
  const renewableRows = data.filter(row => row.average_renewable_energy_usage_percent > 0);
  const avgRenewable = renewableRows.length
    ? renewableRows.reduce((sum, row) => sum + row.average_renewable_energy_usage_percent, 0) / renewableRows.length
    : 0;
  const topCountry = [...data].sort((a, b) => b[selectedMetric] - a[selectedMetric])[0];

  function renderVisualization() {
    if (view === 'bars') return <Bars rows={sortedData} metric={selectedMetric} />;
    if (view === 'columns') return <Columns rows={sortedData} metric={selectedMetric} />;
    if (view === 'scatter') return <Scatter rows={sortedData} xMetric={xMetric} yMetric={yMetric} />;
    if (view === 'bubble') return <Scatter rows={sortedData} xMetric={xMetric} yMetric={yMetric} bubbleMetric={bubbleMetric} />;
    if (view === 'donut') return <Donut rows={sortedData} metric={selectedMetric} />;
    if (view === 'radar') return <Radar rows={sortedData} />;
    if (view === 'heatmap') return <Heatmap rows={sortedData} />;
    if (view === 'treemap') return <Treemap rows={sortedData} metric={selectedMetric} />;
    if (view === 'rankline') return <RankLine rows={sortedData} metric={selectedMetric} />;
    return <DataTable rows={sortedData} />;
  }

  return (
    <main className="min-h-screen bg-[#10100f] text-[#f3f0e8]">
      <section className="relative overflow-hidden border-b border-white/10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(217,255,98,0.18),transparent_28%),linear-gradient(120deg,rgba(255,255,255,0.08),transparent_45%)]" />
        <div className="relative mx-auto grid max-w-7xl gap-10 px-5 py-8 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-12">
          <div className="flex min-h-[360px] flex-col justify-between">
            <div className="flex items-center gap-3 text-xs uppercase tracking-[0.24em] text-stone-400">
              <span className="h-2 w-2 rounded-full bg-[#D9FF62]" />
              GDCD interactive atlas
            </div>
            <div>
              <h1 className="max-w-4xl text-6xl font-semibold leading-[0.9] tracking-normal text-[#F3F0E8] md:text-8xl">
                Global data center intelligence.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-7 text-stone-400">
                Explore infrastructure scale, power, connectivity, sustainability, and growth patterns across countries.
              </p>
            </div>
          </div>

          <div className="grid content-end gap-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-stone-500">Countries</p>
                <p className="mt-3 text-4xl font-semibold">{data.length}</p>
              </div>
              <div className="rounded-md border border-white/10 bg-[#D9FF62] p-5 text-stone-950">
                <p className="text-xs uppercase tracking-[0.18em]">Data centers</p>
                <p className="mt-3 text-4xl font-semibold">{totalDataCenters.toLocaleString()}</p>
              </div>
              <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-stone-500">Power capacity</p>
                <p className="mt-3 text-4xl font-semibold">{formatMetric(totalPower, 'power_capacity_MW_total')}</p>
              </div>
              <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-stone-500">Avg renewable</p>
                <p className="mt-3 text-4xl font-semibold">{avgRenewable.toFixed(1)}%</p>
              </div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-stone-500">Current leader</p>
              <p className="mt-3 text-3xl font-semibold">{topCountry?.country}</p>
              <p className="mt-2 text-sm text-stone-400">{metricLabels[selectedMetric]} · {formatMetric(topCountry?.[selectedMetric] ?? 0, selectedMetric)}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-6 lg:px-8">
        <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
          <div className="flex flex-wrap gap-2">
            {(Object.keys(viewLabels) as VisualizationType[]).map(option => (
              <button
                className={`rounded-full border px-4 py-2 text-sm transition ${view === option ? 'border-[#D9FF62] bg-[#D9FF62] text-stone-950' : 'border-white/15 bg-white/[0.03] text-stone-300 hover:border-white/40'}`}
                key={option}
                onClick={() => setView(option)}
                type="button"
              >
                {viewLabels[option]}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-2 sm:flex">
            <select className="rounded-md border border-white/15 bg-[#171715] px-3 py-2 text-sm" value={selectedMetric} onChange={(event) => setSelectedMetric(event.target.value as DataCenterMetric)}>
              {metrics.map(metric => <option key={metric} value={metric}>{metricLabels[metric]}</option>)}
            </select>
            <select className="rounded-md border border-white/15 bg-[#171715] px-3 py-2 text-sm" value={selectedCountry} onChange={(event) => setSelectedCountry(event.target.value)}>
              <option value="All">All countries</option>
              {data.map(row => <option key={row.country} value={row.country}>{row.country}</option>)}
            </select>
          </div>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Top N
            <input className="accent-[#D9FF62]" max="30" min="5" onChange={(event) => setTopN(Number(event.target.value))} step="1" type="range" value={topN} />
            <span className="text-sm normal-case tracking-normal text-stone-200">{topN} countries</span>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Sort
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={sortDirection} onChange={(event) => setSortDirection(event.target.value as SortDirection)}>
              <option value="desc">Highest first</option>
              <option value="asc">Lowest first</option>
            </select>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            X metric
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={xMetric} onChange={(event) => setXMetric(event.target.value as DataCenterMetric)}>
              {metrics.map(metric => <option key={metric} value={metric}>{metricLabels[metric]}</option>)}
            </select>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Y metric
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={yMetric} onChange={(event) => setYMetric(event.target.value as DataCenterMetric)}>
              {metrics.map(metric => <option key={metric} value={metric}>{metricLabels[metric]}</option>)}
            </select>
          </label>
          <label className="grid gap-2 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs uppercase tracking-[0.16em] text-stone-500">
            Bubble size
            <select className="rounded bg-[#171715] px-3 py-2 text-sm normal-case tracking-normal text-stone-100" value={bubbleMetric} onChange={(event) => setBubbleMetric(event.target.value as DataCenterMetric)}>
              {metrics.map(metric => <option key={metric} value={metric}>{metricLabels[metric]}</option>)}
            </select>
          </label>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-5 pb-12 lg:grid-cols-[1fr_320px] lg:px-8">
        <div className="rounded-md border border-white/10 bg-[#151513] p-5 shadow-2xl shadow-black/40">
          <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-stone-500">{viewLabels[view]}</p>
              <h2 className="mt-2 text-3xl font-semibold">{metricLabels[selectedMetric]}</h2>
            </div>
            <p className="max-w-md text-sm leading-6 text-stone-400">
              Showing {sortedData.length} of {filteredData.length} countries. Scatter and bubble views use the X, Y, and size controls.
            </p>
          </div>
          {renderVisualization()}
        </div>

        <aside className="grid gap-5">
          <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-stone-500">Scale</p>
            <p className="mt-3 text-3xl font-semibold">{formatMetric(totalFloorSpace, 'floor_space_sqft_total')}</p>
            <p className="mt-2 text-sm leading-6 text-stone-400">Combined floor space in the source dataset.</p>
          </div>
          <div className="rounded-md border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-stone-500">Top rows</p>
            <div className="mt-4 grid gap-3">
              {sortedData.slice(0, 5).map((row, index) => (
                <div className="flex items-center justify-between gap-3" key={row.country}>
                  <span className="flex items-center gap-2 text-sm">
                    <span className="grid h-6 w-6 place-items-center rounded-full bg-white/10 text-xs">{index + 1}</span>
                    {row.country}
                  </span>
                  <span className="text-sm text-stone-400">{formatMetric(row[selectedMetric], selectedMetric)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-md border border-white/10 bg-[#D9FF62] p-5 text-stone-950">
            <p className="text-xs uppercase tracking-[0.2em]">Dataset notes</p>
            <p className="mt-3 text-sm leading-6">
              Numerical fields are parsed from the CSV at runtime. Missing or blank values are treated as zero in visual comparisons.
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}

function getPageFromHash(): PageId {
  const hash = window.location.hash.replace('#', '') as PageId;
  return navItems.some(item => item.id === hash) ? hash : 'home';
}

export default function App() {
  const [page, setPage] = React.useState<PageId>(() => getPageFromHash());

  React.useEffect(() => {
    const handleHashChange = () => setPage(getPageFromHash());
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  function navigate(nextPage: PageId) {
    setPage(nextPage);
  }

  return (
    <>
      <TopNav page={page} onNavigate={navigate} />
      {page === 'home' && <HomePage onNavigate={navigate} />}
      {page === 'data-centers' && <DataCenterDashboard />}
      {page === 'waterbodies' && <WaterBodiesDashboard />}
      {page === 'groundwater' && <GroundWaterDashboard />}
      {page === 'cubems' && <CubemsDashboard />}
    </>
  );
}
