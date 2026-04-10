"""
Popcorn AI — Data Collectors v4
Pulls from: Google Trends, YouTube, Spotify, Wikipedia,
TMDB, NewsAPI, AO3, Open Library
+ NEW: Auto-discovery via OpenAI GPT-4o
"""

import os
import json
import time
import re
import base64
import requests
from datetime import datetime, timedelta

# ============================================================
# API KEYS
# ============================================================
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# ============================================================
# CACHE
# ============================================================
_cache = {}
CACHE_TTL = 86400


def get_cached(key):
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry['time'] < CACHE_TTL:
            return entry['data']
    return None


def set_cache(key, data):
    _cache[key] = {'data': data, 'time': time.time()}


# ============================================================
# OPENAI GPT-4o
# ============================================================
def ask_gpt(prompt, max_tokens=4000):
    if not OPENAI_API_KEY:
        return {'error': 'No OpenAI API key'}
    try:
        resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': 'Bearer ' + OPENAI_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens,
                'temperature': 0.7,
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return {'text': data['choices'][0]['message']['content']}
    except Exception as e:
        return {'error': str(e)}


def ask_gpt_json(prompt, max_tokens=4000):
    if not OPENAI_API_KEY:
        return None
    try:
        resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': 'Bearer ' + OPENAI_API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens,
                'temperature': 0.4,
                'response_format': {'type': 'json_object'},
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        text = data['choices'][0]['message']['content']
        return json.loads(text)
    except Exception as e:
        print('[Popcorn] GPT JSON error: ' + str(e))
        return None


# ============================================================
# GOOGLE TRENDS
# ============================================================
def get_google_trends(search_term, timeframe='today 12-m'):
    cache_key = 'gtrends_' + search_term + '_' + timeframe
    cached = get_cached(cache_key)
    if cached:
        return cached
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=1.0)
        pytrends.build_payload([search_term], cat=0, timeframe=timeframe)
        data = pytrends.interest_over_time()
        if data.empty:
            return {'term': search_term, 'data': {}, 'error': 'No data'}
        result = {'term': search_term, 'source': 'Google Trends', 'data': {}, 'collected_at': datetime.utcnow().isoformat()}
        for date, row in data.iterrows():
            mk = date.strftime('%Y-%m')
            val = int(row[search_term])
            if mk in result['data']:
                result['data'][mk] = round((result['data'][mk] + val) / 2)
            else:
                result['data'][mk] = val
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'term': search_term, 'source': 'Google Trends', 'data': {}, 'error': str(e)}


def get_google_trends_batch(terms, timeframe='today 12-m'):
    results = []
    for i, term in enumerate(terms):
        results.append(get_google_trends(term, timeframe))
        if i < len(terms) - 1:
            time.sleep(5)
    return results


# ============================================================
# YOUTUBE
# ============================================================
def search_youtube(query, max_results=10):
    cache_key = 'yt_' + query + '_' + str(max_results)
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not YOUTUBE_API_KEY:
        return {'query': query, 'videos': [], 'error': 'No key'}
    try:
        resp = requests.get('https://www.googleapis.com/youtube/v3/search', params={
            'part': 'snippet', 'q': query, 'type': 'video', 'order': 'relevance',
            'maxResults': max_results, 'key': YOUTUBE_API_KEY,
            'publishedAfter': (datetime.utcnow() - timedelta(days=180)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        videos = []
        for item in data.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published': item['snippet']['publishedAt'],
                'description': item['snippet']['description'][:200],
            })
        result = {'query': query, 'source': 'YouTube', 'video_count': len(videos), 'videos': videos, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'query': query, 'videos': [], 'error': str(e)}


def get_youtube_trending_by_category(category_id='24'):
    cache_key = 'yt_trend_' + category_id
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not YOUTUBE_API_KEY:
        return {'videos': [], 'error': 'No key'}
    try:
        resp = requests.get('https://www.googleapis.com/youtube/v3/videos', params={
            'part': 'snippet,statistics', 'chart': 'mostPopular', 'regionCode': 'US',
            'videoCategoryId': category_id, 'maxResults': 25, 'key': YOUTUBE_API_KEY,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        videos = []
        for item in data.get('items', []):
            stats = item.get('statistics', {})
            videos.append({
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'published': item['snippet']['publishedAt'],
            })
        result = {'source': 'YouTube Trending', 'category': category_id, 'video_count': len(videos), 'videos': videos, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'videos': [], 'error': str(e)}


# ============================================================
# SPOTIFY
# ============================================================
def get_spotify_token():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    cache_key = 'sp_token'
    cached = get_cached(cache_key)
    if cached:
        return cached
    try:
        auth_b64 = base64.b64encode((SPOTIFY_CLIENT_ID + ':' + SPOTIFY_CLIENT_SECRET).encode()).decode()
        resp = requests.post('https://accounts.spotify.com/api/token',
            headers={'Authorization': 'Basic ' + auth_b64},
            data={'grant_type': 'client_credentials'}, timeout=10)
        resp.raise_for_status()
        token = resp.json()['access_token']
        set_cache(cache_key, token)
        return token
    except Exception:
        return None


def search_spotify_playlists(query, limit=10):
    cache_key = 'sp_pl_' + query
    cached = get_cached(cache_key)
    if cached:
        return cached
    token = get_spotify_token()
    if not token:
        return {'query': query, 'playlists': [], 'error': 'No token'}
    try:
        resp = requests.get('https://api.spotify.com/v1/search',
            headers={'Authorization': 'Bearer ' + token},
            params={'q': query, 'type': 'playlist', 'limit': limit, 'market': 'US'}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        playlists = []
        for item in data.get('playlists', {}).get('items', []):
            if item:
                playlists.append({
                    'name': item.get('name', ''),
                    'description': (item.get('description', '') or '')[:150],
                    'tracks': item.get('tracks', {}).get('total', 0),
                })
        result = {'query': query, 'source': 'Spotify', 'playlist_count': len(playlists), 'playlists': playlists, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'query': query, 'playlists': [], 'error': str(e)}


# ============================================================
# WIKIPEDIA
# ============================================================
def get_wikipedia_pageviews(article, days=90):
    cache_key = 'wiki_' + article + '_' + str(days)
    cached = get_cached(cache_key)
    if cached:
        return cached
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/' + article + '/daily/' + start.strftime('%Y%m%d') + '/' + end.strftime('%Y%m%d')
        resp = requests.get(url, headers={'User-Agent': 'PopcornAI/1.0'}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        monthly = {}
        total = 0
        for item in data.get('items', []):
            views = item['views']
            total += views
            mk = item['timestamp'][:6]
            monthly[mk] = monthly.get(mk, 0) + views
        months = sorted(monthly.keys())
        vel = 0
        if len(months) >= 2:
            vel = ((monthly[months[-1]] - monthly[months[0]]) / max(monthly[months[0]], 1)) * 100
        result = {
            'article': article, 'source': 'Wikipedia', 'total_views': total,
            'daily_average': round(total / max(days, 1)), 'monthly_views': monthly,
            'velocity_pct': round(vel, 1),
            'trend': 'rising' if vel > 10 else ('falling' if vel < -10 else 'stable'),
            'collected_at': datetime.utcnow().isoformat()
        }
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'article': article, 'source': 'Wikipedia', 'total_views': 0, 'error': str(e)}


def get_wikipedia_batch(articles, days=90):
    results = []
    for a in articles:
        results.append(get_wikipedia_pageviews(a, days))
        time.sleep(0.5)
    return results


# ============================================================
# TMDB
# ============================================================
def get_tmdb_upcoming_movies():
    cache_key = 'tmdb_up'
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not TMDB_API_KEY:
        return {'movies': [], 'error': 'No key'}
    try:
        resp = requests.get('https://api.themoviedb.org/3/movie/upcoming', params={'api_key': TMDB_API_KEY, 'region': 'US'}, timeout=10)
        resp.raise_for_status()
        movies = [{'title': m['title'], 'release_date': m.get('release_date', ''), 'overview': m.get('overview', '')[:200], 'popularity': m.get('popularity', 0)} for m in resp.json().get('results', [])]
        result = {'source': 'TMDB', 'count': len(movies), 'movies': movies, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'movies': [], 'error': str(e)}


def get_tmdb_trending(media_type='all', window='week'):
    cache_key = 'tmdb_tr_' + media_type + '_' + window
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not TMDB_API_KEY:
        return {'results': [], 'error': 'No key'}
    try:
        resp = requests.get('https://api.themoviedb.org/3/trending/' + media_type + '/' + window, params={'api_key': TMDB_API_KEY}, timeout=10)
        resp.raise_for_status()
        items = [{'title': i.get('title') or i.get('name', ''), 'media_type': i.get('media_type', ''), 'overview': i.get('overview', '')[:200], 'popularity': i.get('popularity', 0)} for i in resp.json().get('results', [])[:25]]
        result = {'source': 'TMDB Trending', 'count': len(items), 'results': items, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'results': [], 'error': str(e)}


def search_tmdb(query):
    cache_key = 'tmdb_s_' + query
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not TMDB_API_KEY:
        return {'results': [], 'error': 'No key'}
    try:
        resp = requests.get('https://api.themoviedb.org/3/search/multi', params={'api_key': TMDB_API_KEY, 'query': query}, timeout=10)
        resp.raise_for_status()
        items = [{'title': i.get('title') or i.get('name', ''), 'overview': i.get('overview', '')[:200], 'popularity': i.get('popularity', 0)} for i in resp.json().get('results', [])[:10]]
        result = {'source': 'TMDB', 'query': query, 'count': len(items), 'results': items, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'results': [], 'error': str(e)}


# ============================================================
# NEWS
# ============================================================
def search_news(query, days_back=30, page_size=10):
    cache_key = 'news_' + query + '_' + str(days_back)
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not NEWS_API_KEY:
        return {'query': query, 'articles': [], 'error': 'No key'}
    try:
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        resp = requests.get('https://newsapi.org/v2/everything', params={
            'q': query, 'from': from_date, 'sortBy': 'relevancy',
            'pageSize': page_size, 'language': 'en', 'apiKey': NEWS_API_KEY,
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        articles = [{'title': a.get('title', ''), 'source': a.get('source', {}).get('name', ''), 'published': a.get('publishedAt', ''), 'description': (a.get('description', '') or '')[:200], 'url': a.get('url', '')} for a in data.get('articles', [])]
        result = {'query': query, 'source': 'NewsAPI', 'total_results': data.get('totalResults', 0), 'article_count': len(articles), 'articles': articles, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'query': query, 'articles': [], 'error': str(e)}


def get_entertainment_headlines():
    cache_key = 'news_hl'
    cached = get_cached(cache_key)
    if cached:
        return cached
    if not NEWS_API_KEY:
        return {'articles': [], 'error': 'No key'}
    try:
        resp = requests.get('https://newsapi.org/v2/top-headlines', params={
            'category': 'entertainment', 'country': 'us', 'pageSize': 20, 'apiKey': NEWS_API_KEY,
        }, timeout=10)
        resp.raise_for_status()
        articles = [{'title': a.get('title', ''), 'source': a.get('source', {}).get('name', ''), 'published': a.get('publishedAt', '')} for a in resp.json().get('articles', [])]
        result = {'source': 'NewsAPI Headlines', 'articles': articles, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'articles': [], 'error': str(e)}


# ============================================================
# AO3
# ============================================================
def get_ao3_tag_count(tag):
    cache_key = 'ao3_' + tag
    cached = get_cached(cache_key)
    if cached:
        return cached
    try:
        url = 'https://archiveofourown.org/tags/' + tag.replace(' ', '%20') + '/works'
        resp = requests.get(url, headers={'User-Agent': 'PopcornAI/1.0'}, timeout=15)
        count = 0
        if resp.status_code == 200:
            match = re.search(r'(\d[\d,]*)\s+Works?\s+found', resp.text)
            if match:
                count = int(match.group(1).replace(',', ''))
            else:
                match = re.search(r'of\s+(\d[\d,]*)\s+Works', resp.text)
                if match:
                    count = int(match.group(1).replace(',', ''))
        result = {'tag': tag, 'source': 'AO3', 'work_count': count, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'tag': tag, 'source': 'AO3', 'work_count': 0, 'error': str(e)}


def get_ao3_batch(tags):
    results = []
    for tag in tags:
        results.append(get_ao3_tag_count(tag))
        time.sleep(2)
    return results


# ============================================================
# OPEN LIBRARY
# ============================================================
def search_open_library(query, limit=10):
    cache_key = 'olib_' + query
    cached = get_cached(cache_key)
    if cached:
        return cached
    try:
        resp = requests.get('https://openlibrary.org/search.json', params={'q': query, 'limit': limit, 'sort': 'new'}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        books = [{'title': d.get('title', ''), 'author': d.get('author_name', ['Unknown'])[0] if d.get('author_name') else 'Unknown', 'year': d.get('first_publish_year', '')} for d in data.get('docs', [])]
        result = {'query': query, 'source': 'Open Library', 'total_found': data.get('numFound', 0), 'books': books, 'collected_at': datetime.utcnow().isoformat()}
        set_cache(cache_key, result)
        return result
    except Exception as e:
        return {'query': query, 'books': [], 'error': str(e)}


# ============================================================
# HARVEST ALL SIGNALS (for auto-discovery)
# ============================================================
def harvest_all_signals():
    print('[Popcorn] Harvesting signals from all sources...')
    signals = {}

    # YouTube trending entertainment
    try:
        yt_ent = get_youtube_trending_by_category('24')
        yt_music = get_youtube_trending_by_category('10')
        signals['youtube_trending'] = {
            'entertainment': [v['title'] for v in yt_ent.get('videos', [])[:25]],
            'music': [v['title'] for v in yt_music.get('videos', [])[:15]],
        }
        print('[Popcorn]   YouTube trending: OK')
    except Exception as e:
        print('[Popcorn]   YouTube trending: FAIL - ' + str(e))
        signals['youtube_trending'] = {}
    time.sleep(1)

    # YouTube searches for cultural signals
    try:
        cultural_searches = [
            'why is everyone talking about',
            'trend 2025',
            'cultural moment',
            'viral right now',
            'everyone is watching',
        ]
        yt_cultural = []
        for q in cultural_searches:
            result = search_youtube(q, max_results=5)
            yt_cultural.extend([v['title'] for v in result.get('videos', [])])
            time.sleep(1)
        signals['youtube_cultural'] = yt_cultural
        print('[Popcorn]   YouTube cultural: OK (' + str(len(yt_cultural)) + ' videos)')
    except Exception as e:
        print('[Popcorn]   YouTube cultural: FAIL - ' + str(e))
        signals['youtube_cultural'] = []

    # Spotify trending
    try:
        mood_searches = ['trending 2025', 'viral hits', 'feel good', 'sad vibes', 'anger', 'nostalgia', 'healing', 'empowerment', 'chill anxiety']
        sp_playlists = []
        for q in mood_searches:
            result = search_spotify_playlists(q, limit=5)
            for pl in result.get('playlists', []):
                sp_playlists.append(pl['name'] + ': ' + pl.get('description', '')[:80])
            time.sleep(1)
        signals['spotify_moods'] = sp_playlists
        print('[Popcorn]   Spotify moods: OK (' + str(len(sp_playlists)) + ' playlists)')
    except Exception as e:
        print('[Popcorn]   Spotify: FAIL - ' + str(e))
        signals['spotify_moods'] = []

    # Wikipedia trending cultural articles
    try:
        wiki_articles = [
            'Loneliness', 'Nostalgia', 'Mental_health', 'Masculinity',
            'Working_class', 'Spirituality', 'Artificial_intelligence',
            'Digital_detox', 'Community_building', 'Found_family',
            'Burnout_(psychology)', 'Minimalism', 'Cottagecore',
            'True_crime', 'K-pop', 'Anime', 'Streaming_media',
            'Psychedelic_therapy', 'Meditation', 'Income_inequality',
        ]
        wiki_data = []
        for a in wiki_articles:
            result = get_wikipedia_pageviews(a, 90)
            if not result.get('error'):
                wiki_data.append({
                    'topic': a.replace('_', ' '),
                    'daily_views': result.get('daily_average', 0),
                    'trend': result.get('trend', 'stable'),
                    'velocity': result.get('velocity_pct', 0),
                })
            time.sleep(0.5)
        signals['wikipedia_cultural'] = wiki_data
        print('[Popcorn]   Wikipedia: OK (' + str(len(wiki_data)) + ' articles)')
    except Exception as e:
        print('[Popcorn]   Wikipedia: FAIL - ' + str(e))
        signals['wikipedia_cultural'] = []

    # News headlines and trending entertainment
    try:
        headlines = get_entertainment_headlines()
        signals['news_headlines'] = [a['title'] for a in headlines.get('articles', [])[:20]]
        print('[Popcorn]   News headlines: OK')
    except Exception as e:
        print('[Popcorn]   News headlines: FAIL - ' + str(e))
        signals['news_headlines'] = []
    time.sleep(1)

    try:
        cultural_news_queries = ['cultural trend 2025', 'audience demand entertainment', 'what audiences want', 'streaming trends', 'gen z culture']
        news_articles = []
        for q in cultural_news_queries:
            result = search_news(q, days_back=30, page_size=5)
            for a in result.get('articles', []):
                news_articles.append(a['title'] + ' — ' + (a.get('description', '') or '')[:100])
            time.sleep(1)
        signals['news_cultural'] = news_articles
        print('[Popcorn]   News cultural: OK (' + str(len(news_articles)) + ' articles)')
    except Exception as e:
        print('[Popcorn]   News cultural: FAIL - ' + str(e))
        signals['news_cultural'] = []

    # AO3 fan fiction trending tags
    try:
        ao3_tags = [
            'Found Family', 'Hurt/Comfort', 'Enemies to Lovers',
            'Slow Burn', 'Angst', 'Fluff', 'Domestic',
            'Mental Health', 'Healing', 'Chosen Family',
            'Working Class', 'Blue Collar', 'Cottagecore',
            'Solarpunk', 'Hopepunk',
        ]
        ao3_data = []
        for tag in ao3_tags:
            result = get_ao3_tag_count(tag)
            if not result.get('error'):
                ao3_data.append({'tag': tag, 'works': result.get('work_count', 0)})
            time.sleep(2)
        signals['ao3_tags'] = ao3_data
        print('[Popcorn]   AO3: OK (' + str(len(ao3_data)) + ' tags)')
    except Exception as e:
        print('[Popcorn]   AO3: FAIL - ' + str(e))
        signals['ao3_tags'] = []

    # TMDB trending and upcoming
    try:
        trending = get_tmdb_trending('all', 'week')
        upcoming = get_tmdb_upcoming_movies()
        signals['tmdb_trending'] = [i['title'] + ': ' + i.get('overview', '')[:100] for i in trending.get('results', [])[:20]]
        signals['tmdb_upcoming'] = [m['title'] + ' (' + m.get('release_date', '') + ')' for m in upcoming.get('movies', [])[:15]]
        print('[Popcorn]   TMDB: OK')
    except Exception as e:
        print('[Popcorn]   TMDB: FAIL - ' + str(e))
        signals['tmdb_trending'] = []
        signals['tmdb_upcoming'] = []

    signals['harvested_at'] = datetime.utcnow().isoformat()
    print('[Popcorn] Harvest complete.')
    return signals
