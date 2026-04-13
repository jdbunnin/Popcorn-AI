"""
Popcorn AI v5.0 — Sharp Predictions + Real Numbers
- Aggressive scoring that reflects reality
- GPT prompt demands OBVIOUS massive cultural movements
- Forces 6-8 predictions
- Shows actual view counts and engagement metrics
- Convergence counts every source that returns data
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
    format_number,
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
# THE PROMPT — Demands MASSIVE obvious cultural movements
# ============================================================
PROMPT = """You are Popcorn AI. You analyze raw cultural signals and identify the BIGGEST, most OBVIOUS audience demand movements happening right now.

CRITICAL RULES — READ CAREFULLY:

1. ONLY identify MASSIVE cultural movements that affect MILLIONS of people. Not niche subcultures. Not obscure genres. MAINSTREAM demand.
   BAD: "Post-apocalyptic hopepunk" (too niche, too specific)
   BAD: "Solarpunk aesthetics in media" (nobody searches this)
   GOOD: "Men's mental health crisis — 40M American men are searching for emotional permission"
   GOOD: "The loneliness epidemic — Americans are desperate for stories about human connection"
   GOOD: "Working class pride — 100M blue-collar Americans have zero representation in prestige TV"

2. Every prediction must be something a NORMAL PERSON would recognize and say "yes, I feel that."
   Test: Would your mom understand this cultural current? If not, it's too niche.

3. Be SPECIFIC about the content opportunity but BROAD about the cultural movement.
   The MOVEMENT is broad: "Americans are lonely and craving connection stories"
   The CONTENT is specific: "An 8-episode ensemble dramedy about strangers who form a community through a shared crisis, in the tone of Ted Lasso meets Friday Night Lights"

4. Generate EXACTLY 7 cultural currents. Not 4. Not 5. SEVEN.

5. Rank them by how LARGE the affected audience is. #1 should affect the most people.

6. For search_terms_to_track: provide 12-15 terms that REAL PEOPLE actually search on Google. Not academic terms. Not jargon.
   BAD: "parasocial relationship dynamics"
   GOOD: "why am I so lonely", "shows about friendship", "feel good tv shows"

7. For audience_size_millions: be aggressive but realistic. The loneliness epidemic affects 60M+ Americans. Men's mental health affects 40M+. Working class representation affects 80M+. These are REAL numbers.

8. For convergence_score: rate HONESTLY based on MY data.
   8-10: You can point to strong signals in 5+ of my data sources
   5-7: Signals in 3-4 of my data sources
   1-4: Signals in 1-2 sources only

9. For confidence: HIGH means the data is overwhelming and obvious. MODERATE means it's clearly there but not dominant. LOW means speculative. Given that I'm feeding you real trending data, most of your currents should be HIGH or MODERATE. If you can't find HIGH confidence currents in this data, you're not looking hard enough.

10. comparable_successes must include SPECIFIC box office or viewership numbers.
    BAD: "Ted Lasso was successful"
    GOOD: "Ted Lasso generated 7.6M viewers per episode in S3 and won 11 Emmys, proving massive demand for warm ensemble comedy"

Return JSON:
{
  "scan_date": "YYYY-MM-DD",
  "total_signals_analyzed": <count ALL data points in my input>,
  "cultural_currents": [
    {
      "name": "Short punchy name a normal person understands",
      "rank": 1,
      "psychological_drive": "WHO feels this (specific demographics with numbers), WHY they feel it (life circumstances), and HOW it manifests in their behavior",
      "confidence": "HIGH/MODERATE/LOW — most should be HIGH given real data",
      "convergence_score": <1-10 based on MY actual data>,
      "supporting_sources": ["only list sources where you SAW signals in my data"],
      "source_count": <real count>,
      "key_signals": [
        "QUOTE specific data from my input with numbers",
        "Reference ACTUAL video titles, playlist names, article headlines from my data",
        "At least 8 specific signals pulled directly from the data I gave you"
      ],
      "target_demographic": "Age, gender, income level, lifestyle — with population size",
      "audience_size_millions": <realistic but aggressive — think big>,
      "format_recommendation": "Specific format with episode count",
      "tone_and_style": "Name 2-3 existing hit shows for tone: 'Ted Lasso warmth meets The Bear intensity meets Fleabag honesty'",
      "entertainment_prediction": "In [timeframe], a [format] about [specific subject] targeting [specific audience of Xm people] in the style of [comparables] will [specific measurable outcome]",
      "demand_gap": "Name 2-3 existing shows that PARTIALLY satisfy this and explain what they're MISSING",
      "content_opportunity": "One paragraph pitch — so specific a producer could greenlight it tomorrow. Include setting, characters, conflict, tone, and episode structure.",
      "comparable_successes": ["Show A (Xm viewers, $Ym revenue) succeeded because Z", "Film B ($Xm box office) captured Y"],
      "historical_parallel": "Which specific pre-hit demand pattern this resembles — reference Barbie ($1.44B), Squid Game (265M hours), The Bear (most watched Hulu premiere)",
      "search_terms_to_track": ["12-15 terms real people actually google — not jargon"],
      "risk_factors": ["2-3 specific risks with mitigation strategies"],
      "timeframe": "X-Y months",
      "what_to_watch": "Specific metric: 'When [search term] crosses [threshold], demand is confirmed'"
    }
  ],
  "meta_analysis": "3 paragraphs about the DOMINANT cultural mood in America right now. Reference specific data points from my input. Be bold and insightful. This should read like a brilliant Variety think piece, not a textbook.",
  "biggest_gap": "The single most obvious massive unserved demand. Describe the EXACT content opportunity in 2-3 sentences. Make it so clear that anyone reading it says 'why doesn't this exist yet?'",
  "collision_alert": "Are 3+ of your identified currents converging toward a single content opportunity — the way nostalgia + camp + feminism + communal experience converged for Barbie ($1.44B)? If yes, describe the collision and the content at the center. If no, say 'No mega-collision detected but [closest convergence described].'"
}

IMPORTANT: Generate EXACTLY 7 currents. Make them BIG and OBVIOUS. I want a studio executive to read each one and say 'obviously, why aren't we making this?'

RAW SIGNAL DATA:

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
        print('[Popcorn] ========== DISCOVERY v5.0 ==========')

        # Step 1: Harvest
        print('[Popcorn] Step 1: Harvesting...')
        raw = harvest_all_signals()
        cache['raw_signals'] = raw
        cache['status'] = 'GPT-4o analyzing signals'

        # Count signals
        total_signals = 0
        for key, val in raw.items():
            if isinstance(val, list):
                total_signals += len(val)
            elif isinstance(val, dict):
                for v2 in val.values():
                    if isinstance(v2, list):
                        total_signals += len(v2)
        print('[Popcorn] Signals harvested: ' + str(total_signals))

        # Step 2: GPT
        sig_json = json.dumps(raw, indent=1, default=str)
        if len(sig_json) > 65000:
            sig_json = sig_json[:65000] + '\n...[truncated]'

        print('[Popcorn] Step 2: GPT-4o analyzing...')
        analysis = ask_gpt_json(PROMPT + sig_json, max_tokens=4096)

        if not analysis:
            cache['error'] = 'GPT-4o returned nothing. Check API key and billing.'
            cache['status'] = 'error'
            cache['loading'] = False
            return

        currents = analysis.get('cultural_currents', [])
        print('[Popcorn] GPT returned ' + str(len(currents)) + ' currents')

        # Step 3: Enrich with HEAVY real data
        cache['status'] = 'enriching with live engagement data'
        enriched = []

        for i, current in enumerate(currents[:8]):
            name = current.get('name', 'Unknown')
            print('[Popcorn] ---- ' + str(i+1) + '. ' + name + ' ----')

            terms = current.get('search_terms_to_track', [])
            if len(terms) < 8:
                terms = terms + make_terms(current)
            terms = list(dict.fromkeys(terms))[:15]

            data = {}
            sources_with_data = 0

            # YOUTUBE — 6 searches × 10 results with full stats
            try:
                yt = []
                grand_views = 0
                grand_likes = 0
                grand_comments = 0
                grand_vids = 0
                for term in terms[:6]:
                    r = search_youtube(term, max_results=10)
                    if not r.get('error') and r.get('video_count', 0) > 0:
                        yt.append(r)
                        grand_views += r.get('total_views', 0)
                        grand_likes += r.get('total_likes', 0)
                        grand_comments += r.get('total_comments', 0)
                        grand_vids += r.get('video_count', 0)
                    t.sleep(0.5)
                data['youtube'] = {
                    'searches': yt,
                    'total_videos': grand_vids,
                    'total_views': grand_views,
                    'total_likes': grand_likes,
                    'total_comments': grand_comments,
                    'total_views_formatted': format_number(grand_views),
                    'total_likes_formatted': format_number(grand_likes),
                    'avg_views_per_video': format_number(round(grand_views / max(grand_vids, 1))),
                }
                if grand_vids > 0:
                    sources_with_data += 1
                print('[Popcorn]   YT: ' + str(grand_vids) + ' videos, ' + format_number(grand_views) + ' views, ' + format_number(grand_likes) + ' likes')
            except Exception as e:
                print('[Popcorn]   YT FAIL: ' + str(e))
                data['youtube'] = {'searches': [], 'total_videos': 0, 'total_views': 0}

            # SPOTIFY — 6 searches × 10 playlists
            try:
                sp = []
                grand_pl = 0
                grand_tracks = 0
                for term in terms[:6]:
                    r = search_spotify_playlists(term, limit=10)
                    if not r.get('error') and r.get('playlist_count', 0) > 0:
                        sp.append(r)
                        grand_pl += r.get('playlist_count', 0)
                        grand_tracks += r.get('total_tracks', 0)
                    t.sleep(0.5)
                data['spotify'] = {
                    'searches': sp,
                    'total_playlists': grand_pl,
                    'total_tracks': grand_tracks,
                    'total_playlists_formatted': format_number(grand_pl),
                    'total_tracks_formatted': format_number(grand_tracks),
                }
                if grand_pl > 0:
                    sources_with_data += 1
                print('[Popcorn]   SP: ' + str(grand_pl) + ' playlists, ' + format_number(grand_tracks) + ' tracks')
            except Exception as e:
                print('[Popcorn]   SP FAIL: ' + str(e))
                data['spotify'] = {'searches': [], 'total_playlists': 0, 'total_tracks': 0}

            # WIKIPEDIA — 8 articles
            try:
                wiki_terms = []
                for term in terms[:8]:
                    clean = term.strip().replace(' ', '_')
                    clean = clean[0].upper() + clean[1:] if clean else clean
                    wiki_terms.append(clean)
                wiki = get_wikipedia_batch(wiki_terms)
                valid = [w for w in wiki if isinstance(w, dict) and not w.get('error') and w.get('total_views', 0) > 0]
                total_daily = sum(w.get('daily_average', 0) for w in valid)
                total_views = sum(w.get('total_views', 0) for w in valid)
                rising = sum(1 for w in valid if w.get('trend') == 'rising')
                data['wikipedia'] = {
                    'articles': valid,
                    'total_articles': len(valid),
                    'total_daily_views': total_daily,
                    'total_views': total_views,
                    'rising_count': rising,
                    'total_daily_formatted': format_number(total_daily),
                    'total_views_formatted': format_number(total_views),
                }
                if len(valid) > 0:
                    sources_with_data += 1
                print('[Popcorn]   WIKI: ' + str(len(valid)) + ' articles, ' + format_number(total_daily) + ' daily views, ' + str(rising) + ' rising')
            except Exception as e:
                print('[Popcorn]   WIKI FAIL: ' + str(e))
                data['wikipedia'] = {'articles': [], 'total_articles': 0, 'total_daily_views': 0}

            # NEWS — 6 searches × 10 articles
            try:
                news = []
                grand_articles = 0
                all_sources = set()
                for term in terms[:6]:
                    r = search_news(term, days_back=30, page_size=10)
                    if not r.get('error') and r.get('total_results', 0) > 0:
                        news.append(r)
                        grand_articles += r.get('total_results', 0)
                        for s in r.get('source_names', []):
                            all_sources.add(s)
                    t.sleep(0.5)
                data['news'] = {
                    'searches': news,
                    'total_articles': grand_articles,
                    'total_articles_formatted': format_number(grand_articles),
                    'unique_sources': len(all_sources),
                    'source_names': list(all_sources)[:15],
                }
                if grand_articles > 0:
                    sources_with_data += 1
                print('[Popcorn]   NEWS: ' + str(grand_articles) + ' articles from ' + str(len(all_sources)) + ' sources')
            except Exception as e:
                print('[Popcorn]   NEWS FAIL: ' + str(e))
                data['news'] = {'searches': [], 'total_articles': 0}

            # AO3 — 6 tags
            try:
                ao3 = get_ao3_batch(terms[:6])
                total_works = sum(r.get('work_count', 0) for r in ao3 if isinstance(r, dict) and not r.get('error'))
                data['ao3'] = {
                    'tags': ao3,
                    'total_works': total_works,
                    'total_works_formatted': format_number(total_works),
                }
                if total_works > 0:
                    sources_with_data += 1
                print('[Popcorn]   AO3: ' + format_number(total_works) + ' works')
            except Exception as e:
                print('[Popcorn]   AO3 FAIL: ' + str(e))
                data['ao3'] = {'tags': [], 'total_works': 0}

            # TMDB — 3 searches
            try:
                tmdb = []
                tmdb_count = 0
                for term in terms[:3]:
                    r = search_tmdb(term)
                    if not r.get('error'):
                        tmdb.append(r)
                        tmdb_count += r.get('count', 0)
                    t.sleep(0.3)
                data['tmdb'] = {
                    'searches': tmdb,
                    'total_titles': tmdb_count,
                }
                sources_with_data += 1  # Always counts (inverse)
                print('[Popcorn]   TMDB: ' + str(tmdb_count) + ' existing titles')
            except Exception as e:
                print('[Popcorn]   TMDB FAIL: ' + str(e))
                data['tmdb'] = {'searches': [], 'total_titles': 0}

            # BOOKS — 3 searches
            try:
                books = []
                book_count = 0
                for term in terms[:3]:
                    r = search_open_library(term)
                    if not r.get('error'):
                        books.append(r)
                        book_count += r.get('total_found', 0)
                    t.sleep(0.3)
                data['books'] = {
                    'searches': books,
                    'total_found': book_count,
                    'total_found_formatted': format_number(book_count),
                }
                if book_count > 0:
                    sources_with_data += 1
                print('[Popcorn]   BOOKS: ' + format_number(book_count))
            except Exception as e:
                print('[Popcorn]   BOOKS FAIL: ' + str(e))
                data['books'] = {'searches': [], 'total_found': 0}

            # SCORE IT — aggressive but honest
            strength = score_it(data, sources_with_data)

            print('[Popcorn]   SCORE: ' + str(strength['overall_score']) + ' | CONF: ' + strength['confidence'] + ' | SOURCES: ' + str(sources_with_data) + '/7')

            enriched.append({
                'id': name.lower().replace(' ', '-').replace('/', '-').replace("'", '').replace('"', '').replace(':', '').replace(',', '')[:40],
                'name': name,
                'rank': i + 1,
                'psychological_drive': current.get('psychological_drive', ''),
                'confidence': strength['confidence'],
                'convergence_score': sources_with_data,
                'source_count': sources_with_data,
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

        # Sort by score
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
    for text in [c.get('name', ''), c.get('psychological_drive', ''), c.get('demand_gap', ''), c.get('content_opportunity', '')]:
        words = text.lower().replace(',', ' ').replace('.', ' ').replace('"', ' ').replace("'", ' ').split()
        for i in range(len(words)):
            if i < len(words) - 1:
                p = words[i] + ' ' + words[i+1]
                if 5 < len(p) < 35:
                    terms.add(p)
    stop = {'the','and','for','that','this','with','from','are','but','not','has','will','about','their','they','been','have','into','more','than','what','when','who','how','can','its','all','may','would','could','should','just'}
    return [x for x in terms if not all(w in stop for w in x.split())][:10]


def score_it(data, sources_with_data):
    scores = {}
    total = 0
    count = 0
    grand_data_points = 0

    # YOUTUBE — views are the king metric
    yt = data.get('youtube', {})
    if yt.get('total_videos', 0) > 0:
        views = yt.get('total_views', 0)
        vids = yt.get('total_videos', 0)
        likes = yt.get('total_likes', 0)

        # Scale: 1M+ total views = 100, 100K = 70, 10K = 40
        if views >= 1000000:
            sc = 100
        elif views >= 100000:
            sc = 70 + (views - 100000) / 30000
        elif views >= 10000:
            sc = 40 + (views - 10000) / 3000
        else:
            sc = max(15, views / 250)
        sc = min(100, sc)

        scores['youtube'] = {
            'score': round(sc),
            'detail': str(vids) + ' videos · ' + format_number(views) + ' total views · ' + format_number(likes) + ' likes',
            'total_views': views,
            'total_videos': vids,
        }
        total += sc
        count += 1
        grand_data_points += vids

    # SPOTIFY
    sp = data.get('spotify', {})
    if sp.get('total_playlists', 0) > 0:
        pls = sp.get('total_playlists', 0)
        tracks = sp.get('total_tracks', 0)

        # Scale: 50+ playlists = 100, 20 = 70, 5 = 40
        if pls >= 50:
            sc = 100
        elif pls >= 20:
            sc = 70 + (pls - 20) / 1
        elif pls >= 5:
            sc = 40 + (pls - 5) * 2
        else:
            sc = pls * 8
        sc = min(100, sc)

        scores['spotify'] = {
            'score': round(sc),
            'detail': str(pls) + ' playlists · ' + format_number(tracks) + ' total tracks',
            'total_playlists': pls,
        }
        total += sc
        count += 1
        grand_data_points += pls

    # WIKIPEDIA
    wiki = data.get('wikipedia', {})
    if wiki.get('total_articles', 0) > 0:
        daily = wiki.get('total_daily_views', 0)
        arts = wiki.get('total_articles', 0)
        rising = wiki.get('rising_count', 0)

        # Scale: 1000+ daily views across articles = 100
        if daily >= 1000:
            sc = 100
        elif daily >= 500:
            sc = 75 + (daily - 500) / 20
        elif daily >= 100:
            sc = 45 + (daily - 100) / 13
        else:
            sc = max(15, daily / 2.5)

        # Bonus for rising articles
        if arts > 0:
            rise_bonus = (rising / arts) * 15
            sc = min(100, sc + rise_bonus)

        scores['wikipedia'] = {
            'score': round(sc),
            'detail': str(arts) + ' articles · ' + format_number(daily) + ' views/day · ' + str(rising) + ' rising',
            'total_daily': daily,
        }
        total += sc
        count += 1
        grand_data_points += daily

    # NEWS
    news = data.get('news', {})
    if news.get('total_articles', 0) > 0:
        arts = news.get('total_articles', 0)
        sources_count = news.get('unique_sources', 0)

        # Scale: 500+ articles = 100, 100 = 70, 20 = 40
        if arts >= 500:
            sc = 100
        elif arts >= 100:
            sc = 70 + (arts - 100) / 13
        elif arts >= 20:
            sc = 40 + (arts - 20) / 2.7
        else:
            sc = arts * 2
        sc = min(100, sc)

        # Bonus for source diversity
        if sources_count >= 10:
            sc = min(100, sc + 10)

        scores['news'] = {
            'score': round(sc),
            'detail': format_number(arts) + ' articles · ' + str(sources_count) + ' news outlets',
            'total_articles': arts,
        }
        total += sc
        count += 1
        grand_data_points += arts

    # AO3
    ao3 = data.get('ao3', {})
    if ao3.get('total_works', 0) > 0:
        works = ao3.get('total_works', 0)

        # Scale: 50K+ works = 100, 10K = 70, 1K = 40
        if works >= 50000:
            sc = 100
        elif works >= 10000:
            sc = 70 + (works - 10000) / 1333
        elif works >= 1000:
            sc = 40 + (works - 1000) / 300
        else:
            sc = max(10, works / 25)
        sc = min(100, sc)

        scores['ao3'] = {
            'score': round(sc),
            'detail': format_number(works) + ' fan fiction works',
            'total_works': works,
        }
        total += sc
        count += 1
        grand_data_points += works

    # TMDB — INVERSE
    tmdb = data.get('tmdb', {})
    tmdb_titles = tmdb.get('total_titles', 0)
    if tmdb_titles == 0:
        sc = 100
    elif tmdb_titles <= 3:
        sc = 85
    elif tmdb_titles <= 10:
        sc = 60
    elif tmdb_titles <= 20:
        sc = 35
    else:
        sc = max(5, 100 - tmdb_titles * 3)

    scores['tmdb'] = {
        'score': round(sc),
        'detail': str(tmdb_titles) + ' existing titles (fewer = bigger gap)',
        'total_titles': tmdb_titles,
    }
    total += sc
    count += 1

    # BOOKS
    books = data.get('books', {})
    if books.get('total_found', 0) > 0:
        bks = books.get('total_found', 0)

        if bks >= 5000:
            sc = 100
        elif bks >= 1000:
            sc = 70 + (bks - 1000) / 133
        elif bks >= 100:
            sc = 40 + (bks - 100) / 30
        else:
            sc = max(10, bks / 2.5)
        sc = min(100, sc)

        scores['books'] = {
            'score': round(sc),
            'detail': format_number(bks) + ' related books',
            'total_found': bks,
        }
        total += sc
        count += 1
        grand_data_points += bks

    overall = round(total / max(count, 1))

    # Confidence based on overall + source count
    if overall >= 60 and sources_with_data >= 5:
        confidence = 'HIGH'
    elif overall >= 45 and sources_with_data >= 4:
        confidence = 'HIGH'
    elif overall >= 35 and sources_with_data >= 3:
        confidence = 'MODERATE'
    else:
        confidence = 'LOW'

    return {
        'overall_score': overall,
        'confidence': confidence,
        'sources_used': count,
        'sources_with_data': sources_with_data,
        'total_data_points': grand_data_points,
        'total_data_points_formatted': format_number(grand_data_points),
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
        'version': '5.0 — Sharp + Real Numbers',
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
    return jsonify({'message': 'Started. Takes 10-15 minutes.'})


@app.route('/api/predictions')
def predictions():
    preds = []
    for p in cache['predictions']:
        s = p['signal_strength']
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
            'content_opportunity': p.get('content_opportunity', ''),
            'timeframe': p['timeframe'],
            'signal_score': s['overall_score'],
            'total_data_points': s.get('total_data_points_formatted', '0'),
            'generated_at': p['generated_at'],
            # Summary engagement numbers for the card
            'headline_stats': {
                'youtube_views': p.get('supporting_data', {}).get('youtube', {}).get('total_views_formatted', '0'),
                'spotify_playlists': p.get('supporting_data', {}).get('spotify', {}).get('total_playlists_formatted', '0'),
                'news_articles': p.get('supporting_data', {}).get('news', {}).get('total_articles_formatted', '0'),
                'wiki_daily': p.get('supporting_data', {}).get('wikipedia', {}).get('total_daily_formatted', '0'),
            },
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
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/raw-signals')
def raw():
    return jsonify(cache.get('raw_signals', {}))


# Scanner
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
