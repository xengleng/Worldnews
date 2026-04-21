# Session: 2026-04-12 - Air Freight Capacity Learning

## Event Detected
**Cathay Pacific to cut flights from mid-May to end-June as jet fuel prices surge**
- Source: CNA (Channel News Asia)
- Threat Score: 0.8 (TIER 1)
- URL: https://www.channelnewsasia.com/business/cathay-pacific-cut-flights-mid-may-end-june-jet-fuel-prices-surge-6050626

## Supply Chain Logic Learned

### Flight Cuts → Air Freight Capacity Reduction
```
Airlines_Flight_Cuts
  └── triggers → Air_Freight_Capacity_Reduction
      └── Impact Chain:
          • Belly cargo capacity ↓ (passenger flights carry freight)
          • Air freight rates ↑
          • Same demand, reduced supply
          • Modal shift to sea freight
```

### Key Relationships Added to ASCR edges.ndjson:

**Triggers:**
- Airlines_Flight_Cuts → Air_Freight_Capacity_Reduction (tier 1)
- Jet_Fuel_Price_Surge → Airlines_Flight_Cuts (tier 1)

**Affected Entities (Tier 1-2):**
- FedEx, UPS (air freight carriers)
- XPOP (air freight ETF)
- Ecommerce_Logistics_Costs (AMZN, Shopify)
- Pharma_Cold_Chain (temperature-sensitive)
- Electronics_Time_Sensitive (AAPL components)

**Beneficiaries (Tier 2-3):**
- Sea_Freight_Demand_Shift
- MAERSK, Hapag_Lloyd (ocean carriers)
- DAL (Delta cargo)

## Scout Agent Updated
- Added keywords: "flight", "flights", "air freight", "jet fuel", "airline", "capacity", "cargo", "route reduction"
- Flight-related articles now detected as supply chain signals

## Historical Precedent
- 2021-2022: Fuel price surge → capacity cuts → air freight rates +30-50%
- Similar pattern expected for this event

## Action Items
1. ✅ Added edges for flight cuts scenario
2. ✅ Updated Scout keywords
3. ✅ Documented for future reference
4. ⏳ Monitor air freight rate indices (XBF, XPOP)
5. ⏳ Watch for FedEx/UPS pricing announcements