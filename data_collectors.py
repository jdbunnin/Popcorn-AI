"""
Popcorn AI — Real Data Collectors
Pulls from: Google Trends, YouTube, Spotify, Wikipedia, 
TMDB, NewsAPI, AO3 Fan Fiction, Open Library
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta

# ============================================================
# API KEYS FROM ENVIRONMENT
# ============================================================
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')

# ============================================================
# CACHE — avoid hitting rate limits
# ============================================================
_cache = {}
CACHE_TTL = 86400  # 24 hours

def get_cached(key):
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry['time'] < CACHE_TTL:
            return entry['data']
    return None

def set_cache(key, data):
    _cache[key] = {'data': data, 'time': time.time()}


# ============================================================
# 1. GOOGLE TRENDS
# ============================================================
def get_google_trends(search_term, timeframe='today 12-m'):
    """
    Pull Google Trends data for a search term.
    Returns monthly interest scores (0-100).
    """
    cache_key = f'gtrends_{search_term}_{timeframe}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=1.0)
        pytrends.build_payload([search_term], cat=0, timeframe=timeframe)
        data = pytrends.interest_over_time()

        if data.empty:
            return {'term': search_term, 'data': {}, 'error': 'No data returned'}

        result = {
            'term': search_term,
            'source': 'Google Trends',
            'timeframe': timeframe,
            'data': {},
            'collected_at': datetime.utcnow().isoformat()
        }

        for date, row in data.iterrows():
            month_key = date.strftime('%Y-%m')
            value = int(row[search_term])
            if month_key in result['data']:
                # Average if multiple weeks in same month
                result['data'][month_key] = round(
                    (result['data'][month_key] + value) / 2
                )
            else:
                result['data'][month_key] = value

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {
            'term': search_term,
            'source': 'Google Trends',
            'data': {},
            'error': str(e)
        }


def get_google_trends_batch(terms, timeframe='today 12-m'):
    """Pull trends for multiple terms. Rate-limited."""
    results = []
    for i, term in enumerate(terms):
        result = get_google_trends(term, timeframe)
        results.append(result)
       if i < len(terms) - 1:
            time.sleep(5)  # Rate limit protection
    return results


# ============================================================
# 2. YOUTUBE
# ============================================================
def search_youtube(query, max_results=10):
    """Search YouTube and return video metadata."""
    cache_key = f'yt_search_{query}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not YOUTUBE_API_KEY:
        return {'query': query, 'videos': [], 'error': 'No YouTube API key'}

    try:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'order': 'relevance',
            'maxResults': max_results,
            'key': YOUTUBE_API_KEY,
            'publishedAfter': (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        videos = []
        for item in data.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published': item['snippet']['publishedAt'],
                'description': item['snippet']['description'][:200],
                'video_id': item['id']['videoId'],
            })

        result = {
            'query': query,
            'source': 'YouTube',
            'video_count': len(videos),
            'videos': videos,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'query': query, 'videos': [], 'error': str(e)}


def get_youtube_trending_by_category(category_id='24'):
    """
    Get trending videos by category.
    24 = Entertainment, 1 = Film, 10 = Music
    """
    cache_key = f'yt_trending_{category_id}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not YOUTUBE_API_KEY:
        return {'category': category_id, 'videos': [], 'error': 'No API key'}

    try:
        url = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': 'US',
            'videoCategoryId': category_id,
            'maxResults': 20,
            'key': YOUTUBE_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        videos = []
        for item in data.get('items', []):
            stats = item.get('statistics', {})
            videos.append({
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published': item['snippet']['publishedAt'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'video_id': item['id'],
            })

        result = {
            'category': category_id,
            'source': 'YouTube Trending',
            'video_count': len(videos),
            'videos': videos,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'category': category_id, 'videos': [], 'error': str(e)}


# ============================================================
# 3. SPOTIFY
# ============================================================
def get_spotify_token():
    """Get Spotify API access token."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None

    cache_key = 'spotify_token'
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        import base64
        auth_str = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'
        auth_b64 = base64.b64encode(auth_str.encode()).decode()

        resp = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={'Authorization': f'Basic {auth_b64}'},
            data={'grant_type': 'client_credentials'},
            timeout=10
        )
        resp.raise_for_status()
        token = resp.json()['access_token']
        set_cache(cache_key, token)
        return token
    except Exception:
        return None


def search_spotify_playlists(query, limit=10):
    """Search for playlists related to a cultural signal."""
    cache_key = f'spotify_pl_{query}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    token = get_spotify_token()
    if not token:
        return {'query': query, 'playlists': [], 'error': 'No Spotify token'}

    try:
        resp = requests.get(
            'https://api.spotify.com/v1/search',
            headers={'Authorization': f'Bearer {token}'},
            params={'q': query, 'type': 'playlist', 'limit': limit, 'market': 'US'},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        playlists = []
        total_followers = 0
        for item in data.get('playlists', {}).get('items', []):
            if item:
                playlists.append({
                    'name': item.get('name', ''),
                    'description': (item.get('description', '') or '')[:150],
                    'tracks': item.get('tracks', {}).get('total', 0),
                    'owner': item.get('owner', {}).get('display_name', ''),
                })

        result = {
            'query': query,
            'source': 'Spotify',
            'playlist_count': len(playlists),
            'playlists': playlists,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'query': query, 'playlists': [], 'error': str(e)}


def get_spotify_category_playlists(category='mood'):
    """Get playlists from a Spotify browse category."""
    cache_key = f'spotify_cat_{category}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    token = get_spotify_token()
    if not token:
        return {'category': category, 'playlists': [], 'error': 'No token'}

    try:
        resp = requests.get(
            f'https://api.spotify.com/v1/browse/categories/{category}/playlists',
            headers={'Authorization': f'Bearer {token}'},
            params={'limit': 20, 'country': 'US'},
            timeout=10
        )
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

        result = {
            'category': category,
            'source': 'Spotify Categories',
            'playlist_count': len(playlists),
            'playlists': playlists,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'category': category, 'playlists': [], 'error': str(e)}


# ============================================================
# 4. WIKIPEDIA PAGEVIEWS
# ============================================================
def get_wikipedia_pageviews(article, days=90):
    """Get daily pageviews for a Wikipedia article."""
    cache_key = f'wiki_{article}_{days}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        url = (
            f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/'
            f'en.wikipedia/all-access/all-agents/{article}/daily/'
            f'{start_date.strftime("%Y%m%d")}/{end_date.strftime("%Y%m%d")}'
        )

        resp = requests.get(url, headers={'User-Agent': 'PopcornAI/1.0'}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        daily_views = {}
        monthly_views = {}
        total_views = 0

        for item in data.get('items', []):
            date_str = item['timestamp'][:8]
            views = item['views']
            daily_views[date_str] = views
            total_views += views

            month_key = date_str[:6]
            if month_key not in monthly_views:
                monthly_views[month_key] = 0
            monthly_views[month_key] += views

        # Calculate trend
        months = sorted(monthly_views.keys())
        if len(months) >= 2:
            first_month = monthly_views[months[0]]
            last_month = monthly_views[months[-1]]
            velocity = ((last_month - first_month) / max(first_month, 1)) * 100
        else:
            velocity = 0

        result = {
            'article': article,
            'source': 'Wikipedia',
            'total_views': total_views,
            'daily_average': round(total_views / max(days, 1)),
            'monthly_views': monthly_views,
            'velocity_pct': round(velocity, 1),
            'trend': 'rising' if velocity > 10 else ('falling' if velocity < -10 else 'stable'),
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {
            'article': article,
            'source': 'Wikipedia',
            'total_views': 0,
            'error': str(e)
        }


def get_wikipedia_batch(articles, days=90):
    """Get pageviews for multiple articles."""
    results = []
    for article in articles:
        result = get_wikipedia_pageviews(article, days)
        results.append(result)
        time.sleep(0.5)  # Rate limit
    return results


# ============================================================
# 5. TMDB — Upcoming Movies & Shows
# ============================================================
def get_tmdb_upcoming_movies(page=1):
    """Get upcoming movie releases."""
    cache_key = f'tmdb_upcoming_{page}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not TMDB_API_KEY:
        return {'movies': [], 'error': 'No TMDB API key'}

    try:
        resp = requests.get(
            'https://api.themoviedb.org/3/movie/upcoming',
            params={'api_key': TMDB_API_KEY, 'region': 'US', 'page': page},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        movies = []
        for m in data.get('results', []):
            movies.append({
                'title': m['title'],
                'release_date': m.get('release_date', ''),
                'overview': m.get('overview', '')[:200],
                'genre_ids': m.get('genre_ids', []),
                'popularity': m.get('popularity', 0),
                'vote_average': m.get('vote_average', 0),
            })

        result = {
            'source': 'TMDB',
            'type': 'upcoming_movies',
            'count': len(movies),
            'movies': movies,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'movies': [], 'error': str(e)}


def get_tmdb_trending(media_type='all', time_window='week'):
    """Get trending movies/shows."""
    cache_key = f'tmdb_trending_{media_type}_{time_window}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not TMDB_API_KEY:
        return {'results': [], 'error': 'No TMDB API key'}

    try:
        resp = requests.get(
            f'https://api.themoviedb.org/3/trending/{media_type}/{time_window}',
            params={'api_key': TMDB_API_KEY},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        items = []
        for item in data.get('results', [])[:20]:
            items.append({
                'title': item.get('title') or item.get('name', ''),
                'media_type': item.get('media_type', ''),
                'overview': item.get('overview', '')[:200],
                'popularity': item.get('popularity', 0),
                'vote_average': item.get('vote_average', 0),
                'release_date': item.get('release_date') or item.get('first_air_date', ''),
            })

        result = {
            'source': 'TMDB',
            'type': 'trending',
            'media_type': media_type,
            'time_window': time_window,
            'count': len(items),
            'results': items,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'results': [], 'error': str(e)}


def search_tmdb(query, media_type='multi'):
    """Search TMDB for movies/shows."""
    cache_key = f'tmdb_search_{query}_{media_type}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not TMDB_API_KEY:
        return {'results': [], 'error': 'No TMDB API key'}

    try:
        resp = requests.get(
            f'https://api.themoviedb.org/3/search/{media_type}',
            params={'api_key': TMDB_API_KEY, 'query': query},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get('results', [])[:10]:
            results.append({
                'title': item.get('title') or item.get('name', ''),
                'media_type': item.get('media_type', media_type),
                'overview': item.get('overview', '')[:200],
                'popularity': item.get('popularity', 0),
                'release_date': item.get('release_date') or item.get('first_air_date', ''),
            })

        result = {
            'source': 'TMDB',
            'query': query,
            'count': len(results),
            'results': results,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'results': [], 'error': str(e)}


# ============================================================
# 6. NEWS API
# ============================================================
def search_news(query, days_back=30, page_size=10):
    """Search recent news articles."""
    cache_key = f'news_{query}_{days_back}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not NEWS_API_KEY:
        return {'query': query, 'articles': [], 'error': 'No News API key'}

    try:
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        resp = requests.get(
            'https://newsapi.org/v2/everything',
            params={
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'pageSize': page_size,
                'language': 'en',
                'apiKey': NEWS_API_KEY,
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for a in data.get('articles', []):
            articles.append({
                'title': a.get('title', ''),
                'source': a.get('source', {}).get('name', ''),
                'published': a.get('publishedAt', ''),
                'description': (a.get('description', '') or '')[:200],
                'url': a.get('url', ''),
            })

        result = {
            'query': query,
            'source': 'NewsAPI',
            'total_results': data.get('totalResults', 0),
            'article_count': len(articles),
            'articles': articles,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'query': query, 'articles': [], 'error': str(e)}


def get_entertainment_headlines():
    """Get top entertainment headlines."""
    cache_key = 'news_entertainment_headlines'
    cached = get_cached(cache_key)
    if cached:
        return cached

    if not NEWS_API_KEY:
        return {'articles': [], 'error': 'No News API key'}

    try:
        resp = requests.get(
            'https://newsapi.org/v2/top-headlines',
            params={
                'category': 'entertainment',
                'country': 'us',
                'pageSize': 20,
                'apiKey': NEWS_API_KEY,
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for a in data.get('articles', []):
            articles.append({
                'title': a.get('title', ''),
                'source': a.get('source', {}).get('name', ''),
                'published': a.get('publishedAt', ''),
                'description': (a.get('description', '') or '')[:200],
                'url': a.get('url', ''),
            })

        result = {
            'source': 'NewsAPI Headlines',
            'article_count': len(articles),
            'articles': articles,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'articles': [], 'error': str(e)}


# ============================================================
# 7. AO3 FAN FICTION (Archive of Our Own)
# ============================================================
def get_ao3_tag_count(tag):
    """
    Get the number of works for a tag on AO3.
    This is a proxy for fandom intensity and cultural interest.
    """
    cache_key = f'ao3_{tag}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        url = f'https://archiveofourown.org/tags/{tag.replace(" ", "%20")}/works'
        resp = requests.get(
            url,
            headers={'User-Agent': 'PopcornAI/1.0 (audience research)'},
            timeout=15
        )

        if resp.status_code == 200:
            text = resp.text
            # Extract work count from page
            import re
            match = re.search(r'(\d[\d,]*)\s+Works?\s+found', text)
            if match:
                count = int(match.group(1).replace(',', ''))
            else:
                match = re.search(r'of\s+(\d[\d,]*)\s+Works', text)
                if match:
                    count = int(match.group(1).replace(',', ''))
                else:
                    count = 0

            result = {
                'tag': tag,
                'source': 'AO3',
                'work_count': count,
                'url': url,
                'collected_at': datetime.utcnow().isoformat()
            }
        else:
            result = {
                'tag': tag,
                'source': 'AO3',
                'work_count': 0,
                'error': f'Status {resp.status_code}'
            }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'tag': tag, 'source': 'AO3', 'work_count': 0, 'error': str(e)}


def get_ao3_batch(tags):
    """Get work counts for multiple AO3 tags."""
    results = []
    for tag in tags:
        result = get_ao3_tag_count(tag)
        results.append(result)
        time.sleep(2)  # Be respectful to AO3
    return results


# ============================================================
# 8. OPEN LIBRARY (Book Trends)
# ============================================================
def search_open_library(query, limit=10):
    """Search Open Library for books related to a cultural signal."""
    cache_key = f'openlib_{query}'
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        resp = requests.get(
            'https://openlibrary.org/search.json',
            params={'q': query, 'limit': limit, 'sort': 'new'},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        books = []
        for doc in data.get('docs', []):
            books.append({
                'title': doc.get('title', ''),
                'author': doc.get('author_name', ['Unknown'])[0] if doc.get('author_name') else 'Unknown',
                'first_publish_year': doc.get('first_publish_year', ''),
                'subject': doc.get('subject', [])[:5],
                'edition_count': doc.get('edition_count', 0),
            })

        result = {
            'query': query,
            'source': 'Open Library',
            'total_found': data.get('numFound', 0),
            'book_count': len(books),
            'books': books,
            'collected_at': datetime.utcnow().isoformat()
        }

        set_cache(cache_key, result)
        return result

    except Exception as e:
        return {'query': query, 'books': [], 'error': str(e)}


# ============================================================
# MASTER: Collect All Signals for a Cultural Current
# ============================================================
def collect_signals_for_topic(topic_name, search_terms, wiki_articles, ao3_tags, news_queries):
    """
    Collect data from ALL sources for a single cultural topic.
    Returns a comprehensive signal package.
    """
    signals = {
        'topic': topic_name,
        'collected_at': datetime.utcnow().isoformat(),
        'sources': {},
    }

    # Google Trends
    if search_terms:
        signals['sources']['google_trends'] = get_google_trends_batch(search_terms)

    # YouTube
    if search_terms:
        yt_results = []
        for term in search_terms[:3]:  # Limit to save quota
            yt_results.append(search_youtube(term, max_results=5))
            time.sleep(1)
        signals['sources']['youtube'] = yt_results

    # Spotify
    if search_terms:
        sp_results = []
        for term in search_terms[:3]:
            sp_results.append(search_spotify_playlists(term, limit=5))
            time.sleep(1)
        signals['sources']['spotify'] = sp_results

    # Wikipedia
    if wiki_articles:
        signals['sources']['wikipedia'] = get_wikipedia_batch(wiki_articles)

    # News
    if news_queries:
        news_results = []
        for query in news_queries[:3]:
            news_results.append(search_news(query, days_back=30, page_size=5))
            time.sleep(1)
        signals['sources']['news'] = news_results

    # AO3
    if ao3_tags:
        signals['sources']['ao3'] = get_ao3_batch(ao3_tags)

    # TMDB
    if search_terms:
        tmdb_results = []
        for term in search_terms[:2]:
            tmdb_results.append(search_tmdb(term))
            time.sleep(0.5)
        signals['sources']['tmdb'] = tmdb_results

    return signals
