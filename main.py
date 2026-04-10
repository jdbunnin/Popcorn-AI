"""
Popcorn AI v4.0 — Auto-Discovery Engine
GPT-4o analyzes signals from 8+ sources and generates
predictions automatically. No human input needed.
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

THE_PROMPT = """You are Popcorn AI, an audience demand intelligence system for the entertainment industry.

I'm giving you raw signals harvested from 8 data sources: YouTube trending videos, YouTube cultural searches, Spotify playlist trends, Wikipedia cultural article traffic, entertainment news headlines, cultural news articles, AO3 fan fiction tag popularity, and TMDB trending/upcoming content.

Your job is to analyze ALL of these signals and identify CULTURAL CURRENTS — underlying psychological themes that connect multiple signals across multiple platforms.

RULES:
1. Only identify currents supported by 3+ INDEPENDENT data sources
2. Focus on AUDIENCE PSYCHOLOGY not content analysis
3. Each current must have a clear ENTERTAINMENT IMPLICATION
4. Be SPECIFIC about what content would satisfy each craving
5. Include a DEMAND GAP — what audiences want that nobody is making
6. Rate confidence based on how many sources converge
7. Compare to historical patterns (pre-Barbie, pre-Squid Game, pre-Bear)

Return a JSON object with this EXACT structure:
{
  "scan_date": "YYYY-MM-DD",
  "total_signals_analyzed": <number>,
  "cultural_currents": [
    {
      "name": "Name of the cultural current",
      "rank": 1,
      "psychological_drive": "The underlying human need driving this",
      "confidence": "HIGH/MODERATE/LOW",
      "convergence_score": <number 1-10>,
      "supporting_sources": ["YouTube", "Spotify", "Wikipedia", etc],
      "source_count": <number>,
      "key_signals": [
        "Specific signal from Source A",
        "Specific signal from Source B",
        "Specific signal from Source C"
      ],
      "audience_size_estimate": "Description of how large the audience is",
      "entertainment_prediction": "Specific prediction about what content will succeed",
      "demand_gap": "What audiences want that nobody is currently making",
      "content_opportunity": "Specific description of the content that would capture this demand",
      "historical_parallel": "Which past hit followed a similar pattern and why",
      "timeframe": "When this demand will peak",
      "what_to_watch": "Specific metrics to monitor to track this current"
    }
  ],
  "meta_analysis": "Overall summary of the cultural moment — what is the dominant psychological state of the American entertainment audience right now?",
  "biggest_gap": "The single largest unserved demand in entertainment right now",
  "collision_alert": "Are any currents converging in a way that resembles pre-Barbie or pre-Squid-Game conditions? If so, describe."
}

Identify 5-8 cultural currents, ranked by confidence and convergence score.

HERE IS THE RAW SIGNAL DATA:

"""


def run_auto_discovery():
    global discovery_cache
    discovery_cache['loading'] = True
    discovery_cache['status'] = 'harvesting signals'
    discovery_cache['error'] = None

    try:
        # Step 1: Harvest all signals
        print('[Popcorn] === AUTO-DISCOVERY STARTING ===')
        raw_signals = harvest_all_signals()
        discovery_cache['raw_signals'] = raw_signals
        discovery_cache['status'] = 'analyzing with GPT-4o'

        # Step 2: Build the prompt with all signal data
        signal_text = json.dumps(raw_signals, indent=2, default=str)

        # Truncate if too long (GPT-4o context limit)
        if len(signal_text) > 50000:
            signal_text = signal_text[:50000] + '\n... [truncated for length]'

        full_prompt = THE_PROMPT + signal_text

        # Step 3: Send to GPT-4o
        print('[Popcorn] Sending to GPT-4o for analysis...')
        analysis = ask_gpt_json(full_prompt, max_tokens=4000)

        if analysis is None:
            discovery_cache['error'] = 'GPT-4o returned no response'
            discovery_cache['status'] = 'error'
            discovery_cache['loading'] = False
            print('[Popcorn] ERROR: GPT returned None')
            return

        # Step 4: Enrich each prediction with live data
        print('[Popcorn] Enriching predictions with source data...')
        discovery_cache['status'] = 'enriching with live data'

        currents = analysis.get('cultural_currents', [])
        enriched_predictions = []

        for current in currents[:8]:
            print('[Popcorn] Enriching: ' + current.get('name', 'Unknown'))

            # Generate search terms from the current
            search_terms = generate_search_terms(current)

            # Pull supporting data
            supporting_data = {}

            # YouTube
            try:
                yt = []
                for term in search_terms[:3]:
                    yt.append(search_youtube(term, max_results=5))
                    t.sleep(0.5)
                supporting_data['youtube'] = yt
            except Exception:
                supporting_data['youtube'] = []

            # Spotify
            try:
                sp = []
                for term in search_terms[:3]:
                    sp.append(search_spotify_playlists(term, limit=5))
                    t.sleep(0.5)
                supporting_data['spotify'] = sp
            except Exception:
                supporting_data['spotify'] = []

            # Wikipedia
            try:
                wiki_terms = [term.replace(' ', '_') for term in search_terms[:3]]
                supporting_data['wikipedia'] = get_wikipedia_batch(wiki_terms)
            except Exception:
                supporting_data['wikipedia'] = []

            # News
            try:
                news = []
                for term in search_terms[:2]:
                    news.append(search_news(term, days_back=30, page_size=5))
                    t.sleep(0.5)
                supporting_data['news'] = news
            except Exception:
                supporting_data['news'] = []

            # Score it
            strength = calc_strength(supporting_data)

            enriched_predictions.append({
                'id': current.get('name', 'unknown').lower().replace(' ', '-').replace('/', '-')[:30],
                'name': current.get('name', 'Unknown Current'),
                'rank': current.get('rank', 0),
                'psychological_drive': current.get('psychological_drive', ''),
                'confidence': current.get('confidence', 'LOW'),
                'convergence_score': current.get('convergence_score', 0),
                'supporting_sources': current.get('supporting_sources', []),
                'source_count': current.get('source_count', 0),
                'key_signals': current.get('key_signals', []),
                'audience_size_estimate': current.get('audience_size_estimate', ''),
                'entertainment_prediction': current.get('entertainment_prediction', ''),
                'demand_gap': current.get('demand_gap', ''),
                'content_opportunity': current.get('content_opportunity', ''),
                'historical_parallel': current.get('historical_parallel', ''),
                'timeframe': current.get('timeframe', ''),
                'what_to_watch': current.get('what_to_watch', ''),
                'signal_strength': strength,
                'supporting_data': supporting_data,
                'search_terms_used': search_terms,
                'generated_at': datetime.utcnow().isoformat(),
            })

        # Step 5: Store everything
        discovery_cache['predictions'] = enriched_predictions
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

        print('[Popcorn] === AUTO-DISCOVERY COMPLETE ===')
        print('[Popcorn] Generated ' + str(len(enriched_predictions)) + ' predictions')

    except Exception as e:
        print('[Popcorn] CRITICAL ERROR: ' + str(e))
        discovery_cache['error'] = str(e)
        discovery_cache['status'] = 'error'
        discovery_cache['loading'] = False


def generate_search_terms(current):
    name = current.get('name', '')
    drive = current.get('psychological_drive', '')
    gap = current.get('demand_gap', '')
    opportunity = current.get('content_opportunity', '')

    terms = set()

    for text in [name, drive, gap, opportunity]:
        words = text.lower().replace(',', ' ').replace('.', ' ').replace('/', ' ').split()
        # Extract 2-3 word phrases
        for i in range(len(words)):
            if i < len(words) - 1:
                phrase = words[i] + ' ' + words[i + 1]
                if len(phrase) > 5 and len(phrase) < 40:
                    terms.add(phrase)
            if i < len(words) - 2:
                phrase = words[i] + ' ' + words[i + 1] + ' ' + words[i + 2]
                if len(phrase) > 8 and len(phrase) < 40:
                    terms.add(phrase)

    # Add the name itself
    terms.add(name.lower())

    # Filter out garbage
    stop_words = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'are', 'but', 'not', 'has', 'have', 'will', 'about'}
    filtered = []
    for term in terms:
        words = term.split()
        if not all(w in stop_words for w in words):
            filtered.append(term)

    return filtered[:10]


def calc_strength(sources):
    scores = {}
    total = 0
    count = 0

    if 'youtube' in sources:
        vids = sum(r.get('video_count', 0) for r in sources['youtube'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, vids * 4)
        scores['youtube'] = {'score': round(sc), 'detail': str(vids) + ' videos'}
        total += sc
        count += 1

    if 'spotify' in sources:
        pls = sum(r.get('playlist_count', 0) for r in sources['spotify'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, pls * 6)
        scores['spotify'] = {'score': round(sc), 'detail': str(pls) + ' playlists'}
        total += sc
        count += 1

    if 'wikipedia' in sources:
        rising = sum(1 for w in sources['wikipedia'] if isinstance(w, dict) and w.get('trend') == 'rising')
        tot = len([w for w in sources['wikipedia'] if isinstance(w, dict) and not w.get('error')])
        total_views = sum(w.get('daily_average', 0) for w in sources['wikipedia'] if isinstance(w, dict) and not w.get('error'))
        sc = min(100, max((rising / max(tot, 1)) * 60, min(total_views / 50, 40)))
        scores['wikipedia'] = {'score': round(sc), 'detail': str(rising) + '/' + str(tot) + ' rising, ' + str(total_views) + ' daily views'}
        total += sc
        count += 1

    if 'news' in sources:
        arts = sum(r.get('total_results', 0) for r in sources['news'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, arts)
        scores['news'] = {'score': round(sc), 'detail': str(arts) + ' articles'}
        total += sc
        count += 1

    overall = round(total / max(count, 1))
    return {
        'overall_score': overall,
        'confidence': 'HIGH' if overall >= 65 else ('MODERATE' if overall >= 40 else 'LOW'),
        'sources_used': count,
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
        'version': '4.0 — Auto-Discovery',
        'discovery_status': discovery_cache['status'],
        'predictions_generated': len(discovery_cache['predictions']),
        'last_run': discovery_cache['last_run'],
        'error': discovery_cache['error'],
        'data_sources': {
            'youtube': bool(os.environ.get('YOUTUBE_API_KEY')),
            'spotify': bool(os.environ.get('SPOTIFY_CLIENT_ID')),
            'tmdb': bool(os.environ.get('TMDB_API_KEY')),
            'news': bool(os.environ.get('NEWS_API_KEY')),
            'openai': bool(os.environ.get('OPENAI_API_KEY')),
            'google_trends': True,
            'wikipedia': True,
            'ao3': True,
        },
    })


@app.route('/api/discover', methods=['POST'])
def trigger_discovery():
    if discovery_cache['loading']:
        return jsonify({'message': 'Already running. Check /api/health for status.'}), 429
    thread = threading.Thread(target=run_auto_discovery, daemon=True)
    thread.start()
    return jsonify({'message': 'Auto-discovery started. This takes 5-10 minutes. Check /api/health for status.'})


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
            'entertainment_prediction': p['entertainment_prediction'],
            'demand_gap': p['demand_gap'],
            'timeframe': p['timeframe'],
            'signal_score': p['signal_strength']['overall_score'],
            'generated_at': p['generated_at'],
        })

    return jsonify({
        'count': len(preds),
        'predictions': preds,
        'analysis': discovery_cache.get('analysis'),
        'status': discovery_cache['status'],
        'last_run': discovery_cache['last_run'],
        'generated_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/predictions/<prediction_id>')
def get_prediction_detail(prediction_id):
    for p in discovery_cache['predictions']:
        if p['id'] == prediction_id:
            return jsonify(p)
    return jsonify({'error': 'Not found. Run /api/discover first.'}), 404


@app.route('/api/raw-signals')
def get_raw_signals():
    return jsonify(discovery_cache.get('raw_signals', {}))


# Scanner routes (keep these for manual exploration)
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
# AUTO-START on first visit
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
