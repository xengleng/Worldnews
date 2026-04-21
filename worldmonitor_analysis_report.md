# WorldMonitor Codebase Analysis Report

## 📊 Executive Summary

**WorldMonitor** is a sophisticated open‑source real‑time global intelligence dashboard with 435+ curated news feeds, dual‑map visualization, AI‑powered analysis, and financial monitoring. Created by Elie Habib (koala73), it's designed for situational awareness across geopolitics, finance, tech, and infrastructure.

## 🏗️ Architecture Overview

### Tech Stack
- **Frontend:** Vanilla TypeScript, Vite, globe.gl + Three.js (3D), deck.gl + MapLibre GL (2D)
- **Desktop:** Tauri 2 (Rust) with Node.js sidecar
- **AI/ML:** Ollama/Groq/OpenRouter, Transformers.js (browser‑side)
- **APIs:** Protocol Buffers (92 protos, 22 services), Vercel Edge Functions
- **Caching:** Redis (Upstash), 3‑tier cache system
- **Deployment:** Vercel, Railway relay, Docker, Tauri desktop apps

### Key Components
1. **Dual Map Engine** – 3D globe + WebGL flat map with 45 data layers
2. **Panel System** – 86 resizable panels for different intelligence domains
3. **AI Workers** – ONNX inference for embeddings, sentiment, summarization
4. **Seed Pipeline** – Continuous data ingestion from 65+ external sources
5. **Variant System** – 5 site variants from single codebase (world, tech, finance, commodity, happy)

## 📰 Data Sources Analysis

### 1. RSS Feeds (435+ across 15 categories)
**Finance Focus:**
- CNBC, Yahoo Finance, Reuters Business, MarketWatch, Financial Times
- Federal Reserve, SEC, Treasury press releases
- 92 stock exchanges, commodities, crypto tracking

**Tech Focus:**
- TechCrunch, Hacker News, The Verge, Ars Technica
- AI news (OpenAI, Anthropic, Google AI, arXiv)
- Startup/VC blogs (Y Combinator, a16z, Sequoia)

**Geopolitics:**
- BBC World, Reuters World, Al Jazeera, Guardian
- Government sources (White House, State Dept, Pentagon, UN)
- Regional feeds (Asia, Europe, Middle East, Africa, Latin America)

**Singapore/Asia Focus:**
- CNA (Channel News Asia)
- Straits Times
- Nikkei Asia
- The Diplomat
- South China Morning Post

### 2. Telegram Channels (Curated list)
- VahidOnline (Iran geopolitics)
- AuroraIntel (conflict monitoring)
- BNO News (breaking news)
- ClashReport (conflict reporting)
- 50+ specialized intelligence channels

### 3. APIs & External Sources
- **Financial:** Finnhub, Yahoo Finance, FRED
- **Geospatial:** ACLED, UCDP, FIRMS
- **Aviation:** OpenSky, Wingbits (ADS‑B)
- **Maritime:** AIS vessel tracking
- **Climate:** NASA FIRMS, weather APIs

## 🤖 AI Integration

### Local AI Support (Ollama)
- Runs entirely offline with local models
- No API keys required for basic operation
- Browser‑side inference via Transformers.js

### AI Capabilities
1. **News Summarization** – Article → concise briefs
2. **Threat Classification** – Critical/High/Medium/Low/Info levels
3. **Semantic Search** – Vector embeddings for relevance
4. **Cross‑stream Correlation** – Identifies signal convergence
5. **Sentiment Analysis** – Market/news sentiment scoring

### ML Pipeline
- **Embeddings:** MiniLM‑L6 (384‑dim)
- **Vector Store:** IndexedDB‑backed in browser
- **Clustering:** Jaccard similarity for news grouping
- **NER:** Entity extraction for geopolitical analysis

## 🎯 Singapore/Asia Relevance

### Regional Data Sources
1. **CNA** – Singapore‑centric news with ASEAN coverage
2. **Straits Times** – Singapore business/politics
3. **Nikkei Asia** – Japanese perspective on Asian markets
4. **The Diplomat** – Geopolitical analysis focused on Asia‑Pacific
5. **South China Morning Post** – China/Hong Kong focus

### Asia‑Specific Categories
- **Asia region feeds** in news aggregation
- **Singapore stocks** monitoring capability
- **ASEAN geopolitical** tracking
- **China slowdown** risk signals
- **Asian currencies** (SGD, JPY, CNY, MYR pairs)

## 🔗 Integration Potential with OpenClaw/RAG

### 1. Enhanced News Aggregation
**Current:** 12 basic RSS feeds in `worldmonitor_news.py`
**Enhanced:** Leverage WorldMonitor's 435+ curated feeds with threat classification

### 2. Financial Monitoring Upgrade
**Current:** Basic stock/forex monitoring
**Enhanced:** Integrate WorldMonitor's 92‑exchange tracking, commodity flows, crypto markets

### 3. Geopolitical Risk Assessment
**Current:** Generic risk categories
**Enhanced:** Use WorldMonitor's Country Intelligence Index (12‑signal risk scoring)

### 4. AI‑Powered Summarization
**Current:** Raw RSS headlines
**Enhanced:** WorldMonitor's AI synthesis into intelligence briefs

### 5. Local AI Integration
**Current:** Cloud‑based embeddings (sentence‑transformers)
**Enhanced:** Ollama local models for complete privacy

## 🚀 Implementation Roadmap

### Phase 1: Feed Expansion (Immediate)
```python
# Upgrade worldmonitor_news.py with WorldMonitor's feed categories
FEED_CATEGORIES = {
    'finance': WorldMonitor's 25+ finance feeds,
    'tech': 20+ tech/AI feeds, 
    'geopolitics': 50+ geopolitical sources,
    'asia': Singapore/Asia‑focused feeds
}
```

### Phase 2: Threat Classification (Week 1)
- Implement WorldMonitor's threat level scoring (Critical/High/Medium/Low/Info)
- Add importance scoring based on source tier, corroboration, recency
- Integrate with existing risk assessment in market reports

### Phase 3: AI Summarization (Week 2)
- Local Ollama integration for article summarization
- Browser‑side Transformers.js for embeddings
- Semantic clustering of related news

### Phase 4: Financial Integration (Week 3)
- 92‑exchange market data integration
- Commodity/crypto tracking
- Sector‑based analysis

### Phase 5: Geopolitical Dashboard (Week 4)
- Country Intelligence Index integration
- Map‑based visualization of risks
- Cross‑stream correlation alerts

## 📋 Technical Requirements

### Dependencies to Add
```bash
# For enhanced WorldMonitor integration
pip install transformers torch  # Local AI
pip install redis              # Caching layer
pip install aiohttp           # Async feed fetching
```

### Architecture Changes
1. **Multi‑tier caching** (Redis + memory + local)
2. **Async pipeline** for 400+ feed processing
3. **Vector database** for semantic search
4. **Threat classification** pipeline
5. **Map integration** for geospatial visualization

## 💡 Actionable Insights

### For Scheduled News Updates (6‑hour)
1. **Categorize by threat level** – Prioritize Critical/High items
2. **Include source tiers** – Highlight Tier 1 sources (BBC, Reuters)
3. **Add corroboration count** – How many sources report same event
4. **Geographic filtering** – Focus on Asia‑Pacific region
5. **AI summaries** – 2‑sentence briefs instead of raw headlines

### For Market Reports (8 AM)
1. **Integrate financial feeds** – 92‑exchange data
2. **Add commodity tracking** – Oil, gold, agricultural
3. **Geopolitical context** – How events affect markets
4. **Country risk scores** – Intelligence Index integration
5. **Sector‑specific news** – Tech, finance, energy sectors

### For RAG Knowledge Base
1. **Ingest summarized news** as topic files
2. **Add threat classifications** as metadata
3. **Include geographic tags** for location‑based queries
4. **Source credibility scoring** in retrieval
5. **Temporal relevance** weighting

## 🏆 Key Strengths for Your Use Case

1. **Singapore/Asia Focus** – Relevant regional coverage
2. **Financial Depth** – 92 exchanges + commodities
3. **Local AI** – Privacy‑preserving, no API costs
4. **Threat Intelligence** – Professional‑grade classification
5. **Open Source** – Full control, customizable

## ⚠️ Considerations

1. **Scale** – 400+ feeds require robust async processing
2. **Rate Limiting** – Respect source terms of service
3. **Data Volume** – Storage for historical analysis
4. **Compute Requirements** – Local AI needs GPU/RAM
5. **Maintenance** – Feed URLs change, need monitoring

## 🎯 Recommended Starting Point

**Immediate action:** Enhance `worldmonitor_news.py` with:
1. WorldMonitor's curated finance/tech/geopolitics feeds
2. Basic threat classification (keyword‑based)
3. Source tier highlighting
4. Asia‑region filtering

**This gives you 80% of WorldMonitor's value with 20% of the complexity.**

## 📈 Expected Outcomes

1. **Higher‑quality news** – Curated, classified, summarized
2. **Better risk assessment** – Threat‑level‑aware analysis
3. **Regional relevance** – Singapore/Asia focus
4. **Financial depth** – Comprehensive market coverage
5. **AI enhancement** – Local summarization and analysis

---

**Next Steps:**
1. Review feed selection for Singapore/Asia focus
2. Test threat classification with sample articles
3. Schedule enhanced news updates starting tomorrow
4. Plan Phase 2 (AI summarization) implementation