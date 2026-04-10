"""
Popcorn AI v4.2 — Precision + Honesty
Data-driven scores override GPT self-assessment.
More data per source. Better scoring.
"""

from flask import Flask, jsonify, send_from_directory, request
import os
import json
import threading
import time as t
import traceback
from datetime import datetime
from data_collectors import (
    harvest_all_signals,
    ask_gpt_json,
    search_youtube,
    search_spotify_playlists,
    get_wikipedia_batch,
    get_wikipedia_pageviews,
    search_news,
    get_ao3_batch,
    get_ao3_tag_count,
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
cache = {
    'predictions': [],
    'analysis': None,
    'raw_signals': {},
    'status': 'not started',
    'loading': False,
    'last_run': None,
    'error': None,
}

# ============================================================
# GPT PROMPT
# ============================================================
PROMPT = """You are Popcorn AI, the world's most precise audience demand intelligence system.

Analyze these raw signals from 8 sources and identify SPECIFIC cultural currents.

RULES:
1. Be EXTREMELY SPECIFIC. Not "people want authentic content." Instead: "Women 25-38 are craving a workplace drama set in healthcare that depicts burnout with dark humor — Scrubs meets The Bear meets Fleabag."
2. Every prediction must specify FORMAT (8-ep series, film, docuseries), TONE (dark comedy, prestige drama), and TARGET DEMOGRAPHIC (age, gender, psychographic).
3. Identify the EXACT demand gap — what audiences search for that NO current content satisfies.
4. Each current needs support from 3+ different sources in the data I provide.
5. Provide 10-15 specific search terms per current that I can use to pull validation data from YouTube, Spotify, Wikipedia, and News.
6. Name SPECIFIC existing shows/films that partially satisfy this demand but miss something.
7. Estimate audience in millions of US adults.
8. Generate 6-8 currents. I want SHARP predictions, not vague ones.
9. For convergence_score: be HONEST. Only rate 8+ if you see strong signals in 6+ of my data sources. Rate 5-7 if you see it in 3-5 sources. Rate 1-4 if only 1-2 sources.
10. For confidence: only say HIGH if the data CLEARLY supports it across multiple sources. MODERATE if it's emerging. LOW if speculative.

Return JSON:
{
  "scan_date": "YYYY-MM-DD",
  "total_signals_analyzed": <count every data point I gave you>,
  "cultural_currents": [
    {
      "name": "Specific descriptive name",
      "rank": 1,
      "psychological_drive": "WHO feels this need, WHY they feel it, and WHAT triggers it — be specific about demographics and life circumstances",
      "confidence": "HIGH/MODERATE/LOW — based on DATA not your gut",
      "convergence_score": <1-10 honestly based on how many of MY sources show this>,
      "supporting_sources": ["list only sources where you SAW relevant signals"],
      "source_count": <actual count of sources with signals>,
      "key_signals": [
        "Quote or reference SPECIFIC data points from my input",
        "Include numbers where possible",
        "At least 8 specific signals"
      ],
      "target_demographic": "Age range, gender skew, psychographic traits, lifestyle markers",
      "audience_size_millions": <realistic number>,
      "format_recommendation": "Specific format with episode count or runtime",
      "tone_and_style": "Reference 2-3 existing shows/films for tone comparison",
      "entertainment_prediction": "SPECIFIC: A [format] about [subject] targeting [audience] in the style of [comparable] will [outcome] within [months]",
      "demand_gap": "Name existing content that comes CLOSE and explain what it's MISSING",
      "content_opportunity": "One-paragraph pitch — specific enough to greenlight",
      "comparable_successes": ["Show A succeeded because X", "Film B captured Y"],
      "historical_parallel": "Which pre-hit pattern this resembles",
      "search_terms_to_track": ["term1", "term2", "at least 10 specific trackable terms"],
      "risk_factors": ["Specific risks, not generic ones"],
      "timeframe": "Specific months range",
      "what_to_watch": "Specific metrics and thresholds to monitor"
    }
  ],
  "meta_analysis": "3-paragraph analysis of the overall cultural moment. Be insightful and specific. Reference the actual data I gave you.",
  "biggest_gap": "The single most valuable unserved demand. Describe the EXACT content. Be specific enough that a producer starts developing it tomorrow.",
  "collision_alert": "Are 3+ currents converging like pre-Barbie or pre-Squid-Game? Only say yes if the data supports it. If not, say 'No collision detected at this time' — that's fine."
}

RAW SIGNALS:

"""


# ============================================================
# DISCOVERY ENGINE
# ============================================================
def run_discovery():
    global cache
    cache['loading'] = True
    cache['status'] = 'harvesting signals from 8 sources'
    cache['error'] = None

    try:
        print('[Popcorn] ========== DISCOVERY v4.2 ==========')

        # Step 1: Harvest
        print('[Popcorn] Step 1: Harvesting all signals...')
        raw = harvest_all_signals()
        cache['raw_signals'] = raw
        cache['status'] = 'sending to GPT-4o for analysis'

        # Count total signals
        total_signals = 0
        for key, val in raw.items():
            if isinstance(val, list):
                total_signals += len(val)
            elif isinstance(val, dict):
                for k2, v2 in val.items():
                    if isinstance(v2, list):
                        total_signals += len(v2)
        print('[Popcorn] Total raw signals: ' + str(total_signals))

        # Step 2: GPT Analysis
        signal_json = json.dumps(raw, indent=1, default=str)
        if len(signal_json) > 60000:
            signal_json = signal_json[:60000] + '\n...[truncated]'

        print('[Popcorn] Step 2: GPT-4o analyzing ' + str(len(signal_json)) + ' chars...')
        analysis = ask_gpt_json(PROMPT + signal_json, max_tokens=4096)

        if not analysis:
            cache['error'] = 'GPT-4o returned nothing'
            cache['status'] = 'error'
            cache['loading'] = False
            print('[Popcorn] ERROR: No GPT response')
            return

        currents = analysis.get('cultural_currents', [])
        print('[Popcorn] GPT found ' + str(len(currents)) + ' currents')

        # Step 3: Enrich each prediction with HEAVY data
        cache['status'] = 'enriching predictions with live data'
        enriched = []

        for i, current in enumerate(currents[:8]):
            name = current.get('name', 'Unknown')
            print('[Popcorn] --- Enriching ' + str(i+1) + '/' + str(len(currents)) + ': ' + name + ' ---')

            # Get search terms from GPT or generate them
            terms = current.get('search_terms_to_track', [])
            if len(terms) < 5:
                terms = terms + make_terms(current)
            terms = terms[:12]
            print('[Popcorn]   Search terms: ' + str(len(terms)))

            data = {}
            source_count = 0

            # YOUTUBE — 5 searches × 10 results
            try:
                yt = []
                for term in terms[:5]:
                    r = search_youtube(term, max_results=10)
                    if not r.get('error'):
                        yt.append(r)
                    t.sleep(0.5)
                data['youtube'] = yt
                vid_count = sum(r.get('video_count', 0) for r in yt)
                if vid_count > 0:
                    source_count += 1
                print('[Popcorn]   YouTube: ' + str(vid_count) + ' videos ✓')
            except Exception as e:
                print('[Popcorn]   YouTube: FAIL - ' + str(e))
                data['youtube'] = []

            # SPOTIFY — 5 searches × 10 playlists
            try:
                sp = []
                for term in terms[:5]:
                    r = search_spotify_playlists(term, limit=10)
                    if not r.get('error'):
                        sp.append(r)
                    t.sleep(0.5)
                data['spotify'] = sp
                pl_count = sum(r.get('playlist_count', 0) for r in sp)
                if pl_count > 0:
                    source_count += 1
                print('[Popcorn]   Spotify: ' + str(pl_count) + ' playlists ✓')
            except Exception as e:
                print('[Popcorn]   Spotify: FAIL - ' + str(e))
                data['spotify'] = []

            # WIKIPEDIA — up to 8 articles
            try:
                wiki_terms = []
                for term in terms[:8]:
                    clean = term.strip().replace(' ', '_')
                    clean = clean[0].upper() + clean[1:] if clean else clean
                    wiki_terms.append(clean)
                wiki = get_wikipedia_batch(wiki_terms)
                data['wikipedia'] = wiki
                valid_wiki = [w for w in wiki if isinstance(w, dict) and not w.get('error') and w.get('total_views', 0) > 0]
                if len(valid_wiki) > 0:
                    source_count += 1
                print('[Popcorn]   Wikipedia: ' + str(len(valid_wiki)) + ' articles ✓')
            except Exception as e:
                print('[Popcorn]   Wikipedia: FAIL - ' + str(e))
                data['wikipedia'] = []

            # NEWS — 5 searches × 10 results
            try:
                news = []
                for term in terms[:5]:
                    r = search_news(term, days_back=30, page_size=10)
                    if not r.get('error'):
                        news.append(r)
                    t.sleep(0.5)
                data['news'] = news
                art_count = sum(r.get('total_results', 0) for r in news)
                if art_count > 0:
                    source_count += 1
                print('[Popcorn]   News: ' + str(art_count) + ' articles ✓')
            except Exception as e:
                print('[Popcorn]   News: FAIL - ' + str(e))
                data['news'] = []

            # AO3 — up to 6 tags
            try:
                ao3_terms = terms[:6]
                ao3 = get_ao3_batch(ao3_terms)
                data['ao3'] = ao3
                work_count = sum(r.get('work_count', 0) for r in ao3 if isinstance(r, dict) and not r.get('error'))
                if work_count > 0:
                    source_count += 1
                print('[Popcorn]   AO3: ' + str(work_count) + ' works ✓')
            except Exception as e:
                print('[Popcorn]   AO3: FAIL - ' + str(e))
                data['ao3'] = []

            # TMDB — 3 searches
            try:
                tmdb = []
                for term in terms[:3]:
                    r = search_tmdb(term)
                    if not r.get('error'):
                        tmdb.append(r)
                    t.sleep(0.3)
                data['tmdb'] = tmdb
                tmdb_count = sum(r.get('count', 0) for r in tmdb)
                source_count += 1  # TMDB always counts (inverse scoring)
                print('[Popcorn]   TMDB: ' + str(tmdb_count) + ' titles ✓')
            except Exception as e:
                print('[Popcorn]   TMDB: FAIL - ' + str(e))
                data['tmdb'] = []

            # BOOKS — 3 searches
            try:
                books = []
                for term in terms[:3]:
                    r = search_open_library(term)
                    if not r.get('error'):
                        books.append(r)
                    t.sleep(0.3)
                data['books'] = books
                book_count = sum(r.get('total_found', 0) for r in books)
                if book_count > 0:
                    source_count += 1
                print('[Popcorn]   Books: ' + str(book_count) + ' found ✓')
            except Exception as e:
                print('[Popcorn]   Books: FAIL - ' + str(e))
                data['books'] = []

            # Calculate REAL scores
            strength = score_sources(data)

            # Override GPT confidence with data-driven confidence
            real_confidence = strength['confidence']
            real_convergence = source_count

            print('[Popcorn]   Score: ' + str(strength['overall_score']) + ' | Sources: ' + str(source_count) + ' | Confidence: ' + real_confidence)

            enriched.append({
                'id': name.lower().replace(' ', '-').replace('/', '-').replace("'", '').replace('"', '').replace(':', '')[:40],
                'name': name,
                'rank': current.get('rank', i + 1),
                'psychological_drive': current.get('psychological_drive', ''),
                'confidence': real_confidence,
                'convergence_score': real_convergence,
                'source_count': source_count,
                'gpt_confidence': current.get('confidence', ''),
                'gpt_convergence': current.get('convergence_score', 0),
                'supporting_sources': current.get('supporting_sources', []),
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
                'search_terms_used': terms,
                'signal_strength': strength,
                'supporting_data': data,
                'generated_at': datetime.utcnow().isoformat(),
            })

        # Sort by signal score
        enriched.sort(key=lambda x: x['signal_strength']['overall_score'], reverse=True)

        # Re-rank after sorting
        for i, p in enumerate(enriched):
            p['rank'] = i + 1

        cache['predictions'] = enriched
        cache['analysis'] = {
            'meta_analysis': analysis.get('meta_analysis', ''),
            'biggest_gap': analysis.get('biggest_gap', ''),
            'collision_alert': analysis.get('collision_alert', ''),
            'total_signals': total_signals,
            'scan_date': analysis.get('scan_date', datetime.utcnow().strftime('%Y-%m-%d')),
            'predictions_count': len(enriched),
        }
        cache['status'] = 'loaded'
        cache['last_run'] = datetime.utcnow().isoformat()
        cache['loading'] = False

        print('[Popcorn] ========== COMPLETE: ' + str(len(enriched)) + ' predictions ==========')

    except Exception as e:
        print('[Popcorn] CRITICAL: ' + str(e))
        traceback.print_exc()
        cache['error'] = str(e)
        cache['status'] = 'error'
        cache['loading'] = False


def make_terms(current):
    terms = set()
    texts = [current.get('name', ''), current.get('psychological_drive', ''), current.get('demand_gap', ''), current.get('content_opportunity', '')]
    for text in texts:
        words = text.lower().replace(',', ' ').replace('.', ' ').replace('"', ' ').replace("'", ' ').split()
        for i in range(len(words)):
            if i < len(words) - 1:
                p = words[i] + ' ' + words[i+1]
                if 5 < len(p) < 35:
                    terms.add(p)
    stop = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'are', 'but', 'not', 'has', 'will', 'about', 'their', 'they', 'been', 'have', 'into', 'more', 'than', 'what', 'when', 'who', 'how', 'can', 'its', 'all', 'may'}
    return [x for x in terms if not all(w in stop for w in x.split())][:8]


def score_sources(data):
    scores = {}
    total = 0
    count = 0
    total_points = 0

    # YouTube: 50 videos = 100
    if 'youtube' in data and data['youtube']:
        vids = sum(r.get('video_count', 0) for r in data['youtube'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, vids * 2)
        scores['youtube'] = {'score': round(sc), 'detail': str(vids) + ' videos found across ' + str(len(data['youtube'])) + ' searches', 'count': vids}
        total += sc
        count += 1
        total_points += vids

    # Spotify: 50 playlists = 100
    if 'spotify' in data and data['spotify']:
        pls = sum(r.get('playlist_count', 0) for r in data['spotify'] if isinstance(r, dict) and not r.get('error'))
        tracks = 0
        for r in data['spotify']:
            if isinstance(r, dict) and not r.get('error'):
                for p in r.get('playlists', []):
                    tracks += p.get('tracks', 0)
        sc = min(100, pls * 2)
        scores['spotify'] = {'score': round(sc), 'detail': str(pls) + ' playlists with ' + str(tracks) + ' total tracks', 'count': pls}
        total += sc
        count += 1
        total_points += pls

    # Wikipedia: volume + trend combined
    if 'wikipedia' in data and data['wikipedia']:
        valid = [w for w in data['wikipedia'] if isinstance(w, dict) and not w.get('error') and w.get('total_views', 0) > 0]
        total_daily = sum(w.get('daily_average', 0) for w in valid)
        rising = sum(1 for w in valid if w.get('trend') == 'rising')
        vol = min(50, total_daily / 20)
        trend = min(50, (rising / max(len(valid), 1)) * 50) if valid else 0
        sc = vol + trend
        scores['wikipedia'] = {'score': round(sc), 'detail': str(len(valid)) + ' articles, ' + str(rising) + ' rising, ' + str(total_daily) + ' views/day', 'count': total_daily}
        total += sc
        count += 1
        total_points += total_daily

    # News: 100 articles = 100
    if 'news' in data and data['news']:
        arts = sum(r.get('total_results', 0) for r in data['news'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, arts)
        scores['news'] = {'score': round(sc), 'detail': str(arts) + ' articles in 30 days', 'count': arts}
        total += sc
        count += 1
        total_points += arts

    # AO3: 10K works = 100
    if 'ao3' in data and data['ao3']:
        works = sum(r.get('work_count', 0) for r in data['ao3'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, works / 100)
        scores['ao3'] = {'score': round(sc), 'detail': str(works) + ' fan fiction works', 'count': works}
        total += sc
        count += 1
        total_points += works

    # TMDB: inverse — less = higher
    if 'tmdb' in data and data['tmdb']:
        res = sum(r.get('count', 0) for r in data['tmdb'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, max(0, 100 - (res * 5)))
        scores['tmdb'] = {'score': round(sc), 'detail': str(res) + ' existing titles (fewer = bigger opportunity)', 'count': res}
        total += sc
        count += 1
        total_points += res

    # Books: 1000 = 100
    if 'books' in data and data['books']:
        bks = sum(r.get('total_found', 0) for r in data['books'] if isinstance(r, dict) and not r.get('error'))
        sc = min(100, bks / 10)
        scores['books'] = {'score': round(sc), 'detail': str(bks) + ' related books', 'count': bks}
        total += sc
        count += 1
        total_points += bks

    overall = round(total / max(count, 1))

    return {
        'overall_score': overall,
        'confidence': 'HIGH' if overall >= 65 else ('MODERATE' if overall >= 40 else 'LOW'),
        'sources_used': count,
        'total_data_points': total_points,
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
        'version': '4.2 — Honest Precision',
        'discovery_status': cache['status'],
        'predictions_generated': len(cache['predictions']),
        'last_run': cache['last_run'],
        'error': cache['error'],
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
def trigger():
    if cache['loading']:
        return jsonify({'message': 'Already running.'}), 429
    thread = threading.Thread(target=run_discovery, daemon=True)
    thread.start()
    return jsonify({'message': 'Started. Takes 8-15 minutes.'})


@app.route('/api/predictions')
def predictions():
    preds = []
    for p in cache['predictions']:
        preds.append({
            'id': p['id'],
            'name': p['name'],
            'rank': p['rank'],
            'psychological_drive': p['psychological_drive'],
            'confidence': p['confidence'],
            'convergence_score': p['convergence_score'],
            'source_count': p['source_count'],
            'gpt_confidence': p.get('gpt_confidence', ''),
            'gpt_convergence': p.get('gpt_convergence', 0),
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
        'analysis': cache.get('analysis'),
        'status': cache['status'],
        'last_run': cache['last_run'],
    })


@app.route('/api/predictions/<pid>')
def prediction_detail(pid):
    for p in cache['predictions']:
        if p['id'] == pid:
            return jsonify(p)
    return jsonify({'error': 'Not found. Run discovery first.'}), 404


@app.route('/api/raw-signals')
def raw():
    return jsonify(cache.get('raw_signals', {}))


# Scanner
@app.route('/api/scan/youtube')
def s_yt():
    q = request.args.get('q', '')
    return jsonify(search_youtube(q, 10)) if q else jsonify({'error': 'Need ?q='}), 400


@app.route('/api/scan/spotify')
def s_sp():
    q = request.args.get('q', '')
    return jsonify(search_spotify_playlists(q, 10)) if q else jsonify({'error': 'Need ?q='}), 400


@app.route('/api/scan/wikipedia')
def s_w():
    a = request.args.get('articles', '')
    if not a:
        return jsonify({'error': 'Need ?articles='}), 400
    return jsonify({'results': get_wikipedia_batch([x.strip() for x in a.split(',')][:5])})


@app.route('/api/scan/news')
def s_n():
    q = request.args.get('q', '')
    return jsonify(search_news(q, 30)) if q else jsonify({'error': 'Need ?q='}), 400


@app.route('/api/scan/news/headlines')
def s_hl():
    return jsonify(get_entertainment_headlines())


@app.route('/api/scan/ao3')
def s_ao3():
    tags = request.args.get('tags', '')
    if not tags:
        return jsonify({'error': 'Need ?tags='}), 400
    return jsonify({'results': get_ao3_batch([x.strip() for x in tags.split(',')][:5])})


@app.route('/api/scan/tmdb/trending')
def s_tmdb():
    return jsonify(get_tmdb_trending(request.args.get('type', 'all'), request.args.get('window', 'week')))


@app.route('/api/scan/tmdb/upcoming')
def s_tmdb_u():
    return jsonify(get_tmdb_upcoming_movies())


@app.route('/api/scan/books')
def s_bk():
    q = request.args.get('q', '')
    return jsonify(search_open_library(q)) if q else jsonify({'error': 'Need ?q='}), 400


@app.route('/api/scan/trends')
def s_tr():
    terms = request.args.get('terms', '')
    if not terms:
        return jsonify({'error': 'Need ?terms='}), 400
    return jsonify({'results': get_google_trends_batch([x.strip() for x in terms.split(',')][:3])})


@app.route('/api/analyses')
def analyses():
    from retroactive import get_all_analyses
    return jsonify(get_all_analyses())


@app.route('/api/analysis/<cid>')
def analysis(cid):
    from retroactive import get_all_analyses
    d = get_all_analyses()
    return jsonify(d[cid]) if cid in d else (jsonify({'error': 'Not found'}), 404)


# Auto-start
_started = False

@app.before_request
def auto():
    global _started
    if not _started and not cache['loading']:
        _started = True
        threading.Thread(target=run_discovery, daemon=True).start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
