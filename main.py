"""
Popcorn AI v5.2 — Sharp + Reliable
Shorter prompt that GPT-4o can handle.
Same sharp predictions. No timeouts.
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
    search_news,
    get_ao3_batch,
    search_tmdb,
    get_google_trends_batch,
    get_youtube_trending_by_category,
    get_tmdb_trending,
    get_tmdb_upcoming_movies,
    get_entertainment_headlines,
    search_open_library,
    format_number,
)

app = Flask(__name__, static_folder='public', static_url_path='')

cache = {
    'predictions': [],
    'analysis': None,
    'raw_signals': {},
    'status': 'not started',
    'loading': False,
    'last_run': None,
    'error': None,
}

PROMPT = """You are Popcorn AI — audience demand intelligence for entertainment.

Analyze these signals from YouTube, Spotify, Wikipedia, News, TMDB, AO3, and Books.

RULES:
1. Generate EXACTLY 7 cultural currents. Each must be COMPLETELY DIFFERENT — no overlap.
2. Be SPECIFIC not obvious. Not "people are lonely." Instead: "35-year-old men who grew up on Jackass are experiencing emotional awakenings through fatherhood — zero prestige content serves this 18M audience."
3. Every content_opportunity must be a COMPLETE PITCH: setting, characters, conflict, tone (reference 3 shows), episode structure. 150+ words. A showrunner could write a pilot from it.
4. search_terms_to_track must be what REAL HUMANS google at 11pm: "why am I so lonely in my 30s" not "loneliness epidemic."
5. comparable_successes must include REAL NUMBERS: "Ted Lasso averaged 7.6M viewers/episode" not "Ted Lasso was popular."
6. demand_gap must name 2-3 SPECIFIC existing shows, what they get RIGHT and what they MISS.
7. No generic predictions. Every one must make a studio exec say "why aren't we making this?"
8. audience_size_millions must be justified with demographics.
9. confidence should be HIGH if 5+ sources show signals, MODERATE if 3-4, LOW if 1-2.
10. Quote SPECIFIC data from my input in key_signals — video titles, playlist names, view counts.

Return JSON:
{
  "scan_date": "YYYY-MM-DD",
  "total_signals_analyzed": <number>,
  "cultural_currents": [
    {
      "name": "Short punchy name max 5 words",
      "rank": 1,
      "psychological_drive": "WHO (demo+age+size), WHY (life circumstance), HOW (behavior)",
      "confidence": "HIGH/MODERATE/LOW",
      "convergence_score": <1-10>,
      "supporting_sources": ["sources with actual signals"],
      "source_count": <number>,
      "key_signals": ["Quote 8+ specific data points from my input with numbers"],
      "target_demographic": "Age, gender, lifestyle, population size",
      "audience_size_millions": <number>,
      "format_recommendation": "Specific format with episode count",
      "tone_and_style": "Show A warmth + Show B intensity + Show C humor",
      "entertainment_prediction": "In X months a format about subject for Xm people styled like 3 shows will outcome",
      "demand_gap": "Name 2-3 shows that come close. What they get right. What they miss.",
      "content_opportunity": "FULL PITCH 150+ words: Setting, characters with ages, conflict, episode structure, tone, opening scene.",
      "comparable_successes": ["Show (Xm viewers) succeeded because reason"],
      "historical_parallel": "Resembles pre-hit because parallels",
      "search_terms_to_track": ["12 terms real humans actually search at 11pm"],
      "risk_factors": ["Specific risks"],
      "timeframe": "X-Y months",
      "what_to_watch": "When metric crosses threshold demand confirmed"
    }
  ],
  "meta_analysis": "3 paragraphs about the American cultural moment. Bold. Reference actual data from my input.",
  "biggest_gap": "The number 1 unserved demand. Describe the exact content in 3 sentences.",
  "collision_alert": "Are 3+ currents converging? Describe or say No collision detected."
}

RAW SIGNALS:

"""


def run_discovery():
    global cache
    cache['loading'] = True
    cache['status'] = 'harvesting signals'
    cache['error'] = None

    try:
        print('[Popcorn] ========== v5.2 DISCOVERY ==========')

        print('[Popcorn] Harvesting...')
        raw = harvest_all_signals()
        cache['raw_signals'] = raw
        cache['status'] = 'GPT-4o analyzing'

        total_signals = 0
        for key, val in raw.items():
            if isinstance(val, list):
                total_signals += len(val)
            elif isinstance(val, dict):
                for v2 in val.values():
                    if isinstance(v2, list):
                        total_signals += len(v2)

        sig_json = json.dumps(raw, indent=1, default=str)
        if len(sig_json) > 40000:
            sig_json = sig_json[:40000] + '\n...[truncated]'

        print('[Popcorn] GPT analyzing ' + str(len(sig_json)) + ' chars...')
        analysis = ask_gpt_json(PROMPT + sig_json, max_tokens=4096)

        if not analysis:
            cache['error'] = 'GPT-4o returned nothing. Check API key and billing.'
            cache['status'] = 'error'
            cache['loading'] = False
            return

        currents = analysis.get('cultural_currents', [])
        print('[Popcorn] GPT found ' + str(len(currents)) + ' currents')

        cache['status'] = 'enriching predictions'
        enriched = []

        for i, cur in enumerate(currents[:7]):
            name = cur.get('name', 'Unknown')
            print('[Popcorn] -- ' + str(i+1) + '. ' + name + ' --')

            terms = cur.get('search_terms_to_track', [])
            if len(terms) < 5:
                terms = terms + make_terms(cur)
            terms = list(dict.fromkeys(terms))[:12]

            data = {}
            src_count = 0

            # YouTube
            try:
                yt_all = []
                gv = 0
                gl = 0
                gc = 0
                for term in terms[:5]:
                    r = search_youtube(term, max_results=10)
                    if not r.get('error') and r.get('video_count', 0) > 0:
                        yt_all.append(r)
                        gv += r.get('total_views', 0)
                        gl += r.get('total_likes', 0)
                        gc += r.get('total_comments', 0)
                    t.sleep(0.5)
                all_vids = []
                for r in yt_all:
                    all_vids.extend(r.get('videos', []))
                all_vids.sort(key=lambda x: x.get('views', 0), reverse=True)
                data['youtube'] = {
                    'searches': yt_all,
                    'relevant_videos': all_vids[:15],
                    'total_videos': len(all_vids),
                    'total_views': gv,
                    'total_likes': gl,
                    'total_comments': gc,
                    'total_views_formatted': format_number(gv),
                    'total_likes_formatted': format_number(gl),
                    'avg_views_per_video': format_number(round(gv / max(len(all_vids), 1))),
                }
                if len(all_vids) > 0:
                    src_count += 1
                print('[Popcorn]   YT: ' + str(len(all_vids)) + ' vids, ' + format_number(gv) + ' views')
            except Exception as e:
                print('[Popcorn]   YT FAIL: ' + str(e))
                data['youtube'] = {'relevant_videos': [], 'total_videos': 0, 'total_views': 0, 'total_likes': 0}

            # Spotify
            try:
                sp = []
                gpl = 0
                gtr = 0
                for term in terms[:5]:
                    r = search_spotify_playlists(term, limit=10)
                    if not r.get('error') and r.get('playlist_count', 0) > 0:
                        sp.append(r)
                        gpl += r.get('playlist_count', 0)
                        gtr += r.get('total_tracks', 0)
                    t.sleep(0.5)
                data['spotify'] = {
                    'searches': sp,
                    'total_playlists': gpl,
                    'total_tracks': gtr,
                    'total_playlists_formatted': format_number(gpl),
                    'total_tracks_formatted': format_number(gtr),
                }
                if gpl > 0:
                    src_count += 1
                print('[Popcorn]   SP: ' + str(gpl) + ' playlists')
            except Exception as e:
                print('[Popcorn]   SP FAIL: ' + str(e))
                data['spotify'] = {'searches': [], 'total_playlists': 0, 'total_tracks': 0}

            # Wikipedia
            try:
                wt = [term.strip().replace(' ', '_').title() for term in terms[:6]]
                wiki = get_wikipedia_batch(wt)
                valid = [w for w in wiki if isinstance(w, dict) and not w.get('error') and w.get('total_views', 0) > 0]
                td = sum(w.get('daily_average', 0) for w in valid)
                tv = sum(w.get('total_views', 0) for w in valid)
                rising = sum(1 for w in valid if w.get('trend') == 'rising')
                data['wikipedia'] = {
                    'articles': valid,
                    'total_articles': len(valid),
                    'total_daily_views': td,
                    'total_views': tv,
                    'rising_count': rising,
                    'total_daily_formatted': format_number(td),
                    'total_views_formatted': format_number(tv),
                }
                if len(valid) > 0:
                    src_count += 1
                print('[Popcorn]   WIKI: ' + str(len(valid)) + ' arts, ' + format_number(td) + '/day')
            except Exception as e:
                print('[Popcorn]   WIKI FAIL: ' + str(e))
                data['wikipedia'] = {'articles': [], 'total_articles': 0, 'total_daily_views': 0}

            # News
            try:
                news = []
                ga = 0
                gsrc = set()
                for term in terms[:5]:
                    r = search_news(term, days_back=30, page_size=10)
                    if not r.get('error') and r.get('total_results', 0) > 0:
                        news.append(r)
                        ga += r.get('total_results', 0)
                        for s in r.get('source_names', []):
                            gsrc.add(s)
                    t.sleep(0.5)
                data['news'] = {
                    'searches': news,
                    'total_articles': ga,
                    'total_articles_formatted': format_number(ga),
                    'unique_sources': len(gsrc),
                    'source_names': list(gsrc)[:15],
                }
                if ga > 0:
                    src_count += 1
                print('[Popcorn]   NEWS: ' + format_number(ga) + ' articles')
            except Exception as e:
                print('[Popcorn]   NEWS FAIL: ' + str(e))
                data['news'] = {'searches': [], 'total_articles': 0}

            # AO3
            try:
                ao3 = get_ao3_batch(terms[:4])
                tw = sum(r.get('work_count', 0) for r in ao3 if isinstance(r, dict) and not r.get('error'))
                data['ao3'] = {
                    'tags': ao3,
                    'total_works': tw,
                    'total_works_formatted': format_number(tw),
                }
                if tw > 0:
                    src_count += 1
                print('[Popcorn]   AO3: ' + format_number(tw))
            except Exception as e:
                print('[Popcorn]   AO3 FAIL: ' + str(e))
                data['ao3'] = {'tags': [], 'total_works': 0}

            # TMDB
            try:
                tmdb = []
                tc = 0
                for term in terms[:2]:
                    r = search_tmdb(term)
                    if not r.get('error'):
                        tmdb.append(r)
                        tc += r.get('count', 0)
                    t.sleep(0.3)
                data['tmdb'] = {'searches': tmdb, 'total_titles': tc}
                src_count += 1
                print('[Popcorn]   TMDB: ' + str(tc))
            except Exception as e:
                print('[Popcorn]   TMDB FAIL: ' + str(e))
                data['tmdb'] = {'searches': [], 'total_titles': 0}

            # Books
            try:
                books = []
                bc = 0
                for term in terms[:2]:
                    r = search_open_library(term)
                    if not r.get('error'):
                        books.append(r)
                        bc += r.get('total_found', 0)
                    t.sleep(0.3)
                data['books'] = {'searches': books, 'total_found': bc, 'total_found_formatted': format_number(bc)}
                if bc > 0:
                    src_count += 1
                print('[Popcorn]   BOOKS: ' + format_number(bc))
            except Exception as e:
                data['books'] = {'searches': [], 'total_found': 0}

            strength = score_it(data, src_count)
            print('[Popcorn]   SCORE: ' + str(strength['overall_score']) + ' | ' + strength['confidence'] + ' | ' + str(src_count) + '/7')

            enriched.append({
                'id': name.lower().replace(' ', '-').replace('/', '-').replace("'", '').replace('"', '').replace(':', '').replace(',', '').replace('—', '-')[:40],
                'name': name,
                'rank': i + 1,
                'psychological_drive': cur.get('psychological_drive', ''),
                'confidence': strength['confidence'],
                'convergence_score': src_count,
                'source_count': src_count,
                'key_signals': cur.get('key_signals', []),
                'target_demographic': cur.get('target_demographic', ''),
                'audience_size_millions': cur.get('audience_size_millions', 0),
                'format_recommendation': cur.get('format_recommendation', ''),
                'tone_and_style': cur.get('tone_and_style', ''),
                'entertainment_prediction': cur.get('entertainment_prediction', ''),
                'demand_gap': cur.get('demand_gap', ''),
                'content_opportunity': cur.get('content_opportunity', ''),
                'comparable_successes': cur.get('comparable_successes', []),
                'historical_parallel': cur.get('historical_parallel', ''),
                'risk_factors': cur.get('risk_factors', []),
                'what_to_watch': cur.get('what_to_watch', ''),
                'timeframe': cur.get('timeframe', ''),
                'search_terms_used': terms,
                'signal_strength': strength,
                'supporting_data': data,
                'generated_at': datetime.utcnow().isoformat(),
            })

        enriched.sort(key=lambda x: x['signal_strength']['overall_score'], reverse=True)
        for i, p in enumerate(enriched):
            p['rank'] = i + 1

        cache['predictions'] = enriched
        cache['analysis'] = {
            'meta_analysis': analysis.get('meta_analysis', ''),
            'biggest_gap': analysis.get('biggest_gap', ''),
            'collision_alert': analysis.get('collision_alert', ''),
            'total_signals': total_signals,
            'scan_date': analysis.get('scan_date', datetime.utcnow().strftime('%Y-%m-%d')),
        }
        cache['status'] = 'loaded'
        cache['last_run'] = datetime.utcnow().isoformat()
        cache['loading'] = False
        print('[Popcorn] ========== DONE: ' + str(len(enriched)) + ' predictions ==========')

    except Exception as e:
        print('[Popcorn] FATAL: ' + str(e))
        traceback.print_exc()
        cache['error'] = str(e)
        cache['status'] = 'error'
        cache['loading'] = False


def make_terms(c):
    terms = set()
    for text in [c.get('name', ''), c.get('psychological_drive', ''), c.get('demand_gap', '')]:
        words = text.lower().replace(',', ' ').replace('.', ' ').replace('"', ' ').split()
        for i in range(len(words)):
            if i < len(words) - 1:
                p = words[i] + ' ' + words[i+1]
                if 5 < len(p) < 35:
                    terms.add(p)
    stop = {'the','and','for','that','this','with','from','are','but','not','has','will','about','their','they','have','into','more','than','what','when','who','how','can','all','would','could','should','just'}
    return [x for x in terms if not all(w in stop for w in x.split())][:8]


def score_it(data, src_count):
    scores = {}
    total = 0
    count = 0
    gp = 0

    yt = data.get('youtube', {})
    if yt.get('total_videos', 0) > 0:
        v = yt['total_views']
        n = yt['total_videos']
        l = yt.get('total_likes', 0)
        sc = 100 if v >= 1000000 else (70 + min(30, (v-100000)/30000) if v >= 100000 else (40 + min(30, (v-10000)/3000) if v >= 10000 else max(15, v/250)))
        sc = min(100, sc)
        scores['youtube'] = {'score': round(sc), 'detail': str(n) + ' videos · ' + format_number(v) + ' views · ' + format_number(l) + ' likes'}
        total += sc; count += 1; gp += n

    sp = data.get('spotify', {})
    if sp.get('total_playlists', 0) > 0:
        p = sp['total_playlists']; tr = sp.get('total_tracks', 0)
        sc = 100 if p >= 50 else (70 + min(30, p-20) if p >= 20 else (40 + min(30, (p-5)*2) if p >= 5 else p*8))
        sc = min(100, sc)
        scores['spotify'] = {'score': round(sc), 'detail': str(p) + ' playlists · ' + format_number(tr) + ' tracks'}
        total += sc; count += 1; gp += p

    wiki = data.get('wikipedia', {})
    if wiki.get('total_articles', 0) > 0:
        d = wiki['total_daily_views']; a = wiki['total_articles']; r = wiki.get('rising_count', 0)
        sc = 100 if d >= 1000 else (75 + min(25, (d-500)/20) if d >= 500 else (45 + min(30, (d-100)/13) if d >= 100 else max(15, d/2.5)))
        if a > 0: sc = min(100, sc + (r/a)*15)
        scores['wikipedia'] = {'score': round(sc), 'detail': str(a) + ' articles · ' + format_number(d) + ' views/day · ' + str(r) + ' rising'}
        total += sc; count += 1; gp += d

    news = data.get('news', {})
    if news.get('total_articles', 0) > 0:
        a = news['total_articles']; ns = news.get('unique_sources', 0)
        sc = 100 if a >= 500 else (70 + min(30, (a-100)/13) if a >= 100 else (40 + min(30, (a-20)/2.7) if a >= 20 else a*2))
        if ns >= 10: sc = min(100, sc + 10)
        sc = min(100, sc)
        scores['news'] = {'score': round(sc), 'detail': format_number(a) + ' articles · ' + str(ns) + ' outlets'}
        total += sc; count += 1; gp += a

    ao3 = data.get('ao3', {})
    if ao3.get('total_works', 0) > 0:
        w = ao3['total_works']
        sc = 100 if w >= 50000 else (70 + min(30, (w-10000)/1333) if w >= 10000 else (40 + min(30, (w-1000)/300) if w >= 1000 else max(10, w/25)))
        sc = min(100, sc)
        scores['ao3'] = {'score': round(sc), 'detail': format_number(w) + ' fan fiction works'}
        total += sc; count += 1; gp += w

    tmdb = data.get('tmdb', {})
    tt = tmdb.get('total_titles', 0)
    sc = 100 if tt == 0 else (85 if tt <= 3 else (60 if tt <= 10 else (35 if tt <= 20 else max(5, 100-tt*3))))
    scores['tmdb'] = {'score': round(sc), 'detail': str(tt) + ' existing titles (fewer = bigger gap)'}
    total += sc; count += 1

    books = data.get('books', {})
    if books.get('total_found', 0) > 0:
        b = books['total_found']
        sc = 100 if b >= 5000 else (70 + min(30, (b-1000)/133) if b >= 1000 else (40 + min(30, (b-100)/30) if b >= 100 else max(10, b/2.5)))
        sc = min(100, sc)
        scores['books'] = {'score': round(sc), 'detail': format_number(b) + ' related books'}
        total += sc; count += 1; gp += b

    overall = round(total / max(count, 1))
    if overall >= 60 and src_count >= 5:
        conf = 'HIGH'
    elif overall >= 45 and src_count >= 4:
        conf = 'HIGH'
    elif overall >= 35 and src_count >= 3:
        conf = 'MODERATE'
    else:
        conf = 'LOW'

    return {
        'overall_score': overall,
        'confidence': conf,
        'sources_used': count,
        'sources_with_data': src_count,
        'total_data_points': gp,
        'total_data_points_formatted': format_number(gp),
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
        'status': 'ok', 'version': '5.2',
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
            'wikipedia': True, 'ao3': True, 'open_library': True,
        },
    })

@app.route('/api/discover', methods=['POST'])
def trigger():
    if cache['loading']:
        return jsonify({'message': 'Already running.'}), 429
    threading.Thread(target=run_discovery, daemon=True).start()
    return jsonify({'message': 'Started. 10-15 min.'})

@app.route('/api/predictions')
def predictions():
    preds = []
    for p in cache['predictions']:
        s = p['signal_strength']
        yt = p.get('supporting_data', {}).get('youtube', {})
        sp = p.get('supporting_data', {}).get('spotify', {})
        news = p.get('supporting_data', {}).get('news', {})
        wiki = p.get('supporting_data', {}).get('wikipedia', {})
        preds.append({
            'id': p['id'], 'name': p['name'], 'rank': p['rank'],
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
            'content_opportunity': p.get('content_opportunity', ''),
            'timeframe': p['timeframe'],
            'signal_score': s['overall_score'],
            'total_data_points': s.get('total_data_points_formatted', '0'),
            'generated_at': p['generated_at'],
            'headline_stats': {
                'youtube_views': yt.get('total_views_formatted', '0'),
                'youtube_videos': str(yt.get('total_videos', 0)),
                'spotify_playlists': sp.get('total_playlists_formatted', '0'),
                'spotify_tracks': sp.get('total_tracks_formatted', '0'),
                'news_articles': news.get('total_articles_formatted', '0'),
                'news_outlets': str(news.get('unique_sources', 0)),
                'wiki_daily': wiki.get('total_daily_formatted', '0'),
            },
        })
    return jsonify({
        'count': len(preds), 'predictions': preds,
        'analysis': cache.get('analysis'),
        'status': cache['status'], 'last_run': cache['last_run'],
    })

@app.route('/api/predictions/<pid>')
def pred_detail(pid):
    for p in cache['predictions']:
        if p['id'] == pid:
            return jsonify(p)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/raw-signals')
def raw():
    return jsonify(cache.get('raw_signals', {}))

@app.route('/api/scan/youtube')
def s_yt():
    q = request.args.get('q', '')
    return jsonify(search_youtube(q, 10)) if q else (jsonify({'error': '?q='}), 400)

@app.route('/api/scan/spotify')
def s_sp():
    q = request.args.get('q', '')
    return jsonify(search_spotify_playlists(q, 10)) if q else (jsonify({'error': '?q='}), 400)

@app.route('/api/scan/wikipedia')
def s_w():
    a = request.args.get('articles', '')
    return jsonify({'results': get_wikipedia_batch([x.strip() for x in a.split(',')][:5])}) if a else (jsonify({'error': '?articles='}), 400)

@app.route('/api/scan/news')
def s_n():
    q = request.args.get('q', '')
    return jsonify(search_news(q, 30)) if q else (jsonify({'error': '?q='}), 400)

@app.route('/api/scan/news/headlines')
def s_hl():
    return jsonify(get_entertainment_headlines())

@app.route('/api/scan/ao3')
def s_ao3():
    tags = request.args.get('tags', '')
    return jsonify({'results': get_ao3_batch([x.strip() for x in tags.split(',')][:5])}) if tags else (jsonify({'error': '?tags='}), 400)

@app.route('/api/scan/tmdb/trending')
def s_tmdb():
    return jsonify(get_tmdb_trending(request.args.get('type', 'all'), request.args.get('window', 'week')))

@app.route('/api/scan/tmdb/upcoming')
def s_tmdb_u():
    return jsonify(get_tmdb_upcoming_movies())

@app.route('/api/scan/books')
def s_bk():
    q = request.args.get('q', '')
    return jsonify(search_open_library(q)) if q else (jsonify({'error': '?q='}), 400)

@app.route('/api/scan/trends')
def s_tr():
    terms = request.args.get('terms', '')
    return jsonify({'results': get_google_trends_batch([x.strip() for x in terms.split(',')][:3])}) if terms else (jsonify({'error': '?terms='}), 400)

@app.route('/api/analyses')
def analyses():
    from retroactive import get_all_analyses
    return jsonify(get_all_analyses())

@app.route('/api/analysis/<cid>')
def analysis_detail(cid):
    from retroactive import get_all_analyses
    d = get_all_analyses()
    return jsonify(d[cid]) if cid in d else (jsonify({'error': 'Not found'}), 404)

_started = False

@app.before_request
def auto():
    global _started
    if not _started and not cache['loading']:
        _started = True
        threading.Thread(target=run_discovery, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
