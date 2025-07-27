#!/usr/bin/env python3
"""
Autonomous Web Research Tool for Financial Analysis
Cost-effective alternative to expensive APIs
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from crewai.tools import tool
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import feedparser
import hashlib
from threading import Lock
import sqlite3
import dotenv
dotenv.load_dotenv()
def get_default_watchlist():
    """Get the default watchlist from environment variable"""
    watchlist = os.getenv("DEFAULT_WATCHLIST", "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI")
    if not watchlist:
        watchlist = "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI"
    return [s.strip() for s in watchlist.split(",") if s.strip()]

class AutonomousWebResearcher:
    """
    Cost-effective web research system that doesn't rely on expensive APIs
   
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Initialize local cache database
        self.cache_db = "web_research_cache.db"
        self.init_cache_db()
        
        # Free financial data sources
        self.free_sources = {
            'google_finance': 'https://www.google.com/finance',
            'google_news': 'https://news.google.com',
            'google_search': 'https://www.google.com/search',
            'google_trends': 'https://trends.google.com',
            'marketwatch': 'https://www.marketwatch.com',
            'finviz': 'https://finviz.com',
            'seeking_alpha': 'https://seekingalpha.com',
            'reddit_wallstreetbets': 'https://www.reddit.com/r/wallstreetbets',
            'reddit_stocks': 'https://www.reddit.com/r/stocks',
        }
        
        # RSS feeds for financial news (free!)
        self.rss_feeds = [
            
            'https://www.marketwatch.com/rss/topstories',
            'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        ]
        
        self.cache_lock = Lock()
    
    def init_cache_db(self):
        """Initialize SQLite database for caching"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS web_cache (
                    url_hash TEXT PRIMARY KEY,
                    url TEXT,
                    content TEXT,
                    timestamp REAL,
                    expires REAL
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache DB init error: {e}")
    
    def get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_cached_content(self, url: str, max_age_hours: int = 1) -> Optional[str]:
        """Get cached content if still valid"""
        try:
            with self.cache_lock:
                conn = sqlite3.connect(self.cache_db)
                cursor = conn.cursor()
                url_hash = self.get_cache_key(url)
                
                cursor.execute(
                    'SELECT content, timestamp FROM web_cache WHERE url_hash = ?',
                    (url_hash,)
                )
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    content, timestamp = result
                    if time.time() - timestamp < max_age_hours * 3600:
                        return content
                        
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        
        return None
    
    def cache_content(self, url: str, content: str, max_age_hours: int = 1):
        """Cache content with expiration"""
        try:
            with self.cache_lock:
                conn = sqlite3.connect(self.cache_db)
                cursor = conn.cursor()
                url_hash = self.get_cache_key(url)
                timestamp = time.time()
                expires = timestamp + (max_age_hours * 3600)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO web_cache 
                    (url_hash, url, content, timestamp, expires) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (url_hash, url, content, timestamp, expires))
                
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Cache storage error: {e}")
    
    def fetch_web_content(self, url: str, use_cache: bool = True) -> Optional[str]:
        """Fetch web content with caching and improved error handling"""
        if use_cache:
            cached = self.get_cached_content(url)
            if cached:
                return cached
        
        try:
            # Add randomized delay to avoid rate limiting
            import time
            import random
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(url, timeout=15)
            
            # Handle different status codes
            if response.status_code == 401:
                print(f"⚠️ Access denied for {url} - site may be blocking requests")
                return None
            elif response.status_code == 403:
                print(f"⚠️ Forbidden access to {url} - trying alternative approach")
                return None
            elif response.status_code == 429:
                print(f"⚠️ Rate limited for {url} - waiting and retrying")
                time.sleep(3)
                response = self.session.get(url, timeout=15)
            
            response.raise_for_status()
            content = response.text
            
            if use_cache:
                self.cache_content(url, content)
            
            return content
            
        except requests.exceptions.HTTPError as e:
            if "401" in str(e) or "403" in str(e):
                print(f"🚫 Site blocking requests for {url} - skipping to next source")
            else:
                print(f"⚠️ HTTP error for {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error for {url}: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Unexpected error for {url}: {e}")
            return None
    
    def extract_stock_sentiment_from_text(self, text: str, symbol: str) -> Dict[str, Any]:
        """Extract sentiment about a stock from text content"""
        text_lower = text.lower()
        symbol_lower = symbol.lower()
        
        # Look for mentions of the stock
        mentions = len(re.findall(rf'\b{symbol_lower}\b|\${symbol_lower}\b', text_lower))
        
        if mentions == 0:
            return {'sentiment': 0.0, 'confidence': 0.0, 'mentions': 0}
        
        # Positive sentiment keywords
        positive_words = [
            'bullish', 'buy', 'long', 'calls', 'moon', 'rocket', 'pump', 'gains', 
            'squeeze', 'up', 'rise', 'surge', 'rally', 'breakout', 'strong', 
            'bullish', 'positive', 'good', 'great', 'excellent', 'growth'
        ]
        
        # Negative sentiment keywords
        negative_words = [
            'bearish', 'sell', 'short', 'puts', 'dump', 'crash', 'drop', 
            'decline', 'fall', 'down', 'weak', 'bad', 'terrible', 'loss', 
            'losses', 'bearish', 'negative', 'poor', 'disappointing'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment = 0.0
            confidence = 0.0
        else:
            sentiment = (positive_count - negative_count) / total_sentiment_words
            confidence = min(1.0, total_sentiment_words / 10.0)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'mentions': mentions,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def research_stock_yahoo(self, symbol: str) -> Dict[str, Any]:
        """Research stock using free Google sources (Google Finance, Google Search, Google News)"""
        try:
            # Try Google Finance first (completely free!)
            try:
                google_url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
                content = self.fetch_web_content(google_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    data = {'source': 'google_finance', 'symbol': symbol}
                    
                    # Extract price from Google Finance
                    price_elements = soup.find_all(['div', 'span'], class_=re.compile('YMlKec|P6K39c|fxKbKc'))
                    for elem in price_elements:
                        price_text = elem.get_text().strip()
                        if price_text and '$' in price_text:
                            data['price_info'] = price_text
                            break
                    
                    # Extract change info
                    change_elements = soup.find_all(['div', 'span'], class_=re.compile('JwB6zf|NydbP'))
                    for elem in change_elements:
                        change_text = elem.get_text().strip()
                        if change_text and ('$' in change_text or '%' in change_text):
                            data['change_info'] = change_text
                            break
                    
                    # Extract more detailed info from Google Finance
                    info_elements = soup.find_all(['div', 'span', 'td'])
                    for elem in info_elements:
                        text = elem.get_text().strip()
                        if 'Market cap' in text or 'Mkt cap' in text:
                            data['market_cap'] = text
                        elif 'P/E ratio' in text or 'PE ratio' in text:
                            data['pe_ratio'] = text
                        elif 'Volume' in text and any(char.isdigit() for char in text):
                            data['volume'] = text
                        elif '52 week' in text.lower():
                            data['52_week_range'] = text
                    
                    # Get additional data from Google Search
                    try:
                        search_data = self._google_search_stock_info(symbol)
                        if search_data:
                            data.update(search_data)
                    except Exception as e:
                        print(f"Google Search error: {e}")
                    
                    if 'price_info' in data:
                        print(f"✅ Retrieved data from Google Finance for {symbol}")
                        return data
            except Exception as e:
                print(f"Google Finance error: {e}")
            
            # Fallback to Google Search for stock information
            try:
                search_result = self._google_search_stock_info(symbol)
                if search_result:
                    search_result['source'] = 'google_search'
                    print(f"✅ Retrieved data from Google Search for {symbol}")
                    return search_result
            except Exception as e:
                print(f"Google Search error: {e}")
            
            # Fallback to MarketWatch (free web scraping)
            try:
                mw_url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
                content = self.fetch_web_content(mw_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    data = {'source': 'marketwatch', 'symbol': symbol}
                    
                    # Extract price from MarketWatch
                    price_elements = soup.find_all(['span', 'div'], class_=re.compile('value|price'))
                    for elem in price_elements:
                        price_text = elem.get_text().strip()
                        if price_text and '$' in price_text:
                            data['price_info'] = price_text
                            break
                    
                    # Extract headlines from MarketWatch
                    headlines = []
                    news_elements = soup.find_all(['h3', 'h4', 'a'], class_=re.compile('headline|title'))
                    for elem in news_elements[:5]:
                        text = elem.get_text().strip()
                        if text and len(text) > 15 and symbol.upper() in text.upper():
                            headlines.append(text)
                    
                    data['headlines'] = headlines
                    
                    if 'price_info' in data:
                        print(f"✅ Retrieved data from MarketWatch for {symbol}")
                        return data
            except Exception as e:
                print(f"MarketWatch error: {e}")
            
            # Fallback to Finviz (free financial data)
            try:
                finviz_url = f"https://finviz.com/quote.ashx?t={symbol.upper()}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                import requests
                response = requests.get(finviz_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    data = {'source': 'finviz', 'symbol': symbol}
                    
                    # Extract data from Finviz table
                    table_rows = soup.find_all('tr')
                    for row in table_rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            label = cells[0].get_text().strip()
                            value = cells[1].get_text().strip()
                            
                            if 'Price' in label:
                                data['price_info'] = f"${value}"
                            elif 'Change' in label:
                                data['change_info'] = value
                            elif 'Volume' in label:
                                data['volume'] = value
                            elif 'Market Cap' in label:
                                data['market_cap'] = value
                    
                    # Get news from Finviz
                    news_table = soup.find('table', {'id': 'news-table'})
                    headlines = []
                    if news_table:
                        news_rows = news_table.find_all('tr')
                        for row in news_rows[:5]:
                            title_link = row.find('a')
                            if title_link:
                                headlines.append(title_link.get_text().strip())
                    
                    data['headlines'] = headlines
                    
                    if 'price_info' in data:
                        print(f"✅ Retrieved data from Finviz for {symbol}")
                        return data
            except Exception as e:
                print(f"Finviz error: {e}")
            
            # Final fallback - try basic stock info from free sources
            try:
                # Try investing.com
                investing_url = f"https://www.investing.com/search/?q={symbol}"
                content = self.fetch_web_content(investing_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for basic price info
                    price_elements = soup.find_all(['span', 'div'])
                    for elem in price_elements:
                        text = elem.get_text().strip()
                        if text and '$' in text and len(text) < 20:
                            return {
                                'source': 'investing_com',
                                'symbol': symbol,
                                'price_info': text,
                                'note': 'Basic price from free web source'
                            }
            except Exception as e:
                print(f"Investing.com error: {e}")
            
            # Return fallback message
            return {
                'source': 'fallback',
                'symbol': symbol,
                'error': 'Unable to fetch from free web sources',
                'suggestion': 'Try again later - free web sources may be temporarily unavailable',
                'attempted_sources': ['Google Finance', 'Google Search', 'MarketWatch', 'Finviz', 'Investing.com']
            }
            
        except Exception as e:
            return {'error': f'Free web research failed: {str(e)}'}
    
    def _google_search_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get additional stock information from Google Search"""
        try:
            import requests
            from urllib.parse import quote
            
            # Search for stock information on Google
            search_query = f"{symbol} stock price market cap pe ratio"
            google_search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=fin"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(google_search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                data = {'symbol': symbol}
                
                # Extract financial data from Google Search results (FIXED REGEX)
                # Look for price elements
                price_elements = soup.find_all(['div', 'span', 'td'], string=re.compile(r'\$[\d,.]+'))
                for elem in price_elements:
                    text = elem.get_text().strip()
                    if '$' in text and 'price' in text.lower():
                        data['google_price'] = text
                        break
                
                # Look for financial class elements
                financial_elements = soup.find_all(['div', 'span'], class_=re.compile('price|value|financial'))
                for elem in financial_elements:
                    text = elem.get_text().strip()
                    if 'volume' in text.lower() and any(char.isdigit() for char in text):
                        data['google_volume'] = text
                        break
                    elif 'cap' in text.lower() and '$' in text:
                        data['google_market_cap'] = text
                        break
                
                # Extract trending info (SIMPLIFIED)
                trending_elements = soup.find_all(['div', 'span'])
                for elem in trending_elements:
                    text = elem.get_text().strip()
                    if '%' in text and any(word in text.lower() for word in ['up', 'down', 'gain', 'loss']):
                        data['google_trend'] = text
                        break
                
                # Get news sentiment from Google Search (SIMPLIFIED)
                news_elements = soup.find_all(['h3', 'a'])
                sentiment_keywords = []
                for elem in news_elements[:5]:
                    text = elem.get_text().strip()
                    if symbol.upper() in text and text:
                        sentiment_keywords.append(text)
                
                if sentiment_keywords:
                    data['google_news_sentiment'] = self._analyze_google_sentiment(sentiment_keywords)
                
                return data if len(data) > 1 else None  # Return only if we found actual data
                
        except Exception as e:
            print(f"Google Search stock info error: {e}")
            return None
    
    def _analyze_google_sentiment(self, texts: List[str]) -> str:
        """Analyze sentiment from Google search results"""
        try:
            positive_words = ['bullish', 'buy', 'upgrade', 'rise', 'gain', 'strong', 'positive', 'rally', 'surge']
            negative_words = ['bearish', 'sell', 'downgrade', 'fall', 'loss', 'weak', 'negative', 'decline', 'plunge']
            
            positive_count = 0
            negative_count = 0
            
            for text in texts:
                text_lower = text.lower()
                positive_count += sum(1 for word in positive_words if word in text_lower)
                negative_count += sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
        except Exception:
            return 'neutral'
    
    def research_stock_reddit(self, symbol: str) -> Dict[str, Any]:
        """Research stock mentions on Reddit (free!)"""
        try:
            # Search multiple subreddits
            subreddits = ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis']
            all_data = []
            
            for subreddit in subreddits:
                # Reddit search URL
                search_url = f"https://www.reddit.com/r/{subreddit}/search.json?q={symbol}&limit=25&sort=hot"
                
                try:
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    reddit_data = response.json()
                    posts = reddit_data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        score = post_data.get('score', 0)
                        
                        # Combine title and text for sentiment analysis
                        full_text = f"{title} {selftext}"
                        sentiment = self.extract_stock_sentiment_from_text(full_text, symbol)
                        
                        if sentiment['mentions'] > 0:
                            all_data.append({
                                'subreddit': subreddit,
                                'title': title,
                                'score': score,
                                'sentiment': sentiment['sentiment'],
                                'confidence': sentiment['confidence'],
                                'mentions': sentiment['mentions']
                            })
                
                except Exception as e:
                    print(f"Reddit {subreddit} error: {e}")
                    continue
                
                # Be respectful to Reddit's servers
                time.sleep(1)
            
            if not all_data:
                return {'error': 'No Reddit data found'}
            
            # Aggregate sentiment
            sentiments = [post['sentiment'] for post in all_data if post['sentiment'] != 0]
            scores = [post['score'] for post in all_data]
            
            return {
                'source': 'reddit',
                'symbol': symbol,
                'posts_found': len(all_data),
                'average_sentiment': np.mean(sentiments) if sentiments else 0.0,
                'sentiment_count': len(sentiments),
                'average_score': np.mean(scores) if scores else 0.0,
                'top_posts': sorted(all_data, key=lambda x: x['score'], reverse=True)[:5]
            }
            
        except Exception as e:
            return {'error': f'Reddit research failed: {str(e)}'}
    
    def research_stock_news(self, symbol: str) -> Dict[str, Any]:
        """Research stock in financial news RSS feeds (free!)"""
        try:
            all_articles = []
            
            for feed_url in self.rss_feeds:
                try:
                    # Parse RSS feed
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:20]:  # Limit to recent articles
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')
                        link = entry.get('link', '')
                        published = entry.get('published', '')
                        
                        # Check if article mentions our stock
                        full_text = f"{title} {summary}"
                        sentiment = self.extract_stock_sentiment_from_text(full_text, symbol)
                        
                        if sentiment['mentions'] > 0:
                            all_articles.append({
                                'title': title,
                                'summary': summary,
                                'link': link,
                                'published': published,
                                'sentiment': sentiment['sentiment'],
                                'confidence': sentiment['confidence'],
                                'mentions': sentiment['mentions']
                            })
                
                except Exception as e:
                    print(f"RSS feed {feed_url} error: {e}")
                    continue
            
            if not all_articles:
                return {'error': 'No news articles found'}
            
            # Aggregate sentiment
            sentiments = [article['sentiment'] for article in all_articles if article['sentiment'] != 0]
            
            return {
                'source': 'news_rss',
                'symbol': symbol,
                'articles_found': len(all_articles),
                'average_sentiment': np.mean(sentiments) if sentiments else 0.0,
                'sentiment_count': len(sentiments),
                'latest_articles': sorted(all_articles, 
                    key=lambda x: x.get('published', ''), reverse=True)[:5]
            }
            
        except Exception as e:
            return {'error': f'News research failed: {str(e)}'}
    
    def comprehensive_stock_research(self, symbol: str) -> Dict[str, Any]:
        """Comprehensive free stock research from multiple sources"""
        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # Research from multiple free sources
        sources = [
            ('yahoo_finance', self.research_stock_yahoo),
            ('reddit', self.research_stock_reddit),
            ('news_rss', self.research_stock_news)
        ]
        
        for source_name, research_func in sources:
            try:
                print(f"🔍 Researching {symbol} from {source_name}...")
                source_data = research_func(symbol)
                results['sources'][source_name] = source_data
                
                # Be respectful to servers
                time.sleep(2)
                
            except Exception as e:
                results['sources'][source_name] = {'error': str(e)}
        
        # Aggregate sentiment across all sources
        all_sentiments = []
        
        for source_name, source_data in results['sources'].items():
            if 'error' not in source_data:
                if 'average_sentiment' in source_data:
                    all_sentiments.append(source_data['average_sentiment'])
                elif 'news_sentiment' in source_data:
                    all_sentiments.append(source_data['news_sentiment']['average'])
        
        if all_sentiments:
            results['overall_sentiment'] = {
                'average': np.mean(all_sentiments),
                'sources_count': len(all_sentiments),
                'sentiment_range': [min(all_sentiments), max(all_sentiments)]
            }
        
        return results

# Create global instance
web_researcher = AutonomousWebResearcher()

@tool("Autonomous Stock Research")
def autonomous_stock_research(symbol: str) -> str:
    """
    Autonomous web research for stock analysis using FREE sources.
    No expensive API costs - uses Yahoo Finance, Reddit, RSS feeds, etc.
    
    Parameters:
        symbol (str): Stock ticker symbol (e.g., AAPL, TSLA, NIO)
    
    Returns:
        str: Comprehensive research report from multiple free sources
    """
    try:
        print(f"🤖 Starting autonomous research for {symbol}...")
        
        # Comprehensive research from free sources
        research_data = web_researcher.comprehensive_stock_research(symbol)
        
        if not research_data or 'sources' not in research_data:
            return f"❌ No research data found for {symbol}"
        
        # Format comprehensive report
        report = []
        report.append(f"🤖 AUTONOMOUS STOCK RESEARCH FOR ${symbol}")
        report.append("=" * 60)
        report.append(f"🆓 FREE SOURCES - NO API COSTS")
        report.append(f"📅 Research Time: {research_data['timestamp'][:19]}")
        report.append("")
        
        # Overall sentiment summary
        if 'overall_sentiment' in research_data:
            sentiment = research_data['overall_sentiment']
            sentiment_emoji = "🟢" if sentiment['average'] > 0.2 else "🔴" if sentiment['average'] < -0.2 else "🟡"
            
            report.append(f"{sentiment_emoji} OVERALL SENTIMENT:")
            report.append(f"   • Average Sentiment: {sentiment['average']:+.3f}")
            report.append(f"   • Sources Used: {sentiment['sources_count']}")
            report.append(f"   • Range: {sentiment['sentiment_range'][0]:+.3f} to {sentiment['sentiment_range'][1]:+.3f}")
            report.append("")
        
        # Source-by-source breakdown
        for source_name, source_data in research_data['sources'].items():
            if 'error' in source_data:
                report.append(f"❌ {source_name.upper()}: {source_data['error']}")
                continue
            
            report.append(f"📊 {source_name.upper()} RESEARCH:")
            
            if source_name == 'yahoo_finance':
                if 'headlines' in source_data:
                    report.append(f"   • Headlines Found: {len(source_data['headlines'])}")
                    if 'news_sentiment' in source_data:
                        report.append(f"   • News Sentiment: {source_data['news_sentiment']['average']:+.3f}")
                    
                    report.append("   • Recent Headlines:")
                    for i, headline in enumerate(source_data['headlines'][:3], 1):
                        report.append(f"     {i}. {headline[:80]}...")
            
            elif source_name == 'reddit':
                if 'posts_found' in source_data:
                    report.append(f"   • Posts Found: {source_data['posts_found']}")
                    report.append(f"   • Average Sentiment: {source_data['average_sentiment']:+.3f}")
                    report.append(f"   • Average Score: {source_data['average_score']:.1f}")
                    
                    if 'top_posts' in source_data:
                        report.append("   • Top Posts:")
                        for i, post in enumerate(source_data['top_posts'][:3], 1):
                            report.append(f"     {i}. [{post['subreddit']}] {post['title'][:60]}... (Score: {post['score']})")
            
            elif source_name == 'news_rss':
                if 'articles_found' in source_data:
                    report.append(f"   • Articles Found: {source_data['articles_found']}")
                    report.append(f"   • News Sentiment: {source_data['average_sentiment']:+.3f}")
                    
                    if 'latest_articles' in source_data:
                        report.append("   • Latest Articles:")
                        for i, article in enumerate(source_data['latest_articles'][:3], 1):
                            report.append(f"     {i}. {article['title'][:60]}...")
            
            report.append("")
        
        # Trading implications
        report.append("💡 AUTONOMOUS ANALYSIS:")
        
        if 'overall_sentiment' in research_data:
            avg_sentiment = research_data['overall_sentiment']['average']
            if avg_sentiment > 0.3:
                report.append("   • Strong positive sentiment across multiple sources")
                report.append("   • Consider this bullish signal in your analysis")
            elif avg_sentiment < -0.3:
                report.append("   • Strong negative sentiment across multiple sources")
                report.append("   • Exercise caution and consider risk management")
            else:
                report.append("   • Mixed or neutral sentiment across sources")
                report.append("   • Rely on technical analysis and fundamentals")
        
        report.append("")
        report.append("🎯 COST SAVINGS:")
        report.append("   • $0 API costs - completely free research")
        report.append("   • Multiple source verification")
        report.append("   • Real-time web scraping and RSS feeds")
        report.append("   • Local caching for efficiency")
        
        return "\n".join(report)
        
    except Exception as e:
        return f"❌ Autonomous research failed for {symbol}: {str(e)}"

@tool("Web News Scanner")  
def scan_financial_news(keywords: str = "market news") -> str:
    """
    Scan financial news from free RSS feeds and web sources.
    
    Parameters:
        keywords (str): Keywords to search for (default: "market news")
    
    Returns:
        str: Latest financial news summary
    """
    try:
        news_data = []
        
        # Scan RSS feeds
        for feed_url in web_researcher.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    
                    # Check if keywords match
                    if any(keyword.lower() in f"{title} {summary}".lower() 
                           for keyword in keywords.split()):
                        news_data.append({
                            'title': title,
                            'summary': summary,
                            'link': link,
                            'published': published,
                            'source': urlparse(feed_url).netloc
                        })
                        
            except Exception as e:
                print(f"Feed scan error: {e}")
                continue
        
        if not news_data:
            return f"❌ No news found for keywords: {keywords}"
        
        # Format report
        report = []
        report.append(f"📰 FINANCIAL NEWS SCAN")
        report.append("=" * 40)
        report.append(f"🔍 Keywords: {keywords}")
        report.append(f"📅 Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📊 Articles Found: {len(news_data)}")
        report.append("")
        
        # Sort by publication date (most recent first)
        news_data.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        for i, article in enumerate(news_data[:10], 1):
            report.append(f"{i}. {article['title']}")
            report.append(f"   📰 Source: {article['source']}")
            if article['published']:
                report.append(f"   📅 Published: {article['published']}")
            if article['summary']:
                report.append(f"   📝 Summary: {article['summary'][:100]}...")
            report.append(f"   🔗 Link: {article['link']}")
            report.append("")
        
        report.append("🆓 FREE NEWS SCANNING - NO API COSTS")
        
        return "\n".join(report)
        
    except Exception as e:
        return f"❌ News scanning failed: {str(e)}"

@tool("Market Sentiment Tracker")
def track_market_sentiment() -> str:
    """
    Track overall market sentiment from free sources.
    
    Returns:
        str: Market sentiment summary
    """
    try:
        # Get symbols from user's DEFAULT_WATCHLIST
        symbols = get_default_watchlist()
        
        market_data = {}
        
        for symbol in symbols:
            print(f"📊 Tracking sentiment for {symbol}...")
            
            # Get research data
            research = web_researcher.comprehensive_stock_research(symbol)
            
            if 'overall_sentiment' in research:
                market_data[symbol] = research['overall_sentiment']['average']
            
            time.sleep(1)  # Be respectful
        
        if not market_data:
            return "❌ No market sentiment data available"
        
        # Calculate overall market sentiment
        overall_sentiment = np.mean(list(market_data.values()))
        sentiment_emoji = "🟢" if overall_sentiment > 0.1 else "🔴" if overall_sentiment < -0.1 else "🟡"
        
        # Format report
        report = []
        report.append(f"📈 MARKET SENTIMENT TRACKER")
        report.append("=" * 40)
        report.append(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append(f"{sentiment_emoji} OVERALL MARKET SENTIMENT: {overall_sentiment:+.3f}")
        report.append("")
        
        report.append("📊 INDEX SENTIMENT BREAKDOWN:")
        for symbol, sentiment in market_data.items():
            emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
            index_name = {
                'SPY': 'S&P 500',
                'QQQ': 'NASDAQ',
                'IWM': 'Russell 2000',
                'DIA': 'Dow Jones'
            }.get(symbol, symbol)
            
            report.append(f"   {emoji} {index_name} ({symbol}): {sentiment:+.3f}")
        
        report.append("")
        report.append("💡 MARKET ANALYSIS:")
        if overall_sentiment > 0.2:
            report.append("   • Strong bullish market sentiment")
            report.append("   • Favorable environment for long positions")
        elif overall_sentiment < -0.2:
            report.append("   • Strong bearish market sentiment") 
            report.append("   • Consider defensive strategies")
        else:
            report.append("   • Neutral market sentiment")
            report.append("   • Mixed signals - use selective strategies")
        
        report.append("")
        report.append("🆓 FREE MARKET TRACKING - NO SUBSCRIPTION FEES")
        
        return "\n".join(report)
        
    except Exception as e:
        return f"❌ Market sentiment tracking failed: {str(e)}" 