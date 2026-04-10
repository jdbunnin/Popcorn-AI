"""
Popcorn AI — Audience Demand Intelligence
v3.1: Pre-computed Google Trends + Live data from other sources
"""

from flask import Flask, jsonify, send_from_directory, request
import os
import threading
import time as time_module
from datetime import datetime
from data_collectors import (
    get_google_trends,
    search_youtube,
    search_spotify_playlists,
    get_wikipedia_pageviews,
    get_wikipedia_batch,
    get_tmdb_upcoming_movies,
    get_tmdb_trending,
    search_tmdb,
    search_news,
    get_entertainment_headlines,
    get_ao3_tag_count,
    get_ao3_batch,
    search_open_library,
    get_google_trends_batch,
    get_youtube_trending_by_category,
)

app = Flask(__name__, static_folder='public', static_url_path='')

# ============================================================
# TRENDS CACHE
# ============================================================
trends_cache = {}
trends_loading = False
trends_loaded = False


def precompute_trends():
    global trends_cache, trends_loading, trends_loaded
    trends_loading = True
    all_terms = set()
    for p in PREDICTIONS:
        for term in p['search_terms']:
            all_terms.add(term)
    print('[Popcorn] Loading ' + str(len(all_terms)) + ' trends...')
    for term in all_terms:
        try:
            result = get_google_trends(term, 'today 12-m')
            trends_cache[term] = result
            print('[Popcorn] OK: ' + term)
        except Exception as e:
            print('[Popcorn] FAIL: ' + term + ' - ' + str(e))
            trends_cache[term] = {'term': term, 'data': {}, 'error': str(e)}
        time_module.sleep(8)
    trends_loading = False
    trends_loaded = True
    print('[Popcorn] Done. ' + str(len(trends_cache)) + ' terms cached.')


# ============================================================
# PREDICTIONS DATA
# ============================================================
PREDICTIONS = [
    {
        'id': 'analog-humanity',
        'name': 'The Human Premium',
        'category': 'Cultural Collision',
        'thesis': 'AI anxiety is driving a counter-movement celebrating irreplaceable human qualities — craftsmanship, physical presence, emotional intuition, and analog experiences.',
        'prediction': 'Content celebrating handmade craft, analog experiences, and human connection will outperform digital/tech-focused content by 2-3x within 12 months.',
        'timeframe': '6-12 months',
        'date_published': '2025-04-10',
        'search_terms': ['analog lifestyle', 'digital detox', 'handmade crafts', 'film photography', 'vinyl records', 'board game cafe', 'artisan craftsmanship'],
        'wiki_articles': ['Slow_movement_(culture)', 'Handicraft', 'Vinyl_revival', 'Film_photography', 'Digital_detox'],
        'ao3_tags': ['Domestic Fluff', 'Cottagecore', 'Slice of Life'],
        'news_queries': ['analog renaissance', 'handmade crafts trend', 'digital detox movement'],
        'spotify_queries': ['acoustic chill', 'folk and craft', 'unplugged living'],
    },
    {
        'id': 'male-vulnerability',
        'name': 'Male Emotional Awakening',
        'category': 'Psychological Drive',
        'thesis': 'Male mental health discourse has exploded. Men are searching for permission to be emotionally vulnerable. Content featuring genuinely open male characters will find a massive underserved audience.',
        'prediction': 'A show or film featuring a male lead whose primary arc is emotional vulnerability will become a top-10 cultural moment within 18 months.',
        'timeframe': '6-18 months',
        'date_published': '2025-04-10',
        'search_terms': ['mens mental health', 'therapy for men', 'men crying', 'toxic masculinity', 'male vulnerability', 'men emotional support', 'boys dont cry myth'],
        'wiki_articles': ['Masculinity', 'Mental_health_of_men', 'Toxic_masculinity', 'Emotional_intelligence'],
        'ao3_tags': ['Hurt/Comfort', 'Emotional Hurt/Comfort', 'Male Friendship'],
        'news_queries': ['men mental health crisis', 'male vulnerability culture', 'men therapy trend'],
        'spotify_queries': ['sad songs for men', 'mens mental health', 'emotional healing'],
    },
    {
        'id': 'found-family',
        'name': 'Found Family Renaissance',
        'category': 'Belonging Drive',
        'thesis': 'Loneliness epidemic plus declining traditional family structures are driving massive demand for stories about chosen families.',
        'prediction': 'The next breakout ensemble show will center on found family dynamics in a non-traditional setting.',
        'timeframe': '3-12 months',
        'date_published': '2025-04-10',
        'search_terms': ['loneliness epidemic', 'found family', 'chosen family', 'making friends as adult', 'community building', 'third places', 'belonging'],
        'wiki_articles': ['Loneliness', 'Chosen_family', 'Third_place', 'Social_isolation'],
        'ao3_tags': ['Found Family', 'Chosen Family', 'Team as Family', 'Platonic Relationships'],
        'news_queries': ['loneliness epidemic america', 'community building trend', 'third places revival'],
        'spotify_queries': ['feel good community', 'friendship anthems', 'together playlist'],
    },
    {
        'id': 'class-consciousness',
        'name': 'Working Class Visibility',
        'category': 'Identity Demand',
        'thesis': '74% of Americans work outside offices but nearly all prestige content depicts upper-middle-class life. The demand gap is widening.',
        'prediction': 'At least two major streaming shows set in blue-collar environments will be greenlit and one will become a top performer within 18 months.',
        'timeframe': '6-18 months',
        'date_published': '2025-04-10',
        'search_terms': ['working class tv shows', 'blue collar jobs', 'skilled trades career', 'trade school vs college', 'construction workers', 'everyday heroes', 'working class representation'],
        'wiki_articles': ['Working_class', 'Blue-collar_worker', 'Trades_(occupation)', 'Class_consciousness'],
        'ao3_tags': ['Working Class', 'Blue Collar', 'Slice of Life'],
        'news_queries': ['skilled trades shortage', 'blue collar renaissance', 'working class culture'],
        'spotify_queries': ['working class anthems', 'blue collar playlist', 'country working man'],
    },
    {
        'id': 'spiritual-not-religious',
        'name': 'Secular Spirituality Wave',
        'category': 'Meaning Drive',
        'thesis': 'Spiritual but not religious is the fastest growing identity category in under-40 demographics. Zero mainstream entertainment takes spirituality seriously.',
        'prediction': 'A prestige series treating non-religious spirituality with the seriousness The Bear treats cooking will become a cultural touchstone.',
        'timeframe': '12-24 months',
        'date_published': '2025-04-10',
        'search_terms': ['spiritual but not religious', 'meditation benefits', 'psychedelic therapy', 'consciousness exploration', 'astrology trend', 'meaning of life', 'spiritual awakening'],
        'wiki_articles': ['Spiritual_but_not_religious', 'Meditation', 'Psychedelic_therapy', 'Astrology_and_science', 'Mindfulness'],
        'ao3_tags': ['Spiritual', 'Meditation', 'Magical Realism'],
        'news_queries': ['psychedelic therapy legalization', 'meditation mainstream', 'spiritual not religious trend'],
        'spotify_queries': ['meditation music', 'spiritual journey', 'consciousness exploration'],
    },
]


# ============================================================
# COLLECT SIGNALS (cached trends + live everything else)
# ============================================================
def collect_prediction_signals(prediction):
    signals = {
        'topic': prediction['name'],
        'collected_at': datetime.utcnow().isoformat(),
        'sources': {},
    }

    # Google Trends — FROM CACHE ONLY
    cached_trends = []
    for term in prediction['search_terms']:
        if term in trends_cache:
            cached_trends.append(trends_cache[term])
        else:
            cached_trends.append({
                'term': term,
                'source': 'Google Trends',
                'data': {},
                'error': 'Still loading in background. Try again in a few minutes.'
            })
    signals['sources']['google_trends'] = cached_trends

    # YouTube — LIVE
    yt = []
    for term in prediction['search_terms'][:3]:
        yt.append(search_youtube(term, max_results=5))
        time_module.sleep(0.5)
    signals['sources']['youtube'] = yt

    # Spotify — LIVE
    sp = []
    for q in prediction.get('spotify_queries', [])[:3]:
        sp.append(search_spotify_playlists(q, limit=5))
        time_module.sleep(0.5)
    signals['sources']['spotify'] = sp

    # Wikipedia — LIVE
    signals['sources']['wikipedia'] = get_wikipedia_batch(prediction['wiki_articles'])

    # News — LIVE
    news = []
    for q in prediction['news_queries'][:3]:
        news.append(search_news(q, days_back=30, page_size=5))
        time_module.sleep(0.5)
    signals['sources']['news'] = news

    # AO3 — LIVE
    signals['sources']['ao3'] = get_ao3_batch(prediction['ao3_tags'])

    # TMDB — LIVE
    tmdb = []
    for term in prediction['search_terms'][:2]:
        tmdb.append(search_tmdb(term))
        time_module.sleep(0.3)
    signals['sources']['tmdb'] = tmdb

    return signals


# ============================================================
# SIGNAL STRENGTH
# ============================================================
def calculate_signal_strength(signals):
    scores = {}
    total_score = 0
    source_count = 0
    sources = signals.get('sources', {})

    # Google Trends
    if 'google_trends' in sources:
        velocities = []
        for t in sources['google_trends']:
            if isinstance(t, dict) and t.get('data') and not t.get('error'):
                data = t['data']
                months = sorted(data.keys())
                if len(months) >= 2:
                    first = data[months[0]]
                    last = data[months[-1]]
                    vel = ((last - first) / max(first, 1)) * 100
                    velocities.append(vel)
        if velocities:
            avg = sum(velocities) / len(velocities)
            sc = min(100, max(0, avg + 50))
            scores['google_trends'] = {'score': round(sc), 'detail': 'Velocity: ' + str(round(avg, 1)) + '% across ' + str(len(velocities)) + ' terms'}
            total_score += sc
            source_count += 1
        else:
            scores['google_trends'] = {'score': 0, 'detail': 'Trends loading in background...'}

    # YouTube
    if 'youtube' in sources:
        total_vids = sum(r.get('video_count', 0) for r in sources['youtube'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, total_vids * 5)
        scores['youtube'] = {'score': round(sc), 'detail': str(total_vids) + ' videos found'}
        total_score += sc
        source_count += 1

    # Spotify
    if 'spotify' in sources:
        total_pl = sum(r.get('playlist_count', 0) for r in sources['spotify'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, total_pl * 8)
        scores['spotify'] = {'score': round(sc), 'detail': str(total_pl) + ' playlists found'}
        total_score += sc
        source_count += 1

    # Wikipedia
    if 'wikipedia' in sources:
        rising = sum(1 for w in sources['wikipedia'] if isinstance(w, dict) and w.get('trend') == 'rising')
        total = len([w for w in sources['wikipedia'] if isinstance(w, dict) and not w.get('error')])
        sc = min(100, (rising / max(total, 1)) * 100)
        scores['wikipedia'] = {'score': round(sc), 'detail': str(rising) + '/' + str(total) + ' articles rising'}
        total_score += sc
        source_count += 1

    # News
    if 'news' in sources:
        total_art = sum(r.get('total_results', 0) for r in sources['news'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, total_art * 2)
        scores['news'] = {'score': round(sc), 'detail': str(total_art) + ' articles found'}
        total_score += sc
        source_count += 1

    # AO3
    if 'ao3' in sources:
        total_works = sum(r.get('work_count', 0) for r in sources['ao3'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, (total_works / 1000) * 10)
        scores['ao3'] = {'score': round(sc), 'detail': str(total_works) + ' fan fiction works'}
        total_score += sc
        source_count += 1

    # TMDB
    if 'tmdb' in sources:
        total_res = sum(r.get('count', 0) for r in sources['tmdb'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, max(0, 100 - (total_res * 8)))
        scores['tmdb'] = {'score': round(sc), 'detail': str(total_res) + ' existing titles (less = bigger gap)'}
        total_score += sc
        source_count += 1

    overall = round(total_score / max(source_count, 1))
    return {
        'overall_score': overall,
        'confidence': 'HIGH' if overall >= 70 else ('MODERATE' if overall >= 45 else 'LOW'),
        'sources_used': source_count,
        'source_scores': scores,
        'interpretation': 'Strong converging signals.' if overall >= 70 else ('Moderate signals. Demand building.' if overall >= 45 else 'Early signals. Monitor for acceleration.'),
    }


# ============================================================
# ROUTES
# ============================================================
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'app': 'Popcorn AI',
        'version': '3.1',
        'trends_cached': len(trends_cache),
        'trends_loading': trends_loading,
        'trends_loaded': trends_loaded,
        'data_sources': {
            'youtube': bool(os.environ.get('YOUTUBE_API_KEY')),
            'spotify': bool(os.environ.get('SPOTIFY_CLIENT_ID')),
            'tmdb': bool(os.environ.get('TMDB_API_KEY')),
            'news': bool(os.environ.get('NEWS_API_KEY')),
            'google_trends': True,
            'wikipedia': True,
            'ao3': True,
            'open_library': True,
        },
    })


@app.route('/api/predictions')
def get_predictions():
    preds = []
    for p in PREDICTIONS:
        preds.append({
            'id': p['id'],
            'name': p['name'],
            'category': p['category'],
            'thesis': p['thesis'],
            'prediction': p['prediction'],
            'timeframe': p['timeframe'],
            'date_published': p['date_published'],
            'search_term_count': len(p['search_terms']),
            'data_sources': ['Google Trends', 'YouTube', 'Spotify', 'Wikipedia', 'NewsAPI', 'AO3', 'TMDB'],
        })
    return jsonify({
        'count': len(preds),
        'predictions': preds,
        'trends_status': 'loaded' if trends_loaded else ('loading' if trends_loading else 'not started'),
        'generated_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/predictions/<prediction_id>/signals')
def get_prediction_signals(prediction_id):
    pred = None
    for p in PREDICTIONS:
        if p['id'] == prediction_id:
            pred = p
            break
    if not pred:
        return jsonify({'error': 'Not found'}), 404

    signals = collect_prediction_signals(pred)
    strength = calculate_signal_strength(signals)

    return jsonify({
        'prediction_id': prediction_id,
        'prediction_name': pred['name'],
        'thesis': pred['thesis'],
        'prediction_text': pred['prediction'],
        'timeframe': pred['timeframe'],
        'date_published': pred['date_published'],
        'signal_strength': strength,
        'raw_signals': signals,
        'trends_status': 'loaded' if trends_loaded else 'loading',
        'collected_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/trends/status')
def get_trends_status():
    return jsonify({
        'loading': trends_loading,
        'loaded': trends_loaded,
        'cached_terms': len(trends_cache),
        'terms': list(trends_cache.keys()),
    })


@app.route('/api/trends/refresh', methods=['POST'])
def refresh_trends():
    if trends_loading:
        return jsonify({'message': 'Already loading.'}), 429
    thread = threading.Thread(target=precompute_trends, daemon=True)
    thread.start()
    return jsonify({'message': 'Refresh started.'})


# Scanner routes
@app.route('/api/scan/trends')
def scan_trends():
    terms = request.args.get('terms', '')
    if not terms:
        return jsonify({'error': 'Provide ?terms=term1,term2'}), 400
    term_list = [t.strip() for t in terms.split(',') if t.strip()][:10]
    return jsonify({'terms': term_list, 'results': get_google_trends_batch(term_list), 'collected_at': datetime.utcnow().isoformat()})


@app.route('/api/scan/youtube')
def scan_youtube():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_youtube(q, max_results=10))


@app.route('/api/scan/youtube/trending')
def scan_yt_trending():
    return jsonify(get_youtube_trending_by_category(request.args.get('category', '24')))


@app.route('/api/scan/spotify')
def scan_spotify():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_spotify_playlists(q, limit=10))


@app.route('/api/scan/wikipedia')
def scan_wiki():
    articles = request.args.get('articles', '')
    if not articles:
        return jsonify({'error': 'Provide ?articles=A1,A2'}), 400
    art_list = [a.strip() for a in articles.split(',') if a.strip()][:10]
    days = int(request.args.get('days', '90'))
    return jsonify({'articles': art_list, 'results': get_wikipedia_batch(art_list, days), 'collected_at': datetime.utcnow().isoformat()})


@app.route('/api/scan/news')
def scan_news_route():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_news(q, days_back=int(request.args.get('days', '30'))))


@app.route('/api/scan/news/headlines')
def scan_headlines():
    return jsonify(get_entertainment_headlines())


@app.route('/api/scan/ao3')
def scan_ao3():
    tags = request.args.get('tags', '')
    if not tags:
        return jsonify({'error': 'Provide ?tags=T1,T2'}), 400
    tag_list = [t.strip() for t in tags.split(',') if t.strip()][:10]
    return jsonify({'tags': tag_list, 'results': get_ao3_batch(tag_list), 'collected_at': datetime.utcnow().isoformat()})


@app.route('/api/scan/tmdb/trending')
def scan_tmdb_trend():
    return jsonify(get_tmdb_trending(request.args.get('type', 'all'), request.args.get('window', 'week')))


@app.route('/api/scan/tmdb/upcoming')
def scan_tmdb_up():
    return jsonify(get_tmdb_upcoming_movies())


@app.route('/api/scan/books')
def scan_books():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_open_library(q))


# Retroactive proof
@app.route('/api/analyses')
def get_analyses():
    from retroactive import get_all_analyses
    return jsonify(get_all_analyses())


@app.route('/api/analysis/<case_id>')
def get_analysis(case_id):
    from retroactive import get_all_analyses
    data = get_all_analyses()
    if case_id in data:
        return jsonify(data[case_id])
    return jsonify({'error': 'Not found'}), 404


# ============================================================
# STARTUP — load trends in background
# ============================================================
@app.before_request
def auto_start_trends():
    global trends_loading
    if not trends_loaded and not trends_loading:
        thread = threading.Thread(target=precompute_trends, daemon=True)
        thread.start()


# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
