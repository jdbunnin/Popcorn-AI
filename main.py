"""
Popcorn AI — Audience Demand Intelligence
v3.0: Real data from Google Trends, YouTube, Spotify, 
Wikipedia, TMDB, NewsAPI, AO3, Open Library
"""

from flask import Flask, jsonify, send_from_directory, request
import os
import json
from datetime import datetime
from data_collectors import (
    get_google_trends, get_google_trends_batch,
    search_youtube, get_youtube_trending_by_category,
    search_spotify_playlists, get_spotify_category_playlists,
    get_wikipedia_pageviews, get_wikipedia_batch,
    get_tmdb_upcoming_movies, get_tmdb_trending, search_tmdb,
    search_news, get_entertainment_headlines,
    get_ao3_tag_count, get_ao3_batch,
    search_open_library,
    collect_signals_for_topic,
)

app = Flask(__name__, static_folder='public', static_url_path='')

# ============================================================
# SERVE FRONTEND
# ============================================================
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/api/health')
def health():
    keys_status = {
        'youtube': bool(os.environ.get('YOUTUBE_API_KEY')),
        'spotify': bool(os.environ.get('SPOTIFY_CLIENT_ID')),
        'tmdb': bool(os.environ.get('TMDB_API_KEY')),
        'news': bool(os.environ.get('NEWS_API_KEY')),
        'google_trends': True,
        'wikipedia': True,
        'ao3': True,
        'open_library': True,
    }
    return jsonify({
        'status': 'ok',
        'app': 'Popcorn AI',
        'version': '3.0 — Real Data',
        'data_sources': keys_status,
        'active_sources': sum(1 for v in keys_status.values() if v),
    })


# ============================================================
# CURRENT CULTURAL SIGNALS — The Live Product
# ============================================================

# These are the cultural currents we're tracking RIGHT NOW
# Each has search terms for multiple data sources
CURRENT_PREDICTIONS = [
    {
        'id': 'analog-humanity',
        'name': 'The Human Premium',
        'category': 'Cultural Collision',
        'thesis': 'AI anxiety is driving a counter-movement celebrating irreplaceable human qualities — craftsmanship, physical presence, emotional intuition, and analog experiences. Content that celebrates what makes humans special will dramatically outperform in the next 12 months.',
        'prediction': 'Content celebrating handmade craft, analog experiences, and human connection will outperform digital/tech-focused content by 2-3x in audience engagement metrics within 12 months.',
        'timeframe': '6-12 months',
        'date_published': datetime.utcnow().strftime('%Y-%m-%d'),
        'search_terms': [
            'analog lifestyle',
            'digital detox',
            'handmade crafts',
            'film photography',
            'vinyl records',
            'board game cafe',
            'artisan craftsmanship',
        ],
        'wiki_articles': [
            'Slow_movement_(culture)',
            'Handicraft',
            'Vinyl_revival',
            'Film_photography',
            'Digital_detox',
        ],
        'ao3_tags': [
            'Domestic Fluff',
            'Cottagecore',
            'Slice of Life',
        ],
        'news_queries': [
            'analog renaissance',
            'handmade crafts trend',
            'digital detox movement',
        ],
        'spotify_queries': [
            'acoustic chill',
            'folk and craft',
            'unplugged living',
        ],
    },
    {
        'id': 'male-vulnerability',
        'name': 'Male Emotional Awakening',
        'category': 'Psychological Drive',
        'thesis': 'Male mental health discourse has exploded. Men are searching for permission to be emotionally vulnerable. Content featuring genuinely emotionally open male characters — not action heroes showing one tear — will find a massive underserved audience.',
        'prediction': 'A show or film featuring a male lead whose primary arc is emotional vulnerability (not action or achievement) will become a top-10 cultural moment within 18 months.',
        'timeframe': '6-18 months',
        'date_published': datetime.utcnow().strftime('%Y-%m-%d'),
        'search_terms': [
            'mens mental health',
            'therapy for men',
            'men crying',
            'toxic masculinity',
            'male vulnerability',
            'men emotional support',
            'boys dont cry myth',
        ],
        'wiki_articles': [
            'Masculinity',
            'Mental_health_of_men',
            'Toxic_masculinity',
            'Emotional_intelligence',
        ],
        'ao3_tags': [
            'Hurt/Comfort',
            'Emotional Hurt/Comfort',
            'Male Friendship',
            'Vulnerability',
        ],
        'news_queries': [
            'men mental health crisis',
            'male vulnerability culture',
            'men therapy trend',
        ],
        'spotify_queries': [
            'sad songs for men',
            'mens mental health',
            'emotional healing',
        ],
    },
    {
        'id': 'found-family',
        'name': 'Found Family Renaissance',
        'category': 'Belonging Drive',
        'thesis': 'Loneliness epidemic plus declining traditional family structures are driving massive demand for stories about chosen families — groups of unrelated people who become each others support system. This is the dominant narrative craving of 2025.',
        'prediction': 'The next breakout ensemble show will center on found family dynamics in a non-traditional setting (not a workplace, not a friend group in a city). Think: strangers bonding through shared adversity in an unexpected context.',
        'timeframe': '3-12 months',
        'date_published': datetime.utcnow().strftime('%Y-%m-%d'),
        'search_terms': [
            'loneliness epidemic',
            'found family',
            'chosen family',
            'making friends as adult',
            'community building',
            'third places',
            'belonging',
        ],
        'wiki_articles': [
            'Loneliness',
            'Chosen_family',
            'Third_place',
            'Social_isolation',
            'Found_family',
        ],
        'ao3_tags': [
            'Found Family',
            'Chosen Family',
            'Team as Family',
            'Platonic Relationships',
        ],
        'news_queries': [
            'loneliness epidemic america',
            'community building trend',
            'third places revival',
        ],
        'spotify_queries': [
            'feel good community',
            'friendship anthems',
            'together playlist',
        ],
    },
    {
        'id': 'class-consciousness',
        'name': 'Working Class Visibility',
        'category': 'Identity Demand',
        'thesis': 'After The Bear proved massive demand exists for authentic working-class stories, the appetite has only grown. 74% of Americans work outside offices but nearly all prestige content depicts upper-middle-class life. The demand gap is widening.',
        'prediction': 'At least two major streaming shows set in blue-collar environments (not restaurants — that niche is filled) will be greenlit and one will become a top performer within 18 months.',
        'timeframe': '6-18 months',
        'date_published': datetime.utcnow().strftime('%Y-%m-%d'),
        'search_terms': [
            'working class tv shows',
            'blue collar jobs',
            'skilled trades career',
            'trade school vs college',
            'construction workers',
            'everyday heroes',
            'working class representation',
        ],
        'wiki_articles': [
            'Working_class',
            'Blue-collar_worker',
            'Trades_(occupation)',
            'Class_consciousness',
        ],
        'ao3_tags': [
            'Working Class',
            'Blue Collar',
            'Slice of Life',
        ],
        'news_queries': [
            'skilled trades shortage',
            'blue collar renaissance',
            'working class culture',
        ],
        'spotify_queries': [
            'working class anthems',
            'blue collar playlist',
            'country working man',
        ],
    },
    {
        'id': 'spiritual-not-religious',
        'name': 'Secular Spirituality Wave',
        'category': 'Meaning Drive',
        'thesis': 'Spiritual but not religious is the fastest growing identity category in under-40 demographics. Meditation apps, psychedelic therapy, astrology, and consciousness content are all surging. Yet zero mainstream entertainment takes spirituality seriously without being preachy or religious.',
        'prediction': 'A prestige series that treats non-religious spirituality (meditation, psychedelics, consciousness exploration, mystical experiences) with the same seriousness that The Bear treats cooking will become a cultural touchstone.',
        'timeframe': '12-24 months',
        'date_published': datetime.utcnow().strftime('%Y-%m-%d'),
        'search_terms': [
            'spiritual but not religious',
            'meditation benefits',
            'psychedelic therapy',
            'consciousness exploration',
            'astrology trend',
            'meaning of life',
            'spiritual awakening',
        ],
        'wiki_articles': [
            'Spiritual_but_not_religious',
            'Meditation',
            'Psychedelic_therapy',
            'Astrology_and_science',
            'Mindfulness',
        ],
        'ao3_tags': [
            'Spiritual',
            'Meditation',
            'Magical Realism',
            'Psychic Abilities',
        ],
        'news_queries': [
            'psychedelic therapy legalization',
            'meditation mainstream',
            'spiritual not religious trend',
        ],
        'spotify_queries': [
            'meditation music',
            'spiritual journey',
            'consciousness exploration',
        ],
    },
]


# ============================================================
# RETROACTIVE PROOF (v2 content-blind — keeping this)
# ============================================================
BARBIE_PROOF = {
    'title': 'Barbie (2023)',
    'release_date': 'July 21, 2023',
    'outcome': '$1.44B worldwide on $145M budget',
    'thesis': 'Four independent cultural currents were converging in early 2023: millennial nostalgia, pink/camp aesthetics, feminist comedy appetite, and communal theatrical craving. The demand existed before the movie.',
    'search_terms': ['90s nostalgia', 'pink aesthetic', 'feminist comedy', 'camp fashion', 'movies to see with friends', 'dopamine dressing'],
    'wiki_articles': ['Nostalgia', 'Camp_(style)', 'Feminism_in_the_United_States'],
}

SQUID_GAME_PROOF = {
    'title': 'Squid Game (2021)',
    'release_date': 'September 17, 2021',
    'outcome': 'Most watched Netflix show ever at release',
    'thesis': 'Economic anxiety, K-culture adoption, survival narrative appetite, and post-pandemic craving for shared cultural moments all converged in mid-2021.',
    'search_terms': ['wealth inequality', 'korean drama recommendations', 'survival anime', 'battle royale games', 'what is everyone watching', 'economic inequality'],
    'wiki_articles': ['Economic_inequality', 'Korean_wave', 'Battle_royale_game'],
}

THE_BEAR_PROOF = {
    'title': 'The Bear (2022)',
    'release_date': 'June 23, 2022',
    'outcome': 'Highest rated new show of 2022, Emmy winner',
    'thesis': 'Massive demand gap for authentic working-class narratives, burnout representation, food-as-art appreciation, and craft/mastery content — all with near-zero supply.',
    'search_terms': ['working class shows', 'burnout', 'restaurant behind the scenes', 'satisfying videos', 'food as art', 'quiet quitting'],
    'wiki_articles': ['Working_class', 'Occupational_burnout', 'Culinary_arts'],
}


# ============================================================
# API ROUTES — Real Data
# ============================================================

@app.route('/api/predictions')
def get_predictions():
    """Return all current predictions with metadata."""
    predictions = []
    for p in CURRENT_PREDICTIONS:
        predictions.append({
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
        'count': len(predictions),
        'predictions': predictions,
        'generated_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/predictions/<prediction_id>/signals')
def get_prediction_signals(prediction_id):
    """
    Pull REAL data for a specific prediction.
    This calls all data sources live.
    """
    prediction = None
    for p in CURRENT_PREDICTIONS:
        if p['id'] == prediction_id:
            prediction = p
            break

    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404

    # Collect real signals from all sources
    signals = collect_signals_for_topic(
        topic_name=prediction['name'],
        search_terms=prediction['search_terms'],
        wiki_articles=prediction['wiki_articles'],
        ao3_tags=prediction['ao3_tags'],
        news_queries=prediction['news_queries'],
    )

    # Also get Spotify data
    spotify_data = []
    for query in prediction.get('spotify_queries', [])[:3]:
        spotify_data.append(search_spotify_playlists(query, limit=5))

    signals['sources']['spotify'] = spotify_data

    # Calculate signal strength
    strength = calculate_signal_strength(signals)

    return jsonify({
        'prediction_id': prediction_id,
        'prediction_name': prediction['name'],
        'thesis': prediction['thesis'],
        'prediction_text': prediction['prediction'],
        'timeframe': prediction['timeframe'],
        'date_published': prediction['date_published'],
        'signal_strength': strength,
        'raw_signals': signals,
        'collected_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/scan/trends')
def scan_trends():
    """
    Pull Google Trends for a custom list of terms.
    Usage: /api/scan/trends?terms=term1,term2,term3
    """
    terms_param = request.args.get('terms', '')
    if not terms_param:
        return jsonify({'error': 'Provide ?terms=term1,term2,term3'}), 400

    terms = [t.strip() for t in terms_param.split(',') if t.strip()][:10]
    timeframe = request.args.get('timeframe', 'today 12-m')

    results = get_google_trends_batch(terms, timeframe)
    return jsonify({
        'terms': terms,
        'timeframe': timeframe,
        'results': results,
        'collected_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/scan/youtube')
def scan_youtube():
    """
    Search YouTube for cultural signals.
    Usage: /api/scan/youtube?q=search+term
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Provide ?q=search+term'}), 400

    results = search_youtube(query, max_results=10)
    return jsonify(results)


@app.route('/api/scan/youtube/trending')
def scan_youtube_trending():
    """Get YouTube trending in entertainment."""
    category = request.args.get('category', '24')
    results = get_youtube_trending_by_category(category)
    return jsonify(results)


@app.route('/api/scan/spotify')
def scan_spotify():
    """
    Search Spotify playlists for cultural signals.
    Usage: /api/scan/spotify?q=search+term
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Provide ?q=search+term'}), 400

    results = search_spotify_playlists(query, limit=10)
    return jsonify(results)


@app.route('/api/scan/wikipedia')
def scan_wikipedia():
    """
    Get Wikipedia pageviews for cultural topics.
    Usage: /api/scan/wikipedia?articles=Article1,Article2
    """
    articles_param = request.args.get('articles', '')
    if not articles_param:
        return jsonify({'error': 'Provide ?articles=Article1,Article2'}), 400

    articles = [a.strip() for a in articles_param.split(',') if a.strip()][:10]
    days = int(request.args.get('days', '90'))

    results = get_wikipedia_batch(articles, days)
    return jsonify({
        'articles': articles,
        'days': days,
        'results': results,
        'collected_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/scan/news')
def scan_news():
    """
    Search news for cultural signals.
    Usage: /api/scan/news?q=search+term
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Provide ?q=search+term'}), 400

    days = int(request.args.get('days', '30'))
    results = search_news(query, days_back=days)
    return jsonify(results)


@app.route('/api/scan/news/headlines')
def scan_headlines():
    """Get current entertainment headlines."""
    results = get_entertainment_headlines()
    return jsonify(results)


@app.route('/api/scan/ao3')
def scan_ao3():
    """
    Get AO3 work counts for tags.
    Usage: /api/scan/ao3?tags=Found+Family,Hurt/Comfort
    """
    tags_param = request.args.get('tags', '')
    if not tags_param:
        return jsonify({'error': 'Provide ?tags=Tag1,Tag2'}), 400

    tags = [t.strip() for t in tags_param.split(',') if t.strip()][:10]
    results = get_ao3_batch(tags)
    return jsonify({
        'tags': tags,
        'results': results,
        'collected_at': datetime.utcnow().isoformat(),
    })


@app.route('/api/scan/tmdb/trending')
def scan_tmdb_trending():
    """Get trending movies and shows."""
    media_type = request.args.get('type', 'all')
    window = request.args.get('window', 'week')
    results = get_tmdb_trending(media_type, window)
    return jsonify(results)


@app.route('/api/scan/tmdb/upcoming')
def scan_tmdb_upcoming():
    """Get upcoming movies."""
    results = get_tmdb_upcoming_movies()
    return jsonify(results)


@app.route('/api/scan/books')
def scan_books():
    """
    Search books for cultural signals.
    Usage: /api/scan/books?q=search+term
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Provide ?q=search+term'}), 400

    results = search_open_library(query)
    return jsonify(results)


# ============================================================
# RETROACTIVE ANALYSES (keeping v2 data)
# ============================================================

@app.route('/api/analyses')
def get_analyses():
    """Return the retroactive proof analyses."""
    # Import the v2 analysis logic
    from retroactive import get_all_analyses
    return jsonify(get_all_analyses())


@app.route('/api/analysis/<case_id>')
def get_single_analysis(case_id):
    from retroactive import get_all_analyses
    analyses = get_all_analyses()
    if case_id in analyses:
        return jsonify(analyses[case_id])
    return jsonify({'error': 'Not found'}), 404


# ============================================================
# SIGNAL STRENGTH CALCULATOR
# ============================================================

def calculate_signal_strength(signals):
    """
    Calculate overall signal strength from collected data.
    Returns a score and breakdown.
    """
    scores = {}
    total_score = 0
    source_count = 0

    sources = signals.get('sources', {})

    # Google Trends scoring
    if 'google_trends' in sources:
        trends = sources['google_trends']
        velocities = []
        for t in trends:
            if isinstance(t, dict) and t.get('data') and not t.get('error'):
                data = t['data']
                months = sorted(data.keys())
                if len(months) >= 2:
                    first = data[months[0]]
                    last = data[months[-1]]
                    velocity = ((last - first) / max(first, 1)) * 100
                    velocities.append(velocity)

        if velocities:
            avg_velocity = sum(velocities) / len(velocities)
            trend_score = min(100, max(0, avg_velocity + 50))
            scores['google_trends'] = {
                'score': round(trend_score),
                'detail': f'Avg velocity: {round(avg_velocity, 1)}% across {len(velocities)} terms',
                'terms_analyzed': len(velocities),
            }
            total_score += trend_score
            source_count += 1

    # YouTube scoring
    if 'youtube' in sources:
        yt = sources['youtube']
        total_videos = sum(
            r.get('video_count', 0) for r in yt if isinstance(r, dict) and not r.get('error')
        )
        yt_score = min(100, total_videos * 5)
        scores['youtube'] = {
            'score': round(yt_score),
            'detail': f'{total_videos} relevant videos found',
        }
        total_score += yt_score
        source_count += 1

    # Spotify scoring
    if 'spotify' in sources:
        sp = sources['spotify']
        total_playlists = sum(
            r.get('playlist_count', 0) for r in sp if isinstance(r, dict) and not r.get('error')
        )
        sp_score = min(100, total_playlists * 8)
        scores['spotify'] = {
            'score': round(sp_score),
            'detail': f'{total_playlists} related playlists found',
        }
        total_score += sp_score
        source_count += 1

    # Wikipedia scoring
    if 'wikipedia' in sources:
        wiki = sources['wikipedia']
        rising_count = sum(
            1 for w in wiki if isinstance(w, dict) and w.get('trend') == 'rising'
        )
        total_articles = len([w for w in wiki if isinstance(w, dict) and not w.get('error')])
        wiki_score = min(100, (rising_count / max(total_articles, 1)) * 100)
        scores['wikipedia'] = {
            'score': round(wiki_score),
            'detail': f'{rising_count}/{total_articles} articles trending upward',
        }
        total_score += wiki_score
        source_count += 1

    # News scoring
    if 'news' in sources:
        news = sources['news']
        total_articles = sum(
            r.get('total_results', 0) for r in news if isinstance(r, dict) and not r.get('error')
        )
        news_score = min(100, total_articles * 2)
        scores['news'] = {
            'score': round(news_score),
            'detail': f'{total_articles} relevant news articles found',
        }
        total_score += news_score
        source_count += 1

    # AO3 scoring
    if 'ao3' in sources:
        ao3 = sources['ao3']
        total_works = sum(
            r.get('work_count', 0) for r in ao3 if isinstance(r, dict) and not r.get('error')
        )
        ao3_score = min(100, (total_works / 1000) * 10)
        scores['ao3'] = {
            'score': round(ao3_score),
            'detail': f'{total_works:,} fan fiction works with related tags',
        }
        total_score += ao3_score
        source_count += 1

    # TMDB scoring
    if 'tmdb' in sources:
        tmdb = sources['tmdb']
        total_results = sum(
            r.get('count', 0) for r in tmdb if isinstance(r, dict) and not r.get('error')
        )
        # Lower TMDB score means LESS supply = BIGGER gap = BETTER for our prediction
        supply_score = min(100, max(0, 100 - (total_results * 8)))
        scores['tmdb'] = {
            'score': round(supply_score),
            'detail': f'{total_results} existing titles found (less = bigger demand gap)',
        }
        total_score += supply_score
        source_count += 1

    # Overall
    overall = round(total_score / max(source_count, 1))

    return {
        'overall_score': overall,
        'confidence': 'HIGH' if overall >= 70 else ('MODERATE' if overall >= 45 else 'LOW'),
        'sources_used': source_count,
        'source_scores': scores,
        'interpretation': (
            'Strong converging signals across multiple independent sources. High confidence in demand prediction.'
            if overall >= 70 else
            'Moderate signals detected. Demand is building but not yet at peak intensity.'
            if overall >= 45 else
            'Early-stage signals. Monitor for acceleration over the next 30-60 days.'
        ),
    }


# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
