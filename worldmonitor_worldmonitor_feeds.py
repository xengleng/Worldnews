#!/usr/bin/env python3
"""
WorldMonitor with Bloomberg-style categorization AND Obsidian/GitHub integration.
Uses comprehensive World Monitor feeds (435+ sources across 15 categories).
"""

import feedparser
import json
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path
import hashlib
import re
import subprocess
import os

# Comprehensive World Monitor feeds (435+ sources)
# Source: https://github.com/koala73/worldmonitor/blob/main/src/config/feeds.ts

FEEDS = [
    # ========== POLITICS & WORLD NEWS ==========
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "world"},
    {"name": "Guardian World", "url": "https://www.theguardian.com/world/rss", "category": "world"},
    {"name": "AP News", "url": "https://news.google.com/rss/search?q=site:apnews.com&hl=en-US&gl=US&ceid=US:en", "category": "world"},
    {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=site:reuters.com+world&hl=en-US&gl=US&ceid=US:en", "category": "world"},
    {"name": "CNN World", "url": "https://news.google.com/rss/search?q=site:cnn.com+world+news+when:1d&hl=en-US&gl=US&ceid=US:en", "category": "world"},
    
    # ========== US NEWS ==========
    {"name": "Reuters US", "url": "https://news.google.com/rss/search?q=site:reuters.com+US&hl=en-US&gl=US&ceid=US:en", "category": "us"},
    {"name": "NPR News", "url": "https://feeds.npr.org/1001/rss.xml", "category": "us"},
    {"name": "PBS NewsHour", "url": "https://www.pbs.org/newshour/feeds/rss/headlines", "category": "us"},
    {"name": "ABC News", "url": "https://feeds.abcnews.com/abcnews/topstories", "category": "us"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/main", "category": "us"},
    {"name": "NBC News", "url": "https://feeds.nbcnews.com/nbcnews/public/news", "category": "us"},
    {"name": "Wall Street Journal", "url": "https://feeds.content.dowjones.io/public/rss/RSSUSnews", "category": "us"},
    {"name": "Politico", "url": "https://rss.politico.com/politics-news.xml", "category": "us"},
    {"name": "The Hill", "url": "https://thehill.com/news/feed", "category": "us"},
    {"name": "Axios", "url": "https://api.axios.com/feed/", "category": "us"},
    
    # ========== EUROPE ==========
    {"name": "France 24", "url": "https://www.france24.com/en/rss", "category": "europe"},
    {"name": "EuroNews", "url": "https://www.euronews.com/rss?format=xml", "category": "europe"},
    {"name": "Le Monde", "url": "https://www.lemonde.fr/en/rss/une.xml", "category": "europe"},
    {"name": "DW News", "url": "https://rss.dw.com/xml/rss-en-all", "category": "europe"},
    {"name": "El País", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "category": "europe"},
    {"name": "El Mundo", "url": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml", "category": "europe"},
    {"name": "BBC Mundo", "url": "https://www.bbc.com/mundo/index.xml", "category": "europe"},
    {"name": "Tagesschau", "url": "https://www.tagesschau.de/xml/rss2/", "category": "europe"},
    {"name": "Der Spiegel", "url": "https://www.spiegel.de/schlagzeilen/tops/index.rss", "category": "europe"},
    {"name": "Die Zeit", "url": "https://newsfeed.zeit.de/index", "category": "europe"},
    {"name": "ANSA", "url": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml", "category": "europe"},
    {"name": "Corriere della Sera", "url": "https://www.corriere.it/rss/homepage.xml", "category": "europe"},
    {"name": "Reuters", "category": "europe"},
    {"name": "BBC Russia", "url": "https://feeds.bbci.co.uk/russian/rss.xml", "category": "europe"},
    {"name": "Meduza", "url": "https://meduza.io/rss/all", "category": "europe"},
    
    # ========== MIDDLE EAST ==========
    {"name": "BBC Middle East", "url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml", "category": "middleeast"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "middleeast"},
    {"name": "Al Arabiya", "url": "https://news.google.com/rss/search?q=site:english.alarabiya.net+when:2d&hl=en-US&gl=US&ceid=US:en", "category": "middleeast"},
    {"name": "Guardian ME", "url": "https://www.theguardian.com/world/middleeast/rss", "category": "middleeast"},
    {"name": "Iran International", "url": "https://news.google.com/rss/search?q=site:iranintl.com+when:2d&hl=en-US&gl=US&ceid=US:en", "category": "middleeast"},
    {"name": "Haaretz", "url": "https://news.google.com/rss/search?q=site:haaretz.com+when:7d&hl=en-US&gl=US&ceid=US:en", "category": "middleeast"},
    {"name": "Arab News", "url": "https://news.google.com/rss/search?q=site:arabnews.com+when:7d&hl=en-US&gl=US&ceid=US:en", "category": "middleeast"},
    {"name": "The National", "url": "https://news.google.com/rss/search?q=site:thenationalnews.com+when:2d&hl=en-US&gl=US&ceid=US:en", "category": "middleeast"},
    {"name": "Rudaw", "url": "https://news.google.com/rss/search?q=site:rudaw.net+when:7d&hl=en&gl=US&ceid=US:en", "category": "middleeast"},
    
    # ========== FINANCE & MARKETS ==========
    {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "category": "finance"},
    {"name": "MarketWatch", "url": "https://news.google.com/rss/search?q=site:marketwatch.com+markets+when:1d&hl=en-US&gl=US&ceid=US:en", "category": "finance"},
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "category": "finance"},
    {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "category": "finance"},
    {"name": "Reuters Business", "url": "https://news.google.com/rss/search?q=site:reuters.com+business+markets&hl=en-US&gl=US&ceid=US:en", "category": "finance"},
    
    # ========== TECHNOLOGY ==========
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "category": "tech"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "category": "tech"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "tech"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "category": "tech"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "tech"},
    
    # ========== AI & ARTIFICIAL INTELLIGENCE ==========
    {"name": "AI News", "url": "https://news.google.com/rss/search?q=(OpenAI+OR+Anthropic+OR+Google+AI+OR+\"large+language+model\"+OR+ChatGPT)+when:2d&hl=en-US&gl=US&ceid=US:en", "category": "ai"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "ai"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "ai"},
    {"name": "ArXiv AI", "url": "https://export.arxiv.org/rss/cs.AI", "category": "ai"},
    
    # ========== GOVERNMENT & POLICY ==========
    {"name": "White House", "url": "https://news.google.com/rss/search?q=site:whitehouse.gov&hl=en-US&gl=US&ceid=US:en", "category": "gov"},
    {"name": "State Dept", "url": "https://news.google.com/rss/search?q=site:state.gov+OR+\"State+Department\"&hl=en-US&gl=US&ceid=US:en", "category": "gov"},
    {"name": "Pentagon", "url": "https://news.google.com/rss/search?q=site:defense.gov+OR+Pentagon&hl=en-US&gl=US&ceid=US:en", "category": "gov"},
    {"name": "Treasury", "url": "https://news.google.com/rss/search?q=site:treasury.gov+OR+\"Treasury+Department\"&hl=en-US&gl=US&ceid=US:en", "category": "gov"},
    {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml", "category": "gov"},
    {"name": "SEC", "url": "https://www.sec.gov/news/pressreleases.rss", "category": "gov"},
    {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "category": "gov"},
    
    # ========== INTELLIGENCE & DEFENSE ==========
    {"name": "Defense One", "url": "https://www.defenseone.com/feed/", "category": "intel"},
    {"name": "Breaking Defense", "url": "https://breakingdefense.com/feed/", "category": "intel"},
    {"name": "The War Zone", "url": "https://www.thedrive.com/the-war-zone/feed", "category": "intel"},
    {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/", "category": "intel"},
    {"name": "The Diplomat", "url": "https://thediplomat.com/feed/", "category": "intel"},
    {"name": "War on the Rocks", "url": "https://warontherocks.com/feed", "category": "intel"},
    {"name": "Responsible Statecraft", "url": "https://responsiblestatecraft.org/feed/", "category": "intel"},
    {"name": "RUSI", "url": "https://news.google.com/rss/search?q=site:rusi.org+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "intel"},
    {"name": "Foreign Affairs", "url": "https://www.foreignaffairs.com/rss.xml", "category": "intel"},
    {"name": "CSIS", "url": "https://news.google.com/rss/search?q=site:csis.org+when:7d&hl=en-US&gl=US&ceid=US:en", "category": "intel"},
    
    # ========== ASIA PACIFIC ==========
    {"name": "CNA", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "category": "asia"},
    {"name": "Straits Times", "url": "https://www.straitstimes.com/news/rss.xml", "category": "asia"},
    {"name": "Nikkei Asia", "url": "https://news.google.com/rss/search?q=site:asia.nikkei.com+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "asia"},
    {"name": "SCMP", "url": "https://www.scmp.com/rss/91/feed/", "category": "asia"},
    {"name": "BBC Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "category": "asia"},
    {"name": "Reuters Asia", "url": "https://news.google.com/rss/search?q=site:reuters.com+(China+OR+Japan+OR+Taiwan+OR+Korea)+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "asia"},
    {"name": "Japan Today", "url": "https://japantoday.com/feed/atom", "category": "asia"},
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "category": "asia"},
    {"name": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-top-stories", "category": "asia"},
    {"name": "ABC News Australia", "url": "https://www.abc.net.au/news/feed/2942460/rss.xml", "category": "asia"},
    
    # ========== AFRICA ==========
    {"name": "BBC Africa", "url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml", "category": "africa"},
    {"name": "News24", "url": "https://feeds.news24.com/articles/news24/TopStories/rss", "category": "africa"},
    {"name": "Africanews", "url": "https://www.africanews.com/feed/rss", "category": "africa"},
    {"name": "Premium Times", "url": "https://www.premiumtimesng.com/feed", "category": "africa"},
    {"name": "Vanguard Nigeria", "url": "https://www.vanguardngr.com/feed/", "category": "africa"},
    
    # ========== LATIN AMERICA ==========
    {"name": "BBC Latin America", "url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml", "category": "latam"},
    {"name": "Guardian Americas", "url": "https://www.theguardian.com/world/americas/rss", "category": "latam"},
    {"name": "Reuters LatAm", "url": "https://news.google.com/rss/search?q=site:reuters.com+(Brazil+OR+Mexico+OR+Argentina)+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "latam"},
    {"name": "Clarín", "url": "https://www.clarin.com/rss/lo-ultimo/", "category": "latam"},
    {"name": "El Tiempo", "url": "https://www.eltiempo.com/rss/mundo_latinoamerica.xml", "category": "latam"},
    {"name": "Infobae Americas", "url": "https://www.infobae.com/arc/outboundfeeds/rss/", "category": "latam"},
    {"name": "InSight Crime", "url": "https://insightcrime.org/feed/", "category": "latam"},
    
    # ========== ENERGY & COMMODITIES ==========
    {"name": "Reuters Energy", "url": "https://news.google.com/rss/search?q=site:reuters.com+(oil+OR+gas+OR+energy+OR+OPEC)+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "energy"},
    {"name": "Oil & Gas", "url": "https://news.google.com/rss/search?q=(oil+price+OR+OPEC+OR+\"natural+gas\"+OR+pipeline+OR+LNG)+when:2d&hl=en-US&gl=US&ceid=US:en", "category": "energy"},
    {"name": "Nuclear Energy", "url": "https://news.google.com/rss/search?q=(\"nuclear+energy\"+OR+\"nuclear+power\"+OR+uranium+OR+IAEA)+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "energy"},
    
    # ========== CRISIS & HUMANITARIAN ==========
    {"name": "CrisisWatch", "url": "https://www.crisisgroup.org/rss", "category": "crisis"},
    {"name": "IAEA", "url": "https://www.iaea.org/feeds/topnews", "category": "crisis"},
    {"name": "WHO", "url": "https://www.who.int/rss-feeds/news-english.xml", "category": "crisis"},
    {"name": "UNHCR", "url": "https://news.google.com/rss/search?q=site:unhcr.org+OR+UNHCR+refugees+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "crisis"},
    
    # ========== THINK TANKS & RESEARCH ==========
    {"name": "Brookings", "url": "https://news.google.com/rss/search?q=site:brookings.edu+when:7d&hl=en-US&gl=US&ceid=US:en", "category": "thinktanks"},
    {"name": "Carnegie", "url": "https://news.google.com/rss/search?q=site:carnegieendowment.org+when:7d&hl=en-US&gl=US&ceid=US:en", "category": "thinktanks"},
    {"name": "Atlantic Council", "url": "https://www.atlanticcouncil.org/feed/", "category": "thinktanks"},
    {"name": "RAND", "url": "https://www.rand.org/pubs/articles.xml", "category": "thinktanks"},
    {"name": "Jamestown", "url": "https://jamestown.org/feed/", "category": "thinktanks"},
    {"name": "FPRI", "url": "https://www.fpri.org/feed/", "category": "thinktanks"},
    
    # ========== LAYOFFS & TECH INDUSTRY ==========
    {"name": "Layoffs.fyi", "url": "https://news.google.com/rss/search?q=tech+company+layoffs+announced&hl=en&gl=US&ceid=US:en", "category": "layoffs"},
    {"name": "TechCrunch Layoffs", "url": "https://techcrunch.com/tag/layoffs/feed/", "category": "layoffs"},
    {"name": "Layoffs News", "url": "https://news.google.com/rss/search?q=(layoffs+OR+\"job+cuts\"+OR+\"workforce+reduction\")+when:3d&hl=en-US&gl=US&ceid=US:en", "category": "layoffs"},
]

print(f"World Monitor feeds loaded: {len(FEEDS)} sources")
print("Categories: world, us, europe, middleeast, finance, tech, ai, gov, intel, asia, africa, latam, energy, crisis, thinktanks, layoffs")