"""
Popcorn AI v3.2 — Fixed for Render free tier
All API calls happen on a manual refresh trigger, not on page click.
Prediction clicks show cached data instantly.
"""

from flask import Flask, jsonify, send_from_directory, request
import os
import json
import threading
import time as t
from datetime import datetime
from data_collectors import (
    get_google_trends,
    search_youtube,
    search_spotify_playlists,
    get_wikipedia_pageviews,
    get_wikipedia_batch,
    get_tmdb_trending,
    search_tmdb,
    search_news,
    get_entertainment_headlines,
    get_ao3_tag_count,
    get_ao3_batch,
    search_open_library,
    get_google_trends_batch,
    get_youtube_trending_by_category,
    get_tmdb_upcoming_movies,
)

app = Flask(__name__, static_folder='public', static_url_path='')

# ============================================================
# SIGNAL CACHE — All prediction data is pre-computed
# ============================================================
signal_cache = {}
cache_loading = False
cache_loaded = False
cache_status = 'not started'

PREDICTIONS = [
    {
        'id': 'analog-humanity',
        'name': 'The Human Premium',
        'category': 'Cultural Collision',
        'thesis': 'AI anxiety is driving a counter-movement celebrating irreplaceable human qualities — craftsmanship, physical presence, emotional intuition, and analog experiences.',
        'prediction': 'Content celebrating handmade craft, analog experiences, and human connection will outperform digital/tech-focused content by 2-3x within 12 months.',
        'timeframe': '6-12 months',
        'date_published': '2025-04-10',
        'search_terms': ['analog lifestyle', 'digital detox', 'handmade crafts', 'film photography', 'vinyl records'],
        'wiki_articles': ['Slow_movement_(culture)', 'Handicraft', 'Vinyl_revival'],
        'ao3_tags': ['Domestic Fluff', 'Cottagecore', 'Slice of Life'],
        'news_queries': ['analog renaissance', 'handmade crafts trend'],
        'spotify_queries': ['acoustic chill', 'folk and craft'],
    },
    {
        'id': 'male-vulnerability',
        'name': 'Male Emotional Awakening',
        'category': 'Psychological Drive',
        'thesis': 'Male mental health discourse has exploded. Content featuring genuinely open male characters will find a massive underserved audience.',
        'prediction': 'A show or film featuring a male lead whose primary arc is emotional vulnerability will become a top-10 cultural moment within 18 months.',
        'timeframe': '6-18 months',
        'date_published': '2025-04-10',
        'search_terms': ['mens mental health', 'therapy for men', 'male vulnerability', 'toxic masculinity', 'men emotional support'],
        'wiki_articles': ['Masculinity', 'Mental_health_of_men', 'Toxic_masculinity'],
        'ao3_tags': ['Hurt/Comfort', 'Emotional Hurt/Comfort', 'Male Friendship'],
        'news_queries': ['men mental health crisis', 'male vulnerability culture'],
        'spotify_queries': ['sad songs for men', 'emotional healing'],
    },
    {
        'id': 'found-family',
        'name': 'Found Family Renaissance',
        'category': 'Belonging Drive',
        'thesis': 'Loneliness epidemic plus declining traditional family structures are driving massive demand for stories about chosen families.',
        'prediction': 'The next breakout ensemble show will center on found family dynamics in a non-traditional setting.',
        'timeframe': '3-12 months',
        'date_published': '2025-04-10',
        'search_terms': ['loneliness epidemic', 'found family', 'chosen family', 'making friends as adult', 'third places'],
        'wiki_articles': ['Loneliness', 'Chosen_family', 'Third_place'],
        'ao3_tags': ['Found Family', 'Chosen Family', 'Team as Family'],
        'news_queries': ['loneliness epidemic america', 'community building trend'],
        'spotify_queries': ['feel good community', 'friendship anthems'],
    },
    {
        'id': 'class-consciousness',
        'name': 'Working Class Visibility',
        'category': 'Identity Demand',
        'thesis': '74% of Americans work outside offices but nearly all prestige content depicts upper-middle-class life.',
        'prediction': 'At least two major streaming shows set in blue-collar environments will be greenlit and one will become a top performer within 18 months.',
        'timeframe': '6-18 months',
        'date_published': '2025-04-10',
        'search_terms': ['working class tv shows', 'blue collar jobs', 'skilled trades career', 'trade school vs college', 'working class representation'],
        'wiki_articles': ['Working_class', 'Blue-collar_worker', 'Trades_(occupation)'],
        'ao3_tags': ['Working Class', 'Blue Collar', 'Slice of Life'],
        'news_queries': ['skilled trades shortage', 'blue collar renaissance'],
        'spotify_queries': ['working class anthems', 'blue collar playlist'],
    },
    {
        'id': 'spiritual-not-religious',
        'name': 'Secular Spirituality Wave',
        'category': 'Meaning Drive',
        'thesis': 'Spiritual but not religious is the fastest growing identity category in under-40 demographics. Zero mainstream entertainment takes spirituality seriously.',
        'prediction': 'A prestige series treating non-religious spirituality with the seriousness The Bear treats cooking will become a cultural touchstone.',
        'timeframe': '12-24 months',
        'date_published': '2025-04-10',
        'search_terms': ['spiritual but not religious', 'meditation benefits', 'psychedelic therapy', 'meaning of life', 'spiritual awakening'],
        'wiki_articles': ['Spiritual_but_not_religious', 'Meditation', 'Psychedelic_therapy'],
        'ao3_tags': ['Spiritual', 'Meditation', 'Magical Realism'],
        'news_queries': ['psychedelic therapy legalization', 'meditation mainstream'],
        'spotify_queries': ['meditation music', 'spiritual journey'],
    },
]


# ============================================================
# BACKGROUND DATA LOADER
# ============================================================
def load_all_signals():
    global signal_cache, cache_loading, cache_loaded, cache_status

    cache_loading = True
    cache_status = 'loading'

    for pred in PREDICTIONS:
        pid = pred['id']
        print('[Popcorn] Loading signals for: ' + pred['name'])

        signals = {'sources': {}, 'collected_at': datetime.utcnow().isoformat()}

        # YouTube (fast, reliable)
        try:
            yt = []
            for term in pred['search_terms'][:2]:
                yt.append(search_youtube(term, max_results=5))
                t.sleep(1)
            signals['sources']['youtube'] = yt
            print('[Popcorn]   YouTube OK')
        except Exception as e:
            print('[Popcorn]   YouTube FAIL: ' + str(e))
            signals['sources']['youtube'] = []

        # Spotify (fast, reliable)
        try:
            sp = []
            for q in pred.get('spotify_queries', [])[:2]:
                sp.append(search_spotify_playlists(q, limit=5))
                t.sleep(1)
            signals['sources']['spotify'] = sp
            print('[Popcorn]   Spotify OK')
        except Exception as e:
            print('[Popcorn]   Spotify FAIL: ' + str(e))
            signals['sources']['spotify'] = []

        # Wikipedia (fast, reliable)
        try:
            signals['sources']['wikipedia'] = get_wikipedia_batch(pred['wiki_articles'][:3])
            print('[Popcorn]   Wikipedia OK')
        except Exception as e:
            print('[Popcorn]   Wikipedia FAIL: ' + str(e))
            signals['sources']['wikipedia'] = []

        # News (fast, reliable)
        try:
            news = []
            for q in pred['news_queries'][:2]:
                news.append(search_news(q, days_back=30, page_size=5))
                t.sleep(1)
            signals['sources']['news'] = news
            print('[Popcorn]   News OK')
        except Exception as e:
            print('[Popcorn]   News FAIL: ' + str(e))
            signals['sources']['news'] = []

        # AO3 (slow but reliable)
        try:
            signals['sources']['ao3'] = get_ao3_batch(pred['ao3_tags'][:3])
            print('[Popcorn]   AO3 OK')
        except Exception as e:
            print('[Popcorn]   AO3 FAIL: ' + str(e))
            signals['sources']['ao3'] = []

        # TMDB (fast)
        try:
            tmdb = []
            for term in pred['search_terms'][:1]:
                tmdb.append(search_tmdb(term))
            signals['sources']['tmdb'] = tmdb
            print('[Popcorn]   TMDB OK')
        except Exception as e:
            print('[Popcorn]   TMDB FAIL: ' + str(e))
            signals['sources']['tmdb'] = []

        # Google Trends (slow, unreliable — do last, skip if fails)
        try:
            trends = []
            for term in pred['search_terms'][:3]:
                trends.append(get_google_trends(term, 'today 12-m'))
                t.sleep(8)
            signals['sources']['google_trends'] = trends
            print('[Popcorn]   Trends OK')
        except Exception as e:
            print('[Popcorn]   Trends FAIL (non-fatal): ' + str(e))
            signals['sources']['google_trends'] = []

        # Calculate strength
        strength = calc_strength(signals)

        signal_cache[pid] = {
            'prediction_id': pid,
            'prediction_name': pred['name'],
            'thesis': pred['thesis'],
            'prediction_text': pred['prediction'],
            'timeframe': pred['timeframe'],
            'date_published': pred['date_published'],
            'signal_strength': strength,
            'raw_signals': signals,
            'collected_at': datetime.utcnow().isoformat(),
        }

        print('[Popcorn] Done: ' + pred['name'] + ' (score: ' + str(strength['overall_score']) + ')')

    cache_loading = False
    cache_loaded = True
    cache_status = 'loaded'
    print('[Popcorn] All predictions loaded. ' + str(len(signal_cache)) + ' cached.')


def calc_strength(signals):
    scores = {}
    total = 0
    count = 0
    sources = signals.get('sources', {})

    if 'google_trends' in sources:
        vels = []
        for tr in sources['google_trends']:
            if isinstance(tr, dict) and tr.get('data') and not tr.get('error'):
                data = tr['data']
                months = sorted(data.keys())
                if len(months) >= 2:
                    v = ((data[months[-1]] - data[months[0]]) / max(data[months[0]], 1)) * 100
                    vels.append(v)
        if vels:
            avg = sum(vels) / len(vels)
            sc = min(100, max(0, avg + 50))
            scores['google_trends'] = {'score': round(sc), 'detail': str(round(avg, 1)) + '% velocity across ' + str(len(vels)) + ' terms'}
            total += sc
            count += 1

    if 'youtube' in sources:
        vids = sum(r.get('video_count', 0) for r in sources['youtube'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, vids * 5)
        scores['youtube'] = {'score': round(sc), 'detail': str(vids) + ' videos found'}
        total += sc
        count += 1

    if 'spotify' in sources:
        pls = sum(r.get('playlist_count', 0) for r in sources['spotify'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, pls * 8)
        scores['spotify'] = {'score': round(sc), 'detail': str(pls) + ' playlists'}
        total += sc
        count += 1

    if 'wikipedia' in sources:
        rising = sum(1 for w in sources['wikipedia'] if isinstance(w, dict) and w.get('trend') == 'rising')
        tot = len([w for w in sources['wikipedia'] if isinstance(w, dict) and not w.get('error')])
        sc = min(100, (rising / max(tot, 1)) * 100)
        scores['wikipedia'] = {'score': round(sc), 'detail': str(rising) + '/' + str(tot) + ' rising'}
        total += sc
        count += 1

    if 'news' in sources:
        arts = sum(r.get('total_results', 0) for r in sources['news'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, arts * 2)
        scores['news'] = {'score': round(sc), 'detail': str(arts) + ' articles'}
        total += sc
        count += 1

    if 'ao3' in sources:
        works = sum(r.get('work_count', 0) for r in sources['ao3'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, (works / 1000) * 10)
        scores['ao3'] = {'score': round(sc), 'detail': str(works) + ' works'}
        total += sc
        count += 1

    if 'tmdb' in sources:
        res = sum(r.get('count', 0) for r in sources['tmdb'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, max(0, 100 - (res * 8)))
        scores['tmdb'] = {'score': round(sc), 'detail': str(res) + ' titles (less = bigger gap)'}
        total += sc
        count += 1

    overall = round(total / max(count, 1))
    return {
        'overall_score': overall,
        'confidence': 'HIGH' if overall >= 70 else ('MODERATE' if overall >= 45 else 'LOW'),
        'sources_used': count,
        'source_scores': scores,
        'interpretation': 'Strong signals.' if overall >= 70 else ('Moderate signals.' if overall >= 45 else 'Early signals.'),
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
        'version': '3.2',
        'cache_status': cache_status,
        'predictions_cached': len(signal_cache),
        'data_sources': {
            'youtube': bool(os.environ.get('YOUTUBE_API_KEY')),
            'spotify': bool(os.environ.get('SPOTIFY_CLIENT_ID')),
            'tmdb': bool(os.environ.get('TMDB_API_KEY')),
            'news': bool(os.environ.get('NEWS_API_KEY')),
            'google_trends': True,
            'wikipedia': True,
            'ao3': True,
        },
    })


@app.route('/api/predictions')
def get_predictions():
    preds = []
    for p in PREDICTIONS:
        cached = signal_cache.get(p['id'])
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
            'signal_score': cached['signal_strength']['overall_score'] if cached else None,
            'data_ready': cached is not None,
        })
    return jsonify({
        'count': len(preds),
        'predictions': preds,
        'cache_status': cache_status,
        'generated_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/predictions/<prediction_id>/signals')
def get_signals(prediction_id):
    # Return cached data INSTANTLY
    if prediction_id in signal_cache:
        return jsonify(signal_cache[prediction_id])

    # Not cached yet
    if cache_loading:
        return jsonify({'error': 'Data is still loading. Try again in 2-3 minutes.', 'status': 'loading'}), 202

    return jsonify({'error': 'No data yet. Trigger a refresh first.', 'status': 'not_loaded'}), 404


@app.route('/api/refresh', methods=['POST'])
def refresh():
    global cache_loading
    if cache_loading:
        return jsonify({'message': 'Already loading.'}), 429
    thread = threading.Thread(target=load_all_signals, daemon=True)
    thread.start()
    return jsonify({'message': 'Refresh started. Check /api/health for status.'})


@app.route('/api/cache/status')
def get_cache_status():
    return jsonify({
        'status': cache_status,
        'loading': cache_loading,
        'loaded': cache_loaded,
        'predictions_cached': list(signal_cache.keys()),
        'count': len(signal_cache),
    })


# Scanner routes
@app.route('/api/scan/youtube')
def scan_yt():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_youtube(q, max_results=10))


@app.route('/api/scan/spotify')
def scan_sp():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_spotify_playlists(q, limit=10))


@app.route('/api/scan/wikipedia')
def scan_wiki():
    articles = request.args.get('articles', '')
    if not articles:
        return jsonify({'error': 'Provide ?articles=A1,A2'}), 400
    arts = [a.strip() for a in articles.split(',') if a.strip()][:5]
    return jsonify({'results': get_wikipedia_batch(arts), 'collected_at': datetime.utcnow().isoformat()})


@app.route('/api/scan/news')
def scan_news_r():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_news(q, days_back=30))


@app.route('/api/scan/news/headlines')
def scan_hl():
    return jsonify(get_entertainment_headlines())


@app.route('/api/scan/ao3')
def scan_ao3():
    tags = request.args.get('tags', '')
    if not tags:
        return jsonify({'error': 'Provide ?tags=T1,T2'}), 400
    tl = [x.strip() for x in tags.split(',') if x.strip()][:5]
    return jsonify({'results': get_ao3_batch(tl), 'collected_at': datetime.utcnow().isoformat()})


@app.route('/api/scan/tmdb/trending')
def scan_tmdb_t():
    return jsonify(get_tmdb_trending(request.args.get('type', 'all'), request.args.get('window', 'week')))


@app.route('/api/scan/tmdb/upcoming')
def scan_tmdb_u():
    return jsonify(get_tmdb_upcoming_movies())


@app.route('/api/scan/books')
def scan_bk():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Provide ?q=term'}), 400
    return jsonify(search_open_library(q))


@app.route('/api/scan/trends')
def scan_tr():
    terms = request.args.get('terms', '')
    if not terms:
        return jsonify({'error': 'Provide ?terms=t1,t2'}), 400
    tl = [x.strip() for x in terms.split(',') if x.strip()][:3]
    return jsonify({'results': get_google_trends_batch(tl), 'collected_at': datetime.utcnow().isoformat()})


# Retroactive proof
@app.route('/api/analyses')
def get_analyses():
    from retroactive import get_all_analyses
    return jsonify(get_all_analyses())


@app.route('/api/analysis/<cid>')
def get_analysis(cid):
    from retroactive import get_all_analyses
    d = get_all_analyses()
    if cid in d:
        return jsonify(d[cid])
    return jsonify({'error': 'Not found'}), 404


# ============================================================
# AUTO-START: Load data in background on first request
# ============================================================
_started = False


@app.before_request
def auto_load():
    global _started
    if not _started and not cache_loading:
        _started = True
        thread = threading.Thread(target=load_all_signals, daemon=True)
        thread.start()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
