# World Monitor Codebase Structure

**Repository:** https://github.com/koala73/worldmonitor  
**Clone location:** `/home/yeoel/.openclaw/workspace/worldmonitor`  
**Last reviewed:** 2026-04-13

---

## Top-Level Architecture

World Monitor is a **real-time global intelligence dashboard** — TypeScript SPA with dual map rendering (globe.gl 3D + deck.gl WebGL flat map), 65+ upstream data sources, AI-powered news synthesis, and a desktop Tauri app.

**Stack:**
- Frontend: Vanilla TypeScript, Vite, globe.gl + Three.js, deck.gl + MapLibre GL
- Desktop: Tauri 2 (Rust) with Node.js sidecar
- AI/ML: Ollama / Groq / OpenRouter, Transformers.js (browser-side ONNX)
- API: Protocol Buffers via sebuf (92 protos, 22 services), Vercel Edge Functions
- Backend: Convex (cloud), Railway relay (AIS WebSocket), Upstash Redis
- Deployment: Vercel Edge Functions, Railway, Docker (GHCR)

---

## Key Directories

### `src/` — Browser SPA (TypeScript)
| Subdir | Purpose |
|--------|---------|
| `app/` | App orchestration managers |
| `bootstrap/` | Chunk reload recovery |
| `components/` | 86+ Panel subclasses + map components (DeckGLMap.ts, GlobeMap.ts) |
| `config/` | Variant, panel, layer, market configurations |
| `generated/` | Proto-generated client/server stubs (DO NOT EDIT) |
| `locales/` | i18n translation files (21 languages) |
| `services/` | Business logic organized by domain |
| `types/` | TypeScript type definitions |
| `utils/` | Shared utilities (circuit-breaker, theme, URL state) |
| `workers/` | Web Workers (analysis, ML, vector DB) |

### `api/` — Vercel Edge Functions (self-contained JS, cannot import from `src/` or `server/`)
| Subdir | Domain |
|--------|--------|
| `aviation/` | Flight data, OpenSky, airline intel |
| `climate/` | Climate anomalies, air quality, EONET |
| `conflict/` | ACLED, UCDP, displacement, unrest |
| `cyber/` | Security advisories, threat intel |
| `economic/` | Macro data, sanctions, trade |
| `forecast/` | Market forecasts, predictions |
| `health/` | Disease outbreaks |
| `imagery/` | Satellite imagery, webcams |
| `infrastructure/` | Cable health, energy grids |
| `intelligence/` | GDELT, news aggregation |
| `maritime/` | AIS, vessels, Hormuz tracker |
| `market/` | Stocks, commodities, crypto, ETF flows |
| `military/` | Military flights, bases, vessels, posture |
| `news/` | RSS aggregation, live news |
| `prediction/` | ML predictions, sentiment |
| `supply-chain/` | Supply chain signals, Hormuz |
| `trade/` | Trade data, tariffs |
| `wildfire/` | FIRMS fire data |
| `enrichment/` | Company lookup, signals enrichment |
| `oauth/` | OAuth registration/authorization |
| `skills/` | AgentSkills fetching |
| `_*.js` | Shared helpers (_cors, _rate-limit, _api-key, _relay, etc.) |

### `server/` — Server-side code (bundled into Edge Functions)
| Subdir | Purpose |
|--------|---------|
| `_shared/` | Redis, rate-limit, LLM, caching utilities |
| `worldmonitor/<domain>/` | Domain handlers (mirrors proto structure) |
| `gateway.ts` | Domain gateway factory (rate-limit, ETag, cache headers) |
| `router.ts` | Route matching |

### `scripts/` — Seed scripts & build helpers
- `seed-*.mjs` — fetch upstream data, write to Redis
- `ais-relay.cjs` — Railway WebSocket proxy + seed loops
- `_seed-utils.mjs` — atomic publish with Redis lock

### `src-tauri/` — Desktop Tauri app
- `src/` — Rust shell (lifecycle, tray, window management)
- `sidecar/` — Node.js sidecar that loads Edge Function handlers locally

### `proto/` — Protocol Buffer definitions
- `sebuf/` — sebuf framework
- `worldmonitor/` — service definitions with `(sebuf.http.config)` annotations

### `convex/` — Convex cloud backend
- Contact form, waitlist, entitlements, checkout

### `docs/` — Mintlify documentation site
- Architecture, data sources, API contracts

### `tests/` — Unit/integration tests (node:test)
### `e2e/` — Playwright E2E specs

---

## Component Overview (selected key panels)

**Map:** `DeckGLMap.ts`, `GlobeMap.ts`  
**Intelligence:** `LiveNewsPanel.ts`, `CountryBriefPanel.ts`, `CountryDeepDivePanel.ts`  
**Market:** `DailyMarketBriefPanel.ts`, `ETFFlowsPanel.ts`, `FearGreedPanel.ts`, `CotPositioningPanel.ts`  
**Military:** `MilitaryFlightsPanel.ts`, `MilitaryVesselsPanel.ts`, `CountryInstabilityPanel.ts`  
**Climate:** `ClimateAnomalyPanel.ts`, `DiseaseOutbreaksPanel.ts`, `WildfirePanel.ts`  
**Supply Chain:** `HormuzPanel.ts`, `SupplyChainPanel.ts`  
**AI:** `ChatAnalystPanel.ts`, `InsightsPanel.ts`, `CorrelationPanel.ts`

---

## Variant System

5 site variants from single codebase, detected by hostname:

| Variant | Hostname | Default Focus |
|---------|----------|---------------|
| world | worldmonitor.app | Full global intelligence |
| tech | tech.worldmonitor.app | Technology sector |
| finance | finance.worldmonitor.app | Financial markets |
| commodity | commodity.worldmonitor.app | Commodities |
| happy | happy.worldmonitor.app | Positive events |

---

## Key Patterns

1. **Two-tier bootstrap** — `/api/bootstrap` with fast (3s) + slow (5s) hydration
2. **Cache-miss coalescing** — concurrent requests share a single upstream fetch
3. **Circuit breaker** — per-upstream circuit breakers with cascade fallback chains
4. **ETag caching** — FNV-1a hash as ETag, 304 responses, CDN layer
5. **Seed metadata** — every Redis write also writes `seed-meta:<key>` with freshness info
6. **Desktop fetch patch** — `globalThis.fetch` patched to route `/api/*` through Tauri sidecar
7. **Proto-generated RPC** — 92 protos generate TypeScript stubs, CI enforces committed output freshness

---

## Self-Hosting Options

- **Vercel** — Edge Functions + Convex
- **Docker** — GHCR multi-arch image (amd64, arm64), nginx serving built SPA
- **Desktop** — Tauri app (macOS ARM64/x64, Windows x64, Linux x64/ARM64, AppImage)
- **Railway** — AIS relay + seed loops

---

## License

AGPL-3.0 for non-commercial. Commercial license required for SaaS/rebranding.
**Copyright (C) 2024-2026 Elie Habib**
