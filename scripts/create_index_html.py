import json

with open('data.json') as f:
    data_str = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Electric Two-Wheeler (E2W) Penetration in India | Policy Evaluation</title>
  
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
          }},
          colors: {{
            brand: {{
              50: '#ecfdf5',
              100: '#d1fae5',
              500: '#10b981',
              600: '#059669',
              700: '#047857',
            }},
            slate: {{
              850: '#151f32',
              900: '#0f172a',
              950: '#080d1a',
            }}
          }}
        }}
      }}
    }}
  </script>

  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <style>
    /* Custom scrollbars */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #0f172a;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #334155;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #475569;
    }}
    
    /* Map styling */
    .leaflet-container {{
      background: #0b1120 !important;
      font-family: inherit;
    }}
    .state-tooltip {{
      background: rgba(15, 23, 42, 0.95) !important;
      border: 1px solid rgba(51, 65, 85, 0.8) !important;
      color: #f8fafc !important;
      border-radius: 8px !important;
      padding: 8px 12px !important;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
      font-size: 12px !important;
      font-weight: 500 !important;
    }}
    .state-tooltip::before {{
      border-top-color: rgba(15, 23, 42, 0.95) !important;
    }}
    .glass-card {{
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .glass-card-hover:hover {{
      border-color: rgba(16, 185, 129, 0.3);
      box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.15);
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-emerald-500 selection:text-white">

  <!-- Inject Embedded Data directly -->
  <script>
    window.DASHBOARD_DATA = {data_str};
  </script>

  <!-- Navigation Bar -->
  <header class="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <i data-lucide="zap" class="w-5 h-5 text-white"></i>
        </div>
        <div>
          <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">E2W India Analytics</span>
          <span class="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">PS648 Policy Evaluation</span>
        </div>
      </div>

      <nav class="hidden md:flex items-center space-x-1 text-sm font-medium text-slate-300">
        <a href="#overview" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800 transition">Overview</a>
        <a href="#map-section" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800 transition">Interactive Map</a>
        <a href="#trends" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800 transition">Trends</a>
        <a href="#rankings" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800 transition">Rankings</a>
        <a href="#econometrics" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800 transition">Econometrics</a>
        <a href="#policy-matrix" class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800 transition">Policy Matrix</a>
      </nav>

      <div class="flex items-center space-x-3">
        <a href="https://github.com/narayanamalla/PS-EV-peneteration-in-india" target="_blank" class="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition">
          <i data-lucide="github" class="w-4 h-4"></i>
          <span>GitHub</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section id="overview" class="relative pt-12 pb-16 overflow-hidden">
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(16,185,129,0.08),transparent_50%)]"></div>
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_80%_80%,rgba(56,189,248,0.05),transparent_50%)]"></div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-semibold text-emerald-400 mb-4">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>Ministry of Road Transport & Highways (Vahan Registry) • FY2020–21 to FY2023–24</span>
      </div>

      <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white max-w-4xl leading-tight">
        Evaluating the Added Impact of State Purchase Incentives on <span class="bg-gradient-to-r from-emerald-400 via-teal-300 to-sky-400 bg-clip-text text-transparent">Electric Two-Wheeler Adoption in India</span>
      </h1>
      
      <p class="mt-4 text-slate-300 text-base sm:text-lg max-w-3xl leading-relaxed">
        Did Indian states offering direct consumer purchase subsidies experience faster electric two-wheeler penetration than states without additional subsidies? An empirical public policy analysis across 36 Indian states and union territories.
      </p>

      <!-- Key KPI Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
        <div class="glass-card rounded-2xl p-5 border border-slate-800 hover:border-emerald-500/30 transition">
          <div class="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>National EV Penetration</span>
            <i data-lucide="trending-up" class="w-4 h-4 text-emerald-400"></i>
          </div>
          <div class="mt-3 flex items-baseline space-x-2">
            <span class="text-3xl font-extrabold text-white">5.49%</span>
            <span class="text-xs font-bold text-emerald-400">+5.15 pp</span>
          </div>
          <p class="mt-1 text-xs text-slate-400">Up from 0.34% in FY2020–21 (16.2× expansion)</p>
        </div>

        <div class="glass-card rounded-2xl p-5 border border-slate-800 hover:border-sky-500/30 transition">
          <div class="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Annual E2W Registrations</span>
            <i data-lucide="zap" class="w-4 h-4 text-sky-400"></i>
          </div>
          <div class="mt-3 flex items-baseline space-x-2">
            <span class="text-3xl font-extrabold text-white">1,000,580</span>
          </div>
          <p class="mt-1 text-xs text-slate-400">Crossed 1M annual milestone in FY2023–24</p>
        </div>

        <div class="glass-card rounded-2xl p-5 border border-slate-800 hover:border-emerald-500/30 transition">
          <div class="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Incentive States Penetration</span>
            <i data-lucide="award" class="w-4 h-4 text-emerald-400"></i>
          </div>
          <div class="mt-3 flex items-baseline space-x-2">
            <span class="text-3xl font-extrabold text-emerald-400">7.24%</span>
            <span class="text-xs text-slate-400">vs 4.22%</span>
          </div>
          <p class="mt-1 text-xs text-slate-400">+3.02 pp premium over comparison group</p>
        </div>

        <div class="glass-card rounded-2xl p-5 border border-slate-800 hover:border-amber-500/30 transition">
          <div class="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>DiD Policy Impact</span>
            <i data-lucide="percent" class="w-4 h-4 text-amber-400"></i>
          </div>
          <div class="mt-3 flex items-baseline space-x-2">
            <span class="text-3xl font-extrabold text-amber-400">+3.48 pp</span>
            <span class="text-xs text-slate-400">p = 0.028</span>
          </div>
          <p class="mt-1 text-xs text-slate-400">Statistically significant (caveats apply)</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Interactive Map Section -->
  <section id="map-section" class="py-12 bg-slate-900/50 border-y border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400 mb-2">
            <i data-lucide="map" class="w-3.5 h-3.5"></i>
            <span>Geographic Distribution Studio</span>
          </div>
          <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Interactive Map of EV Two-Wheeler Penetration</h2>
          <p class="text-slate-400 text-sm mt-1">Official Survey of India boundaries (including full Jammu & Kashmir and Ladakh). Click on any state to inspect policy details.</p>
        </div>

        <!-- Controls: Year Selector & Timeline Player -->
        <div class="flex flex-wrap items-center gap-2">
          <div class="flex bg-slate-800 p-1 rounded-xl border border-slate-700" id="year-tabs">
            <button data-year="FY2020-21" class="year-btn px-3 py-1.5 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white">FY 2020–21</button>
            <button data-year="FY2021-22" class="year-btn px-3 py-1.5 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white">FY 2021–22</button>
            <button data-year="FY2022-23" class="year-btn px-3 py-1.5 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white">FY 2022–23</button>
            <button data-year="FY2023-24" class="year-btn px-3 py-1.5 text-xs font-bold rounded-lg transition bg-emerald-500 text-slate-950 shadow-sm">FY 2023–24</button>
          </div>

          <button id="play-btn" class="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-bold rounded-xl border border-slate-700 transition">
            <i data-lucide="play" class="w-3.5 h-3.5" id="play-icon"></i>
            <span id="play-text">Auto Play</span>
          </button>
        </div>
      </div>

      <!-- Map + Side Inspection Card Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- Left: Map Container -->
        <div class="lg:col-span-8 glass-card rounded-2xl p-4 border border-slate-800 relative">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-3 text-xs text-slate-400">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <span class="font-semibold text-slate-300">Metric: EV Two-Wheeler Penetration (%)</span>
            </div>
            <div class="flex items-center space-x-3">
              <span class="flex items-center space-x-1">
                <span class="w-3.5 h-2 rounded border border-emerald-400 bg-emerald-500/20"></span>
                <span>★ Direct Subsidy State</span>
              </span>
              <button id="reset-zoom-btn" class="text-xs text-emerald-400 hover:underline">Reset View</button>
            </div>
          </div>

          <!-- Leaflet Map Div -->
          <div id="india-map" class="w-full h-[540px] sm:h-[600px] rounded-xl overflow-hidden"></div>

          <!-- Dynamic Choropleth Legend -->
          <div class="mt-4 pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
            <span class="font-semibold text-slate-300">EV Penetration Scale:</span>
            <div class="flex items-center space-x-1">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold text-white" style="background:#2b83ba;">&lt; 1%</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold text-slate-900" style="background:#abdda4;">1–3%</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold text-slate-900" style="background:#ffffbf;">3–6%</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold text-slate-900" style="background:#fdae61;">6–10%</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold text-white" style="background:#d7191c;">&gt; 10%</span>
            </div>
            <span class="text-slate-500 text-[11px]">Hover or click state for breakdown</span>
          </div>
        </div>

        <!-- Right: State Deep Dive Card -->
        <div class="lg:col-span-4 glass-card rounded-2xl p-5 border border-slate-800 sticky top-24" id="state-inspector">
          
          <div class="flex items-start justify-between">
            <div>
              <span class="text-xs font-bold uppercase tracking-wider text-slate-400" id="inspector-tag">State Profile</span>
              <h3 class="text-2xl font-black text-white mt-0.5" id="inspector-name">Select a State</h3>
            </div>
            <span class="px-2.5 py-1 text-xs font-bold rounded-full bg-slate-800 text-slate-300 border border-slate-700" id="inspector-group">National View</span>
          </div>

          <!-- Main Stat Display -->
          <div class="mt-5 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div class="flex items-baseline justify-between">
              <div>
                <span class="text-xs text-slate-400 font-semibold" id="inspector-year-label">FY 2023–24 Penetration</span>
                <div class="text-4xl font-black text-emerald-400 mt-1" id="inspector-pen">5.49%</div>
              </div>
              <div class="text-right">
                <span class="text-xs text-slate-400 font-semibold">National Rank</span>
                <div class="text-xl font-bold text-white mt-1" id="inspector-rank">All-India</div>
              </div>
            </div>

            <!-- Progress Bar vs National Avg -->
            <div class="mt-3">
              <div class="flex justify-between text-xs text-slate-400 mb-1">
                <span>vs National Benchmark (5.49%)</span>
                <span id="inspector-diff" class="font-bold text-slate-300">Baseline</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500" id="inspector-bar" style="width: 27%;"></div>
              </div>
            </div>
          </div>

          <!-- 4-Year Adoption Mini Bar Chart -->
          <div class="mt-4">
            <span class="text-xs font-semibold text-slate-400 mb-2 block">4-Year Adoption Trajectory (% EV)</span>
            <div class="grid grid-cols-4 gap-2 text-center" id="trajectory-bars">
              <!-- Dynamically populated -->
            </div>
          </div>

          <!-- Volume Stats -->
          <div class="grid grid-cols-2 gap-3 mt-4 text-xs">
            <div class="p-3 rounded-lg bg-slate-950/40 border border-slate-800">
              <span class="text-slate-400 block">Electric 2W Count</span>
              <span class="text-base font-bold text-white mt-0.5 block" id="inspector-ev">1,000,580</span>
            </div>
            <div class="p-3 rounded-lg bg-slate-950/40 border border-slate-800">
              <span class="text-slate-400 block">Total 2W Market</span>
              <span class="text-base font-bold text-white mt-0.5 block" id="inspector-total">18,217,742</span>
            </div>
          </div>

          <!-- Policy Breakdown Box -->
          <div class="mt-4 pt-4 border-t border-slate-800 text-xs">
            <div class="flex items-center justify-between mb-1.5">
              <span class="font-bold text-slate-300">State EV Policy:</span>
              <span class="text-emerald-400 font-semibold text-[11px]" id="inspector-policy-status">Policy Active</span>
            </div>
            <p class="font-semibold text-white text-sm" id="inspector-policy-name">National FAME II + State Level Matrix</p>
            <div class="mt-2 p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-emerald-200" id="inspector-incentive-box">
              <span class="font-semibold block text-[11px] text-emerald-400">Direct Purchase Subsidy:</span>
              <span id="inspector-incentive-formula" class="text-xs">₹5,000 per kWh or fixed early-bird incentives depending on state order.</span>
            </div>
            <p class="mt-2 text-slate-400 text-[11px] leading-relaxed" id="inspector-policy-notes">
              Select any state to read the specific policy notification and gazette verification status.
            </p>
          </div>

        </div>
      </div>
    </div>
  </section>

  <!-- Adoption Trajectories & Comparative Trends Section -->
  <section id="trends" class="py-16">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="max-w-3xl mb-8">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-sky-400 mb-2">
          <i data-lucide="line-chart" class="w-3.5 h-3.5"></i>
          <span>Longitudinal Adoption Patterns</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Monthly Trajectories & Group Divergence</h2>
        <p class="text-slate-400 text-sm mt-1">High-frequency monthly registration data reveals when the incentive and comparison state trajectories diverged.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Left: 48-Month Adoption Line Chart -->
        <div class="lg:col-span-8 glass-card rounded-2xl p-6 border border-slate-800">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2 mb-4">
            <div>
              <h3 class="text-base font-bold text-white">Monthly EV Penetration Curve (Apr 2020 – Mar 2024)</h3>
              <p class="text-xs text-slate-400">Pooled EV Registrations divided by Total 2W Registrations per cohort</p>
            </div>
            <div class="flex items-center space-x-4 text-xs font-semibold">
              <span class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500"></span><span class="text-slate-300">Incentive States</span></span>
              <span class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded-full bg-sky-400"></span><span class="text-slate-300">National All-India</span></span>
              <span class="flex items-center space-x-1.5"><span class="w-3 h-3 rounded-full bg-rose-500"></span><span class="text-slate-300">Comparison States</span></span>
            </div>
          </div>
          
          <div class="w-full h-80">
            <canvas id="monthlyTrendChart"></canvas>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Key Event: Central FAME II subsidy increased to ₹15,000/kWh in June 2021</span>
            <span>48 Monthly Data Points</span>
          </div>
        </div>

        <!-- Right: Market Volume Growth Breakdown -->
        <div class="lg:col-span-4 glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 class="text-base font-bold text-white mb-1">Annual Market Transition</h3>
            <p class="text-xs text-slate-400 mb-4">Total two-wheeler registrations vs EV market share expansion.</p>
            
            <div class="w-full h-64">
              <canvas id="annualVolumeChart"></canvas>
            </div>
          </div>

          <div class="mt-4 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
            <span class="font-bold text-emerald-400 block mb-1">Market Dynamics Insight:</span>
            Overall two-wheeler sales grew 32% (13.8M → 18.2M) following pandemic rebound, while electric two-wheelers grew 2,032% (46.9k → 1.0M), proving transition was not merely a rebound artifact.
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- State League Table & Frontrunners Section -->
  <section id="rankings" class="py-16 bg-slate-900/40 border-t border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="max-w-3xl mb-8">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs font-semibold text-amber-400 mb-2">
          <i data-lucide="trophy" class="w-3.5 h-3.5"></i>
          <span>State Leaderboard & Comparative Rankings</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">State Rankings: Adoption Champions</h2>
        <p class="text-slate-400 text-sm mt-1">Comparing EV adoption across states highlights both subsidy-driven winners and surprising non-subsidized outliers.</p>
      </div>

      <!-- Top 5 Spotlight Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        
        <div class="glass-card rounded-xl p-4 border border-slate-800 hover:border-amber-500/30 transition">
          <div class="flex items-center justify-between text-xs">
            <span class="font-black text-amber-400">#1 GOA</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">Comparison</span>
          </div>
          <div class="text-2xl font-black text-white mt-2">18.15%</div>
          <p class="text-[11px] text-slate-400 mt-1">+17.65 pp gain. High disposable income, compact commuting geography.</p>
        </div>

        <div class="glass-card rounded-xl p-4 border border-slate-800 hover:border-emerald-500/30 transition">
          <div class="flex items-center justify-between text-xs">
            <span class="font-black text-emerald-400">#2 KERALA</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 font-bold">★ Incentive</span>
          </div>
          <div class="text-2xl font-black text-white mt-2">13.49%</div>
          <p class="text-[11px] text-slate-400 mt-1">+13.32 pp gain. Direct ₹15,000 cash purchase incentive for first 50k units.</p>
        </div>

        <div class="glass-card rounded-xl p-4 border border-slate-800 hover:border-sky-500/30 transition">
          <div class="flex items-center justify-between text-xs">
            <span class="font-black text-sky-400">#3 KARNATAKA</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">Comparison</span>
          </div>
          <div class="text-2xl font-black text-white mt-2">11.62%</div>
          <p class="text-[11px] text-slate-400 mt-1">+10.25 pp gain. EV innovation hub with road tax & registration fee waivers.</p>
        </div>

        <div class="glass-card rounded-xl p-4 border border-slate-800 hover:border-emerald-500/30 transition">
          <div class="flex items-center justify-between text-xs">
            <span class="font-black text-emerald-400">#4 MAHARASHTRA</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 font-bold">★ Incentive</span>
          </div>
          <div class="text-2xl font-black text-white mt-2">10.10%</div>
          <p class="text-[11px] text-slate-400 mt-1">+9.54 pp gain. Early-bird subsidy of up to ₹25,000 launched in July 2021.</p>
        </div>

        <div class="glass-card rounded-xl p-4 border border-slate-800 hover:border-emerald-500/30 transition">
          <div class="flex items-center justify-between text-xs">
            <span class="font-black text-emerald-400">#5 DELHI</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 font-bold">★ Incentive</span>
          </div>
          <div class="text-2xl font-black text-white mt-2">9.37%</div>
          <p class="text-[11px] text-slate-400 mt-1">+8.76 pp gain. August 2020 pioneer policy with up to ₹30,000 subsidy.</p>
        </div>

      </div>

      <!-- Filterable Full State Table -->
      <div class="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        
        <!-- Table Controls Bar -->
        <div class="p-4 sm:p-5 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="relative flex-1 max-w-sm">
            <i data-lucide="search" class="w-4 h-4 absolute left-3 top-3 text-slate-400"></i>
            <input type="text" id="table-search" placeholder="Search state or UT..." class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition">
          </div>

          <div class="flex items-center gap-2">
            <div class="flex bg-slate-950 p-1 rounded-xl border border-slate-800" id="table-filter-pills">
              <button data-filter="all" class="table-filter-btn px-3 py-1.5 text-xs font-bold rounded-lg bg-slate-800 text-white">All (36)</button>
              <button data-filter="incentive" class="table-filter-btn px-3 py-1.5 text-xs font-bold rounded-lg text-slate-400 hover:text-white">Incentive (8)</button>
              <button data-filter="comparison" class="table-filter-btn px-3 py-1.5 text-xs font-bold rounded-lg text-slate-400 hover:text-white">Comparison (28)</button>
            </div>
          </div>
        </div>

        <!-- Table Container -->
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs" id="state-league-table">
            <thead class="bg-slate-950/80 text-slate-400 uppercase font-bold tracking-wider border-b border-slate-800">
              <tr>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="rank">Rank <i data-lucide="arrow-up-down" class="inline w-3 h-3 ml-0.5"></i></th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="name">State / UT <i data-lucide="arrow-up-down" class="inline w-3 h-3 ml-0.5"></i></th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="group">Incentive Status</th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="fy21">FY21 %</th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="fy22">FY22 %</th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="fy23">FY23 %</th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white text-emerald-400 font-extrabold" data-sort="fy24">FY24 Penetration <i data-lucide="arrow-up-down" class="inline w-3 h-3 ml-0.5"></i></th>
                <th class="py-3.5 px-4 cursor-pointer hover:text-white" data-sort="change">4-Yr Change (pp) <i data-lucide="arrow-up-down" class="inline w-3 h-3 ml-0.5"></i></th>
                <th class="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 font-medium" id="table-body">
              <!-- Populated by JS -->
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

  <!-- Econometrics & Policy Impact Evaluation Section -->
  <section id="econometrics" class="py-16">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="max-w-3xl mb-8">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400 mb-2">
          <i data-lucide="scale" class="w-3.5 h-3.5"></i>
          <span>Econometric Evaluation</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Difference-in-Differences & Causal Assessment</h2>
        <p class="text-slate-400 text-sm mt-1">Rigorous public policy evaluation testing whether state subsidies caused adoption gains or merely rewarded pre-existing advantages.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Left: Model Estimates Table -->
        <div class="lg:col-span-6 glass-card rounded-2xl p-6 border border-slate-800">
          <h3 class="text-lg font-bold text-white mb-2">Model Specifications & Results</h3>
          <p class="text-xs text-slate-400 mb-6">Estimated using state-level panel observations with heteroskedasticity and cluster-robust standard errors.</p>

          <div class="space-y-4">
            <!-- Simple DiD Box -->
            <div class="p-4 rounded-xl bg-slate-950/80 border border-emerald-500/30">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-emerald-400">Model 1: Simple Difference-in-Differences (OLS HC3)</span>
                <span class="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/20 text-emerald-300">Statistically Significant</span>
              </div>
              <div class="text-3xl font-black text-white">+3.48 percentage points</div>
              <div class="grid grid-cols-3 gap-2 mt-3 text-xs text-slate-400">
                <div><span class="block text-slate-500">Std Error:</span> <span class="font-bold text-white">1.589 pp</span></div>
                <div><span class="block text-slate-500">95% CI:</span> <span class="font-bold text-white">[0.37, 6.60]</span></div>
                <div><span class="block text-slate-500">p-value:</span> <span class="font-bold text-emerald-400">0.028</span></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-800/80">
                Incentive states gained 6.78 pp vs comparison states gaining 3.29 pp between FY20-21 and FY23-24.
              </p>
            </div>

            <!-- TWFE Box -->
            <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-slate-300">Model 2: Two-Way Fixed Effects (State & Year FE)</span>
                <span class="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-800 text-slate-400">p = 0.083</span>
              </div>
              <div class="text-3xl font-black text-white">+1.74 percentage points</div>
              <div class="grid grid-cols-3 gap-2 mt-3 text-xs text-slate-400">
                <div><span class="block text-slate-500">Clustered SE:</span> <span class="font-bold text-white">1.003 pp</span></div>
                <div><span class="block text-slate-500">95% CI:</span> <span class="font-bold text-white">[-0.23, 3.71]</span></div>
                <div><span class="block text-slate-500">R-squared:</span> <span class="font-bold text-white">0.739 (N=144)</span></div>
              </div>
              <p class="text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-800/80">
                Controlling for unobserved time-invariant state characteristics attenuates the coefficient by 50%, indicating that part of the observed gap was due to baseline structural differences.
              </p>
            </div>
          </div>
        </div>

        <!-- Right: 3 Key Policy Caveats Card -->
        <div class="lg:col-span-6 glass-card rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 class="text-lg font-bold text-white mb-2">Critical Public Policy Caveats</h3>
            <p class="text-xs text-slate-400 mb-4">Why a difference in adoption cannot be uncritically interpreted as pure subsidy causality:</p>

            <div class="space-y-3.5 text-xs">
              <div class="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-amber-200">
                <div class="font-bold text-amber-400 flex items-center space-x-1.5 mb-1">
                  <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i>
                  <span>1. Pre-Treatment Baseline Imbalance</span>
                </div>
                Incentive states had higher EV adoption before policies were enacted (0.39% vs 0.16% in FY20-21, t=2.18, p=0.037). Parallel trends cannot be verified with only one pre-treatment financial year.
              </div>

              <div class="p-3.5 rounded-xl bg-sky-950/20 border border-sky-500/20 text-sky-200">
                <div class="font-bold text-sky-400 flex items-center space-x-1.5 mb-1">
                  <i data-lucide="info" class="w-3.5 h-3.5"></i>
                  <span>2. National FAME II Program Confounding</span>
                </div>
                Central demand incentives under FAME II (which increased from ₹10,000/kWh to ₹15,000/kWh in June 2021) applied nationally to all states, driving the overall baseline adoption wave.
              </div>

              <div class="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-emerald-200">
                <div class="font-bold text-emerald-400 flex items-center space-x-1.5 mb-1">
                  <i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>
                  <span>3. The "Unsubsidized Outliers"</span>
                </div>
                Goa (18.15%) and Karnataka (11.62%) rank #1 and #3 nationwide without direct consumer cash purchase subsidies. High urbanization, road tax waivers, and charging networks often matter more than direct cash outlays.
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500">
            Methodology: Evaluated per Angrist & Pischke guidelines and Callaway-Sant'Anna staggered DiD principles.
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- State EV Policy Matrix Section -->
  <section id="policy-matrix" class="py-16 bg-slate-900/40 border-t border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="max-w-3xl mb-8">
        <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-semibold text-emerald-400 mb-2">
          <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
          <span>Official Gazette Documentation</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight">Verified State Purchase Incentive Policies (8 States)</h2>
        <p class="text-slate-400 text-sm mt-1">Direct consumer purchase subsidy notifications verified against state government gazettes and orders.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" id="policy-cards-grid">
        <!-- Injected via JavaScript for the 8 incentive states -->
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="bg-slate-950 border-t border-slate-800/80 py-12 text-slate-400 text-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
      <div>
        <div class="flex items-center space-x-2 font-bold text-slate-200 text-sm">
          <i data-lucide="zap" class="w-4 h-4 text-emerald-400"></i>
          <span>E2W India Public Policy Research</span>
        </div>
        <p class="mt-1 text-slate-500">PS648 Data Visualisation for Public Policy • Ministry of Road Transport & Highways Data</p>
      </div>

      <div class="flex flex-wrap items-center gap-6">
        <a href="https://github.com/narayanamalla/PS-EV-peneteration-in-india" target="_blank" class="hover:text-emerald-400 transition flex items-center space-x-1">
          <i data-lucide="github" class="w-3.5 h-3.5"></i>
          <span>GitHub Source</span>
        </a>
        <a href="data/processed/cleaned_state_monthly_data.csv" download class="hover:text-emerald-400 transition flex items-center space-x-1">
          <i data-lucide="download" class="w-3.5 h-3.5"></i>
          <span>Monthly CSV (1,728 rows)</span>
        </a>
        <a href="data/processed/cleaned_state_financial_year_data.csv" download class="hover:text-emerald-400 transition flex items-center space-x-1">
          <i data-lucide="download" class="w-3.5 h-3.5"></i>
          <span>Annual CSV (144 rows)</span>
        </a>
      </div>
    </div>
  </footer>

  <!-- Main JavaScript Application Logic -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      lucide.createIcons();
      initDashboard();
    }});

    // Global application state
    const appState = {{
      currentYear: 'FY2023-24',
      selectedState: 'Maharashtra',
      isPlaying: false,
      playInterval: null,
      tableFilter: 'all',
      tableSearch: '',
      sortField: 'fy24',
      sortAsc: false
    }};

    let leafletMap = null;
    let geoLayer = null;
    let monthlyChart = null;
    let volumeChart = null;

    // Color ramp for choropleth (Spectral_r style)
    function getChoroplethColor(val) {{
      if (val === null || val === undefined || isNaN(val)) return '#334155';
      if (val < 1.0)  return '#2b83ba'; // Cool deep blue
      if (val < 3.0)  return '#abdda4'; // Mint green
      if (val < 6.0)  return '#ffffbf'; // Warm pale yellow
      if (val < 10.0) return '#fdae61'; // Vibrant orange
      return '#d7191c';                 // Ruby crimson
    }}

    function initDashboard() {{
      const data = window.DASHBOARD_DATA;
      if (!data) return;

      initMap(data);
      initCharts(data);
      initTable(data);
      initPolicyCards(data);
      updateInspector(data.states[appState.selectedState], appState.currentYear);
      setupEventListeners(data);
    }}

    // ── 1. Map Initialization (Leaflet) ─────────────────────────────────────────
    function initMap(data) {{
      leafletMap = L.map('india-map', {{
        center: [22.8, 80.5],
        zoom: 4.4,
        minZoom: 4,
        maxZoom: 7,
        zoomControl: false,
        attributionControl: false
      }});

      L.control.zoom({{ position: 'topright' }}).addTo(leafletMap);

      renderGeoLayer(data);
    }}

    function renderGeoLayer(data) {{
      if (geoLayer) leafletMap.removeLayer(geoLayer);

      geoLayer = L.geoJSON(data.geo_json, {{
        style: (feature) => {{
          const stName = feature.properties.state;
          const stData = data.states[stName];
          const val = stData ? stData.years[appState.currentYear]?.penetration_pct : 0;
          const isSelected = (stName === appState.selectedState);
          const hasIncentive = stData?.has_direct_incentive;

          return {{
            fillColor: getChoroplethColor(val),
            weight: isSelected ? 2.8 : (hasIncentive ? 1.8 : 0.8),
            opacity: 1,
            color: isSelected ? '#10b981' : (hasIncentive ? '#38bdf8' : '#475569'),
            fillOpacity: isSelected ? 0.95 : 0.85
          }};
        }},
        onEachFeature: (feature, layer) => {{
          const stName = feature.properties.state;
          const stData = data.states[stName];

          // Tooltip on hover
          layer.on('mouseover', (e) => {{
            const val = stData ? stData.years[appState.currentYear]?.penetration_pct : 0;
            const incBadge = stData?.has_direct_incentive ? '★ Direct Subsidy' : 'Comparison';
            layer.bindTooltip(`
              <div class="font-bold text-sm">${{stName}}</div>
              <div class="text-xs text-slate-300 mt-0.5">EV Penetration: <span class="text-emerald-400 font-extrabold text-sm">${{val}}%</span></div>
              <div class="text-[10px] text-slate-400 mt-1">${{incBadge}}</div>
            `, {{ className: 'state-tooltip', sticky: true }}).openTooltip();

            e.target.setStyle({{
              weight: 2.5,
              color: '#ffffff',
              fillOpacity: 1
            }});
          }});

          layer.on('mouseout', (e) => {{
            const isSelected = (stName === appState.selectedState);
            const hasIncentive = stData?.has_direct_incentive;
            e.target.setStyle({{
              weight: isSelected ? 2.8 : (hasIncentive ? 1.8 : 0.8),
              color: isSelected ? '#10b981' : (hasIncentive ? '#38bdf8' : '#475569'),
              fillOpacity: isSelected ? 0.95 : 0.85
            }});
          }});

          // Click to inspect
          layer.on('click', () => {{
            appState.selectedState = stName;
            updateInspector(stData, appState.currentYear);
            renderGeoLayer(data);
          }});
        }}
      }}).addTo(leafletMap);
    }}

    // ── 2. Inspector Update Logic ───────────────────────────────────────────────
    function updateInspector(stData, year) {{
      if (!stData) return;
      const yrData = stData.years[year] || {{ penetration_pct: 0, total_2w: 0, electric_2w: 0 }};

      document.getElementById('inspector-name').textContent = stData.name;
      document.getElementById('inspector-tag').textContent = `State Profile • ${{year}}`;
      
      const grpBadge = document.getElementById('inspector-group');
      if (stData.has_direct_incentive) {{
        grpBadge.textContent = '★ Direct Purchase Subsidy';
        grpBadge.className = 'px-2.5 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
      }} else {{
        grpBadge.textContent = 'Comparison Group';
        grpBadge.className = 'px-2.5 py-1 text-xs font-bold rounded-full bg-slate-800 text-slate-300 border border-slate-700';
      }}

      document.getElementById('inspector-pen').textContent = `${{yrData.penetration_pct.toFixed(2)}}%`;
      document.getElementById('inspector-rank').textContent = `#${{stData.rank_fy24}} of 36`;

      // Difference vs National 5.49%
      const diff = yrData.penetration_pct - 5.49;
      const diffEl = document.getElementById('inspector-diff');
      if (diff >= 0) {{
        diffEl.textContent = `+${{diff.toFixed(2)}} pp above national`;
        diffEl.className = 'font-bold text-emerald-400';
      }} else {{
        diffEl.textContent = `${{diff.toFixed(2)}} pp below national`;
        diffEl.className = 'font-bold text-rose-400';
      }}

      // Bar width capped at 100%
      const barPct = Math.min(100, Math.max(5, (yrData.penetration_pct / 20.0) * 100));
      document.getElementById('inspector-bar').style.width = `${{barPct}}%`;

      document.getElementById('inspector-ev').textContent = yrData.electric_2w.toLocaleString();
      document.getElementById('inspector-total').textContent = yrData.total_2w.toLocaleString();

      // Policy Info
      document.getElementById('inspector-policy-name').textContent = stData.policy_name;
      document.getElementById('inspector-policy-status').textContent = stData.has_direct_incentive ? 'Verified Cash Subsidy' : 'Tax / Infrastructure Waiver';
      document.getElementById('inspector-incentive-formula').textContent = stData.incentive_amount;
      document.getElementById('inspector-policy-notes').textContent = stData.notes || 'No state policy notes recorded.';

      // Render Trajectory Mini Bar Chart
      const trajContainer = document.getElementById('trajectory-bars');
      trajContainer.innerHTML = '';
      const years = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24'];
      years.forEach(y => {{
        const p = stData.years[y]?.penetration_pct || 0;
        const isCurrent = (y === year);
        const colDiv = document.createElement('div');
        colDiv.className = `p-2 rounded-lg border transition ${{isCurrent ? 'bg-emerald-500/20 border-emerald-500 text-white font-bold' : 'bg-slate-950/60 border-slate-800 text-slate-400'}}`;
        colDiv.innerHTML = `
          <span class="block text-[10px] text-slate-400">${{y.replace('FY20', '')}}</span>
          <span class="text-xs font-black ${{isCurrent ? 'text-emerald-400' : 'text-slate-200'}}">${{p}}%</span>
        `;
        trajContainer.appendChild(colDiv);
      }});
    }}

    // ── 3. Chart.js Initialization ──────────────────────────────────────────────
    function initCharts(data) {{
      // 1. Monthly line chart
      const ctxMonthly = document.getElementById('monthlyTrendChart').getContext('2d');
      const labels = data.monthly_trend.map(d => d.label);
      const incData = data.monthly_trend.map(d => d.penetration_incentive);
      const natData = data.monthly_trend.map(d => d.penetration_all);
      const cmpData = data.monthly_trend.map(d => d.penetration_comparison);

      monthlyChart = new Chart(ctxMonthly, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Incentive States Pooled',
              data: incData,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderWidth: 2.5,
              tension: 0.25,
              fill: true,
              pointRadius: 0,
              pointHoverRadius: 5
            }},
            {{
              label: 'National All-India',
              data: natData,
              borderColor: '#38bdf8',
              borderWidth: 2,
              tension: 0.25,
              borderDash: [4, 4],
              pointRadius: 0,
              pointHoverRadius: 5
            }},
            {{
              label: 'Comparison States Pooled',
              data: cmpData,
              borderColor: '#f43f5e',
              borderWidth: 2,
              tension: 0.25,
              pointRadius: 0,
              pointHoverRadius: 5
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'index', intersect: false }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderWidth: 1,
              titleColor: '#ffffff',
              bodyColor: '#cbd5e1',
              padding: 10,
              callbacks: {{
                label: (c) => `${{c.dataset.label}}: ${{c.parsed.y.toFixed(2)}}%`
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }}, maxTicksLimit: 8 }}
            }},
            y: {{
              grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }}, callback: (v) => `${{v}}%` }}
            }}
          }}
        }}
      }});

      // 2. Annual volume chart
      const ctxVol = document.getElementById('annualVolumeChart').getContext('2d');
      const fyLabels = data.national_annual.map(d => d.financial_year.replace('FY20', 'FY'));
      const totalVols = data.national_annual.map(d => (d.total_2w / 1000000).toFixed(1));
      const evPcts = data.national_annual.map(d => d.penetration_pct);

      volumeChart = new Chart(ctxVol, {{
        type: 'bar',
        data: {{
          labels: fyLabels,
          datasets: [
            {{
              type: 'bar',
              label: 'Total 2W (Millions)',
              data: totalVols,
              backgroundColor: 'rgba(51, 65, 85, 0.6)',
              borderRadius: 6,
              yAxisID: 'y'
            }},
            {{
              type: 'line',
              label: 'EV Share (%)',
              data: evPcts,
              borderColor: '#10b981',
              borderWidth: 2.5,
              pointBackgroundColor: '#10b981',
              pointRadius: 4,
              yAxisID: 'y1'
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderWidth: 1
            }}
          }},
          scales: {{
            x: {{
              grid: {{ display: false }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}
            }},
            y: {{
              grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }}, callback: (v) => `${{v}}M` }}
            }},
            y1: {{
              position: 'right',
              grid: {{ display: false }},
              ticks: {{ color: '#10b981', font: {{ size: 10 }}, callback: (v) => `${{v}}%` }}
            }}
          }}
        }}
      }});
    }}

    // ── 4. Table Logic & Sorting ────────────────────────────────────────────────
    function initTable(data) {{
      renderTableRows(data);
    }}

    function renderTableRows(data) {{
      const tbody = document.getElementById('table-body');
      tbody.innerHTML = '';

      let list = Object.values(data.states);

      // Filtering
      if (appState.tableFilter === 'incentive') {{
        list = list.filter(s => s.has_direct_incentive);
      }} else if (appState.tableFilter === 'comparison') {{
        list = list.filter(s => !s.has_direct_incentive);
      }}

      // Search
      if (appState.tableSearch) {{
        const q = appState.tableSearch.toLowerCase();
        list = list.filter(s => s.name.toLowerCase().includes(q));
      }}

      // Sorting
      list.sort((a, b) => {{
        let vA, vB;
        if (appState.sortField === 'rank') {{ vA = a.rank_fy24; vB = b.rank_fy24; }}
        else if (appState.sortField === 'name') {{ vA = a.name; vB = b.name; }}
        else if (appState.sortField === 'group') {{ vA = a.has_direct_incentive ? 1 : 0; vB = b.has_direct_incentive ? 1 : 0; }}
        else if (appState.sortField === 'fy21') {{ vA = a.years['FY2020-21'].penetration_pct; vB = b.years['FY2020-21'].penetration_pct; }}
        else if (appState.sortField === 'fy22') {{ vA = a.years['FY2021-22'].penetration_pct; vB = b.years['FY2021-22'].penetration_pct; }}
        else if (appState.sortField === 'fy23') {{ vA = a.years['FY2022-23'].penetration_pct; vB = b.years['FY2022-23'].penetration_pct; }}
        else if (appState.sortField === 'fy24') {{ vA = a.years['FY2023-24'].penetration_pct; vB = b.years['FY2023-24'].penetration_pct; }}
        else if (appState.sortField === 'change') {{ vA = a.change_pp; vB = b.change_pp; }}

        if (typeof vA === 'string') {{
          return appState.sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
        }}
        return appState.sortAsc ? vA - vB : vB - vA;
      }});

      list.forEach(s => {{
        const p24 = s.years['FY2023-24'].penetration_pct;
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition cursor-pointer';
        tr.innerHTML = `
          <td class="py-3 px-4 font-bold text-slate-400">#${{s.rank_fy24}}</td>
          <td class="py-3 px-4 font-bold text-white flex items-center space-x-2">
            <span>${{s.name}}</span>
          </td>
          <td class="py-3 px-4">
            ${{s.has_direct_incentive 
              ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">★ Subsidy</span>' 
              : '<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">Tax Waiver</span>'}}
          </td>
          <td class="py-3 px-4 text-slate-400">${{s.years['FY2020-21'].penetration_pct}}%</td>
          <td class="py-3 px-4 text-slate-400">${{s.years['FY2021-22'].penetration_pct}}%</td>
          <td class="py-3 px-4 text-slate-400">${{s.years['FY2022-23'].penetration_pct}}%</td>
          <td class="py-3 px-4">
            <div class="flex items-center space-x-2">
              <span class="font-black text-emerald-400 text-sm">${{p24}}%</span>
              <div class="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-emerald-400 h-full rounded-full" style="width: ${{Math.min(100, (p24 / 20) * 100)}}%;"></div>
              </div>
            </div>
          </td>
          <td class="py-3 px-4 font-bold ${{s.change_pp >= 5 ? 'text-emerald-400' : 'text-slate-300'}}">+${{s.change_pp.toFixed(2)}} pp</td>
          <td class="py-3 px-4 text-right">
            <button class="px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-600 hover:text-white text-slate-300 text-[11px] font-semibold transition" onclick="inspectFromTable('${{s.name}}')">
              Inspect
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    window.inspectFromTable = function(name) {{
      appState.selectedState = name;
      updateInspector(window.DASHBOARD_DATA.states[name], appState.currentYear);
      renderGeoLayer(window.DASHBOARD_DATA);
      document.getElementById('map-section').scrollIntoView({{ behavior: 'smooth' }});
    }};

    // ── 5. Policy Matrix Cards ──────────────────────────────────────────────────
    function initPolicyCards(data) {{
      const grid = document.getElementById('policy-cards-grid');
      grid.innerHTML = '';

      const incStates = Object.values(data.states).filter(s => s.has_direct_incentive);
      incStates.sort((a, b) => b.years['FY2023-24'].penetration_pct - a.years['FY2023-24'].penetration_pct);

      incStates.forEach(s => {{
        const card = document.createElement('div');
        card.className = 'glass-card rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 transition flex flex-col justify-between';
        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between text-xs mb-2">
              <span class="font-bold text-white text-sm">${{s.name}}</span>
              <span class="text-emerald-400 font-extrabold text-xs">${{s.years['FY2023-24'].penetration_pct}}%</span>
            </div>
            <div class="text-[11px] font-semibold text-slate-300 mb-1">${{s.policy_name}}</div>
            <div class="p-2 rounded bg-slate-950/60 border border-slate-800 text-[11px] text-emerald-300 mb-2">
              ${{s.incentive_amount}}
            </div>
            <p class="text-[11px] text-slate-400 leading-relaxed">${{s.notes}}</p>
          </div>
          <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
            <span>Effective: ${{s.effective_date}}</span>
            <span class="text-emerald-400 font-medium">Verified Order</span>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    // ── 6. Event Listeners & Auto-Play ──────────────────────────────────────────
    function setupEventListeners(data) {{
      // Year selector pills
      const yearBtns = document.querySelectorAll('.year-btn');
      yearBtns.forEach(btn => {{
        btn.addEventListener('click', () => {{
          stopPlay();
          setYear(btn.getAttribute('data-year'), data);
        }});
      }});

      // Auto-play button
      const playBtn = document.getElementById('play-btn');
      playBtn.addEventListener('click', () => {{
        if (appState.isPlaying) {{
          stopPlay();
        }} else {{
          startPlay(data);
        }}
      }});

      // Reset zoom
      document.getElementById('reset-zoom-btn').addEventListener('click', () => {{
        leafletMap.setView([22.8, 80.5], 4.4);
      }});

      // Table search
      document.getElementById('table-search').addEventListener('input', (e) => {{
        appState.tableSearch = e.target.value;
        renderTableRows(data);
      }});

      // Table filter pills
      const filterBtns = document.querySelectorAll('.table-filter-btn');
      filterBtns.forEach(btn => {{
        btn.addEventListener('click', () => {{
          filterBtns.forEach(b => {{
            b.className = 'table-filter-btn px-3 py-1.5 text-xs font-bold rounded-lg text-slate-400 hover:text-white';
          }});
          btn.className = 'table-filter-btn px-3 py-1.5 text-xs font-bold rounded-lg bg-slate-800 text-white';
          appState.tableFilter = btn.getAttribute('data-filter');
          renderTableRows(data);
        }});
      }});

      // Table column sorting
      const headers = document.querySelectorAll('#state-league-table th[data-sort]');
      headers.forEach(th => {{
        th.addEventListener('click', () => {{
          const field = th.getAttribute('data-sort');
          if (appState.sortField === field) {{
            appState.sortAsc = !appState.sortAsc;
          }} else {{
            appState.sortField = field;
            appState.sortAsc = false;
          }}
          renderTableRows(data);
        }});
      }});
    }}

    function setYear(year, data) {{
      appState.currentYear = year;

      // Update button styles
      document.querySelectorAll('.year-btn').forEach(btn => {{
        if (btn.getAttribute('data-year') === year) {{
          btn.className = 'year-btn px-3 py-1.5 text-xs font-bold rounded-lg bg-emerald-500 text-slate-950 shadow-sm';
        }} else {{
          btn.className = 'year-btn px-3 py-1.5 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition';
        }}
      }});

      renderGeoLayer(data);
      updateInspector(data.states[appState.selectedState], year);
    }}

    function startPlay(data) {{
      appState.isPlaying = true;
      document.getElementById('play-text').textContent = 'Pause';
      document.getElementById('play-icon').setAttribute('data-lucide', 'pause');
      lucide.createIcons();

      const years = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24'];
      let idx = years.indexOf(appState.currentYear);

      appState.playInterval = setInterval(() => {{
        idx = (idx + 1) % years.length;
        setYear(years[idx], data);
      }}, 2200);
    }}

    function stopPlay() {{
      appState.isPlaying = false;
      clearInterval(appState.playInterval);
      document.getElementById('play-text').textContent = 'Auto Play';
      document.getElementById('play-icon').setAttribute('data-lucide', 'play');
      lucide.createIcons();
    }}
  </script>
</body>
</html>
"""

with open('index.html', 'w') as f:
    f.write(html_content)

print('index.html generated successfully!')
