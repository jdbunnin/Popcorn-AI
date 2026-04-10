"""
Popcorn AI v4.1 — Precision Engine
More data. Sharper predictions. Better scoring.
"""

from flask import Flask, jsonify, send_from_directory, request
import os
import json
import threading
import time as t
from datetime import datetime
from data_collectors import (
    harvest_all_signals,
    ask_gpt_json,
    search_youtube,
    search_spotify_playlists,
    get_wikipedia_batch,
    search_news,
    get_ao3_batch,
    search_tmdb,
    get_google_trends,
    get_google_trends_batch,
    get_youtube_trending_by_category,
    get_tmdb_trending,
    get_tmdb_upcoming_movies,
    get_entertainment_headlines,
    search_open_library,
)

app = Flask(__name__, static_folder='public', static_url_path='')

# ============================================================
# STATE
# ============================================================
discovery_cache = {
    'predictions': [],
    'raw_signals': {},
    'analysis': None,
    'status': 'not started',
    'loading': False,
    'last_run': None,
    'error': None,
}

# ============================================================
# THE PROMPT — This is the brain
# ============================================================
DISCOVERY_PROMPT = """You are Popcorn AI, the world's most precise audience demand intelligence system for entertainment.

I'm giving you raw signals from 8 data sources. Your job is to find SPECIFIC, ACTIONABLE cultural currents.

CRITICAL RULES:
1. Be EXTREMELY SPECIFIC. Not "people want authentic content." Instead: "Women 25-38 are craving a workplace drama set in healthcare that depicts burnout with dark humor — similar to how Scrubs depicted hospital life but with the tonal intensity of The Bear."
2. Every prediction must name a SPECIFIC format (series, film, limited series, documentary), SPECIFIC tone (dark comedy, prestige drama, light adventure), and SPECIFIC target demographic.
3. Identify the EXACT demand gap — what audiences are searching for that ZERO current or announced content satisfies.
4. Each current must be supported by signals from AT LEAST 3 different data sources.
5. Rate convergence 1-10 where 10 means "this is pre-Barbie level convergence across every source."
6. For each current, provide 8-12 specific search terms that would validate the demand.
7. Name specific shows, films, or creators that partially satisfy this demand but don't fully capture it.
8. Estimate audience size in millions of US adults.

THINK LIKE A STUDIO HEAD WHO NEEDS TO GREENLIGHT A SPECIFIC PROJECT TOMORROW.

Return JSON:
{
  "scan_date": "YYYY-MM-DD",
  "total_signals_analyzed": <number>,
  "cultural_currents": [
    {
      "name": "Highly specific name",
      "rank": 1,
      "psychological_drive": "The exact human need — be specific about WHO feels it and WHY",
      "confidence": "HIGH/MODERATE/LOW",
      "convergence_score": <1-10>,
      "supporting_sources": ["YouTube", "Spotify", etc],
      "source_count": <number>,
      "key_signals": [
        "SPECIFIC signal with numbers: 'YouTube videos about X average 2M views in 30 days'",
        "SPECIFIC signal: 'Spotify playlists tagged X grew from 50 to 200 in 6 months'",
        "At least 6 specific signals with data"
      ],
      "target_demographic": "Exact age, gender, psychographic profile",
      "audience_size_millions": <number>,
      "format_recommendation": "8-episode limited series / feature film / docuseries / etc",
      "tone_and_style": "Specific tone: 'dark comedy with warm core, like Fleabag meets workplace drama'",
      "entertainment_prediction": "SPECIFIC: 'A [format] about [specific subject] targeting [specific audience] with [specific tone] will [specific outcome] within [timeframe]'",
      "demand_gap": "EXACTLY what is missing — name existing content that comes close but doesn't fully satisfy",
      "content_opportunity": "The EXACT show/film that should be made — describe it like a one-paragraph pitch",
      "comparable_successes": ["Show A succeeded because...", "Film B captured similar demand by..."],
      "historical_parallel": "Which past pattern this resembles and why",
      "search_terms_to_track": ["term1", "term2", "term3", "at least 8 terms"],
      "timeframe": "Specific: '6-9 months' not just 'soon'",
      "risk_factors": ["What could prevent this from materializing"],
      "what_to_watch": "Specific metrics and thresholds: 'If X search volume crosses Y, demand is confirmed'"
    }
  ],
  "meta_analysis": "2-3 paragraph analysis of the OVERALL cultural moment. What is the dominant psychological state? What macro forces are shaping entertainment demand? Be specific and insightful, not generic.",
  "biggest_gap": "The single most valuable unserved demand. Describe the EXACT content that would fill it. Be so specific a producer could start developing it tomorrow.",
  "collision_alert": "Are 3+ currents converging like pre-Barbie (nostalgia + aesthetic + feminist + communal) or pre-Squid-Game (economic anxiety + K-culture + survival + shared moment)? If yes, this is the most important finding. Describe it in detail with the specific content opportunity at the center."
}

Generate 6-8 currents ranked by specificity and actionability. I'd rather have 4 razor-sharp predictions than 8 vague ones.

RAW SIGNAL DATA:

"""


def run_auto_discovery():
    global discovery_cache
    discovery_cache['loading'] = True
    discovery_cache['status'] = 'harvesting signals'
    discovery_cache['error'] = None

    try:
        print('[Popcorn] === DISCOVERY v4.1 STARTING ===')
        raw_signals = harvest_all_signals()
        discovery_cache['raw_signals'] = raw_signals
        discovery_cache['status'] = 'analyzing with GPT-4o'

        signal_text = json.dumps(raw_signals, indent=2, default=str)
        if len(signal_text) > 60000:
            signal_text = signal_text[:60000] + '\n...[truncated]'

        print('[Popcorn] Sending ' + str(len(signal_text)) + ' chars to GPT-4o...')
        analysis = ask_gpt_json(DISCOVERY_PROMPT + signal_text, max_tokens=4096)

        if analysis is None:
            discovery_cache['error'] = 'GPT-4o returned no response'
            discovery_cache['status'] = 'error'
            discovery_cache['loading'] = False
            return

        print('[Popcorn] GPT analysis received. Enriching predictions...')
        discovery_cache['status'] = 'enriching with live data'

        currents = analysis.get('cultural_currents', [])
        enriched = []

        for current in currents[:8]:
            name = current.get('name', 'Unknown')
            print('[Popcorn] Enriching: ' + name)

            # Use GPT-provided search terms
            search_terms = current.get('search_terms_to_track', [])
            if not search_terms:
                search_terms = generate_search_terms(current)

            # Pull HEAVY data from each source
            supporting = {}

            # YouTube — 5 searches × 10 results = up to 50 videos
            try:
                yt = []
                for term in search_terms[:5]:
                    result = search_youtube(term, max_results=10)
                    yt.append(result)
                    t.sleep(0.5)
                supporting['youtube'] = yt
                total_vids = sum(r.get('video_count', 0) for r in yt if not r.get('error'))
                print('[Popcorn]   YouTube: ' + str(total_vids) + ' videos')
            except Exception as e:
                print('[Popcorn]   YouTube FAIL: ' + str(e))
                supporting['youtube'] = []

            # Spotify — 5 searches × 10 playlists = up to 50 playlists
            try:
                sp = []
                for term in search_terms[:5]:
                    result = search_spotify_playlists(term, limit=10)
                    sp.append(result)
                    t.sleep(0.5)
                supporting['spotify'] = sp
                total_pl = sum(r.get('playlist_count', 0) for r in sp if not r.get('error'))
                print('[Popcorn]   Spotify: ' + str(total_pl) + ' playlists')
            except Exception as e:
                print('[Popcorn]   Spotify FAIL: ' + str(e))
                supporting['spotify'] = []

            # Wikipedia — up to 8 articles
            try:
                wiki_terms = []
                for term in search_terms[:8]:
                    wiki_terms.append(term.replace(' ', '_').title())
                supporting['wikipedia'] = get_wikipedia_batch(wiki_terms)
                valid = [w for w in supporting['wikipedia'] if not w.get('error')]
                print('[Popcorn]   Wikipedia: ' + str(len(valid)) + ' articles')
            except Exception as e:
                print('[Popcorn]   Wikipedia FAIL: ' + str(e))
                supporting['wikipedia'] = []

            # News — 5 searches × 10 articles = up to 50 articles
            try:
                news = []
                for term in search_terms[:5]:
                    result = search_news(term, days_back=30, page_size=10)
                    news.append(result)
                    t.sleep(0.5)
                supporting['news'] = news
                total_arts = sum(r.get('total_results', 0) for r in news if not r.get('error'))
                print('[Popcorn]   News: ' + str(total_arts) + ' articles')
            except Exception as e:
                print('[Popcorn]   News FAIL: ' + str(e))
                supporting['news'] = []

            # AO3 — up to 6 tags
            try:
                ao3_tags = search_terms[:6]
                supporting['ao3'] = get_ao3_batch(ao3_tags)
                total_works = sum(r.get('work_count', 0) for r in supporting['ao3'] if not r.get('error'))
                print('[Popcorn]   AO3: ' + str(total_works) + ' works')
            except Exception as e:
                print('[Popcorn]   AO3 FAIL: ' + str(e))
                supporting['ao3'] = []

            # TMDB — 3 searches
            try:
                tmdb = []
                for term in search_terms[:3]:
                    tmdb.append(search_tmdb(term))
                    t.sleep(0.3)
                supporting['tmdb'] = tmdb
                print('[Popcorn]   TMDB: OK')
            except Exception as e:
                print('[Popcorn]   TMDB FAIL: ' + str(e))
                supporting['tmdb'] = []

            # Books — 3 searches
            try:
                books = []
                for term in search_terms[:3]:
                    books.append(search_open_library(term))
                    t.sleep(0.3)
                supporting['books'] = books
                print('[Popcorn]   Books: OK')
            except Exception as e:
                supporting['books'] = []

            strength = calc_strength(supporting)

            enriched.append({
                'id': name.lower().replace(' ', '-').replace('/', '-').replace("'", '')[:40],
                'name': name,
                'rank': current.get('rank', 0),
                'psychological_drive': current.get('psychological_drive', ''),
                'confidence': current.get('confidence', 'LOW'),
                'convergence_score': current.get('convergence_score', 0),
                'supporting_sources': current.get('supporting_sources', []),
                'source_count': current.get('source_count', 0),
                'key_signals': current.get('key_signals', []),
                'target_demographic': current.get('target_demographic', ''),
                'audience_size_millions': current.get('audience_size_millions', 0),
                'format_recommendation': current.get('format_recommendation', ''),
                'tone_and_style': current.get('tone_and_style', ''),
                'entertainment_prediction': current.get('entertainment_prediction', ''),
                'demand_gap': current.get('demand_gap', ''),
                'content_opportunity': current.get('content_opportunity', ''),
                'comparable_successes': current.get('comparable_successes', []),
                'historical_parallel': current.get('historical_parallel', ''),
                'risk_factors': current.get('risk_factors', []),
                'what_to_watch': current.get('what_to_watch', ''),
                'timeframe': current.get('timeframe', ''),
                'search_terms_used': search_terms,
                'signal_strength': strength,
                'supporting_data': supporting,
                'generated_at': datetime.utcnow().isoformat(),
            })

            print('[Popcorn] Done: ' + name + ' (score: ' + str(strength['overall_score']) + ')')

        discovery_cache['predictions'] = enriched
        discovery_cache['analysis'] = {
            'meta_analysis': analysis.get('meta_analysis', ''),
            'biggest_gap': analysis.get('biggest_gap', ''),
            'collision_alert': analysis.get('collision_alert', ''),
            'total_signals': analysis.get('total_signals_analyzed', 0),
            'scan_date': analysis.get('scan_date', datetime.utcnow().strftime('%Y-%m-%d')),
        }
        discovery_cache['status'] = 'loaded'
        discovery_cache['last_run'] = datetime.utcnow().isoformat()
        discovery_cache['loading'] = False

        print('[Popcorn] === DISCOVERY COMPLETE: ' + str(len(enriched)) + ' predictions ===')

    except Exception as e:
        print('[Popcorn] CRITICAL ERROR: ' + str(e))
        import traceback
        traceback.print_exc()
        discovery_cache['error'] = str(e)
        discovery_cache['status'] = 'error'
        discovery_cache['loading'] = False


def generate_search_terms(current):
    terms = set()
    for text in [current.get('name', ''), current.get('psychological_drive', ''), current.get('demand_gap', ''), current.get('content_opportunity', '')]:
        words = text.lower().replace(',', ' ').replace('.', ' ').split()
        for i in range(len(words)):
            if i < len(words) - 1:
                phrase = words[i] + ' ' + words[i+1]
                if 5 < len(phrase) < 40:
                    terms.add(phrase)
            if i < len(words) - 2:
                phrase = words[i] + ' ' + words[i+1] + ' ' + words[i+2]
                if 8 < len(phrase) < 40:
                    terms.add(phrase)
    terms.add(current.get('name', 'unknown').lower())
    stop = {'the','and','for','that','this','with','from','are','but','not','has','will','about','their','they','been','have','into','more','than','what','when','who','how'}
    filtered = [term for term in terms if not all(w in stop for w in term.split())]
    return filtered[:12]


def calc_strength(sources):
    scores = {}
    total = 0
    count = 0

    # YouTube — scale: 50 videos = 100
    if 'youtube' in sources:
        vids = sum(r.get('video_count', 0) for r in sources['youtube'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, vids * 2)
        scores['youtube'] = {'score': round(sc), 'detail': str(vids) + ' videos across ' + str(len(sources['youtube'])) + ' searches', 'raw_count': vids}
        total += sc
        count += 1

    # Spotify — scale: 50 playlists = 100
    if 'spotify' in sources:
        pls = sum(r.get('playlist_count', 0) for r in sources['spotify'] if isinstance(r, dict) and not r.get('error'))
        total_tracks = sum(sum(p.get('tracks', 0) for p in r.get('playlists', [])) for r in sources['spotify'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, pls * 2)
        scores['spotify'] = {'score': round(sc), 'detail': str(pls) + ' playlists, ' + str(total_tracks) + ' total tracks', 'raw_count': pls}
        total += sc
        count += 1

    # Wikipedia — combine volume AND trend
    if 'wikipedia' in sources:
        valid = [w for w in sources['wikipedia'] if isinstance(w, dict) and not w.get('error')]
        rising = sum(1 for w in valid if w.get('trend') == 'rising')
        total_daily = sum(w.get('daily_average', 0) for w in valid)
        vol_score = min(50, total_daily / 20)
        trend_score = min(50, (rising / max(len(valid), 1)) * 50) if valid else 0
        sc = vol_score + trend_score
        scores['wikipedia'] = {'score': round(sc), 'detail': str(len(valid)) + ' articles, ' + str(rising) + ' rising, ' + str(total_daily) + ' daily views', 'raw_count': total_daily}
        total += sc
        count += 1

    # News — scale: 100 articles = 100
    if 'news' in sources:
        arts = sum(r.get('total_results', 0) for r in sources['news'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, arts)
        scores['news'] = {'score': round(sc), 'detail': str(arts) + ' articles in last 30 days', 'raw_count': arts}
        total += sc
        count += 1

    # AO3 — scale: 10K works = 100
    if 'ao3' in sources:
        works = sum(r.get('work_count', 0) for r in sources['ao3'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, works / 100)
        scores['ao3'] = {'score': round(sc), 'detail': str(works) + ' fan works', 'raw_count': works}
        total += sc
        count += 1

    # TMDB — INVERSE: less supply = higher score
    if 'tmdb' in sources:
        res = sum(r.get('count', 0) for r in sources['tmdb'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, max(0, 100 - (res * 5)))
        scores['tmdb'] = {'score': round(sc), 'detail': str(res) + ' existing titles (fewer = bigger gap)', 'raw_count': res}
        total += sc
        count += 1

    # Books
    if 'books' in sources:
        bks = sum(r.get('total_found', 0) for r in sources['books'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, bks / 10)
        scores['books'] = {'score': round(sc), 'detail': str(bks) + ' related books', 'raw_count': bks}
        total += sc
        count += 1

    overall = round(total / max(count, 1))

    return {
        'overall_score': overall,
        'confidence': 'HIGH' if overall >= 65 else ('MODERATE' if overall >= 40 else 'LOW'),
        'sources_used': count,
        'total_data_points': sum(s.get('raw_count', 0) for s in scores.values()),
        'source_scores': scores,
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
        'version': '4.1 — Precision Engine',
        'discovery_status': discovery_cache['status'],
        'predictions_generated': len(discovery_cache['predictions']),
        'last_run': discovery_cache['last_run'],
        'error': discovery_cache['error'],
        'data_sources': {
            'openai': bool(os.environ.get('OPENAI_API_KEY')),
            'youtube': bool(os.environ.get('YOUTUBE_API_KEY')),
            'spotify': bool(os.environ.get('SPOTIFY_CLIENT_ID')),
            'tmdb': bool(os.environ.get('TMDB_API_KEY')),
            'news': bool(os.environ.get('NEWS_API_KEY')),
            'wikipedia': True,
            'ao3': True,
            'open_library': True,
        },
    })


@app.route('/api/discover', methods=['POST'])
def trigger_discovery():
    if discovery_cache['loading']:
        return jsonify({'message': 'Already running.'}), 429
    thread = threading.Thread(target=run_auto_discovery, daemon=True)
    thread.start()
    return jsonify({'message': 'Discovery started. Takes 8-15 minutes.'})


@app.route('/api/predictions')
def get_predictions():
    preds = []
    for p in discovery_cache['predictions']:
        preds.append({
            'id': p['id'],
            'name': p['name'],
            'rank': p['rank'],
            'psychological_drive': p['psychological_drive'],
            'confidence': p['confidence'],
            'convergence_score': p['convergence_score'],
            'source_count': p['source_count'],
            'target_demographic': p.get('target_demographic', ''),
            'audience_size_millions': p.get('audience_size_millions', 0),
            'format_recommendation': p.get('format_recommendation', ''),
            'tone_and_style': p.get('tone_and_style', ''),
            'entertainment_prediction': p['entertainment_prediction'],
            'demand_gap': p['demand_gap'],
            'timeframe': p['timeframe'],
            'signal_score': p['signal_strength']['overall_score'],
            'total_data_points': p['signal_strength'].get('total_data_points', 0),
            'generated_at': p['generated_at'],
        })
    return jsonify({
        'count': len(preds),
        'predictions': preds,
        'analysis': discovery_cache.get('analysis'),
        'status': discovery_cache['status'],
        'last_run': discovery_cache['last_run'],
    })


@app.route('/api/predictions/<pid>')
def get_prediction(pid):
    for p in discovery_cache['predictions']:
        if p['id'] == pid:
            return jsonify(p)
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/raw-signals')
def raw_signals():
    return jsonify(discovery_cache.get('raw_signals', {}))


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
    a = request.args.get('articles', '')
    if not a:
        return jsonify({'error': 'Provide ?articles=A1,A2'}), 400
    arts = [x.strip() for x in a.split(',') if x.strip()][:5]
    return jsonify({'results': get_wikipedia_batch(arts)})


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
    return jsonify({'results': get_ao3_batch(tl)})


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
    return jsonify({'results': get_google_trends_batch(tl)})


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
# AUTO-START
# ============================================================
_started = False


@app.before_request
def auto_start():
    global _started
    if not _started and not discovery_cache['loading']:
        _started = True
        thread = threading.Thread(target=run_auto_discovery, daemon=True)
        thread.start()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
