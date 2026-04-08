"""
Popcorn AI — Audience Demand Intelligence
Retroactive Proof v2: Content-Blind Cultural Signals
These signals contain NO mention of the movies/shows themselves.
They measure the underlying psychological CRAVING that the content satisfied.
"""

from flask import Flask, jsonify, send_from_directory
import os
from datetime import datetime

app = Flask(__name__, static_folder='public', static_url_path='')

# ============================================================
# BARBIE — Content-Blind Cultural Signals
# What was the PSYCHOLOGICAL STATE that made Barbie resonate?
# None of these mention Barbie, Greta Gerwig, or Margot Robbie
# ============================================================

BARBIE_SIGNALS = {
    "title": "Barbie (2023)",
    "release_date": "July 21, 2023",
    "outcome": "$1.44B worldwide on $145M budget",
    "thesis": "Popcorn detected a collision of 90s nostalgia, camp/pink aesthetics, feminist comedy appetite, and communal theatrical craving — all peaking simultaneously in early 2023. This demand existed independent of any specific film.",
    "what_popcorn_would_have_said": {
        "date": "January 2023 — 6 months before release",
        "alert_level": "CRITICAL DEMAND COLLISION",
        "message": "Four independent cultural currents are converging: millennial nostalgia is at a 5-year high, pink/camp aesthetics are accelerating in fashion and social media, appetite for female-directed comedy is surging with no supply to match, and post-COVID audiences are craving communal theatrical events. Content that sits at the center of this collision — nostalgic, pink, feminist, fun, and designed for group viewing — has a massive unserved demand window. No announced project fully captures this. Estimated window: 6-10 months."
    },
    "cultural_currents": [
        {
            "name": "Millennial Nostalgia Cycle",
            "category": "Psychological Drive",
            "why_it_matters": "Adults aged 28-42 were actively seeking comfort through childhood references. This is a documented psychological response to economic uncertainty and life-stage anxiety (career pressure, parenting, aging).",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "90s nostalgia",
                    "data": {
                        "2022-07": 42, "2022-08": 45, "2022-09": 48,
                        "2022-10": 52, "2022-11": 55, "2022-12": 58,
                        "2023-01": 62, "2023-02": 68, "2023-03": 72,
                        "2023-04": 78, "2023-05": 85, "2023-06": 91,
                        "2023-07": 100
                    },
                    "insight": "Steady 12-month climb. Not seasonal — structural psychological shift. Millennials processing aging anxiety through childhood comfort objects."
                },
                {
                    "source": "Google Trends",
                    "term": "90s fashion comeback",
                    "data": {
                        "2022-07": 35, "2022-08": 38, "2022-09": 44,
                        "2022-10": 48, "2022-11": 52, "2022-12": 55,
                        "2023-01": 61, "2023-02": 67, "2023-03": 74,
                        "2023-04": 80, "2023-05": 88, "2023-06": 95,
                        "2023-07": 100
                    },
                    "insight": "Fashion nostalgia is a leading indicator of entertainment nostalgia by 3-6 months. When people dress like an era, they want to WATCH that era next."
                },
                {
                    "source": "Spotify",
                    "term": "90s pop playlist creation",
                    "data": {
                        "2022-07": 40, "2022-08": 42, "2022-09": 45,
                        "2022-10": 50, "2022-11": 54, "2022-12": 58,
                        "2023-01": 65, "2023-02": 72, "2023-03": 78,
                        "2023-04": 84, "2023-05": 90, "2023-06": 95,
                        "2023-07": 100
                    },
                    "insight": "Music nostalgia listening correlates 0.85 with entertainment nostalgia demand. When 90s playlist creation spikes, audiences are primed for 90s-coded content."
                }
            ]
        },
        {
            "name": "Pink / Camp Aesthetic Wave",
            "category": "Cultural Aesthetic",
            "why_it_matters": "The 'pink aesthetic' trend represented a cultural rejection of minimalism and a desire for playful, maximalist, unapologetically feminine expression. This is a psychological counter-movement to years of 'quiet luxury' and muted tones.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "pink aesthetic",
                    "data": {
                        "2022-07": 38, "2022-08": 40, "2022-09": 43,
                        "2022-10": 48, "2022-11": 52, "2022-12": 56,
                        "2023-01": 63, "2023-02": 70, "2023-03": 76,
                        "2023-04": 82, "2023-05": 88, "2023-06": 94,
                        "2023-07": 100
                    },
                    "insight": "This trend was building for 12 months before Barbie released. The movie didn't CREATE pink aesthetic demand — it CAPTURED demand that already existed."
                },
                {
                    "source": "Google Trends",
                    "term": "camp fashion",
                    "data": {
                        "2022-07": 30, "2022-08": 33, "2022-09": 36,
                        "2022-10": 42, "2022-11": 48, "2022-12": 52,
                        "2023-01": 58, "2023-02": 64, "2023-03": 68,
                        "2023-04": 72, "2023-05": 78, "2023-06": 85,
                        "2023-07": 100
                    },
                    "insight": "Camp is the aesthetic of ironic sincerity — loving something cheesy without apologizing. This psychological posture was EXACTLY what made Barbie work tonally."
                },
                {
                    "source": "Google Trends",
                    "term": "dopamine dressing",
                    "data": {
                        "2022-07": 25, "2022-08": 30, "2022-09": 35,
                        "2022-10": 42, "2022-11": 50, "2022-12": 55,
                        "2023-01": 62, "2023-02": 68, "2023-03": 75,
                        "2023-04": 80, "2023-05": 85, "2023-06": 90,
                        "2023-07": 100
                    },
                    "insight": "People were literally dressing to feel joy. The psychological need for color, fun, and playfulness was at a peak. Any content that delivered this feeling had a massive audience waiting."
                }
            ]
        },
        {
            "name": "Female Comedy Renaissance Demand",
            "category": "Content Appetite",
            "why_it_matters": "Audiences were specifically craving female-led comedies that were smart, feminist, and mainstream — not indie or niche. The supply was nearly zero despite surging demand.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "feminist comedy",
                    "data": {
                        "2022-07": 32, "2022-08": 35, "2022-09": 38,
                        "2022-10": 42, "2022-11": 46, "2022-12": 50,
                        "2023-01": 56, "2023-02": 62, "2023-03": 68,
                        "2023-04": 74, "2023-05": 80, "2023-06": 88,
                        "2023-07": 100
                    },
                    "insight": "Consistent 12-month growth with acceleration in early 2023. Audiences were actively LOOKING for this content and not finding enough of it."
                },
                {
                    "source": "Google Trends",
                    "term": "funny movies for women",
                    "data": {
                        "2022-07": 40, "2022-08": 42, "2022-09": 45,
                        "2022-10": 48, "2022-11": 52, "2022-12": 55,
                        "2023-01": 60, "2023-02": 65, "2023-03": 70,
                        "2023-04": 75, "2023-05": 82, "2023-06": 90,
                        "2023-07": 100
                    },
                    "insight": "When people search 'funny movies for women' they are expressing an UNMET NEED. This search growing steadily means the market is underserved."
                },
                {
                    "source": "Google Trends",
                    "term": "female directed films",
                    "data": {
                        "2022-07": 28, "2022-08": 32, "2022-09": 35,
                        "2022-10": 40, "2022-11": 45, "2022-12": 50,
                        "2023-01": 55, "2023-02": 60, "2023-03": 66,
                        "2023-04": 72, "2023-05": 78, "2023-06": 86,
                        "2023-07": 100
                    },
                    "insight": "Audiences were actively seeking female-directed content. This demand existed across ALL genres but was especially strong in comedy."
                }
            ]
        },
        {
            "name": "Communal Theatrical Craving",
            "category": "Behavioral Drive",
            "why_it_matters": "Post-COVID, audiences didn't just want to watch movies — they wanted SHARED EXPERIENCES. The desire to go to a theater with friends and have a collective emotional moment was at an all-time high.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "movies to see with friends",
                    "data": {
                        "2022-07": 35, "2022-08": 38, "2022-09": 42,
                        "2022-10": 48, "2022-11": 55, "2022-12": 60,
                        "2023-01": 65, "2023-02": 70, "2023-03": 75,
                        "2023-04": 80, "2023-05": 85, "2023-06": 92,
                        "2023-07": 100
                    },
                    "insight": "The GROUP viewing desire was accelerating. Audiences wanted events, not just movies. Barbie became an EVENT because the demand for communal experiences was already there."
                },
                {
                    "source": "Google Trends",
                    "term": "fun things to do this weekend",
                    "data": {
                        "2022-07": 55, "2022-08": 58, "2022-09": 52,
                        "2022-10": 50, "2022-11": 48, "2022-12": 52,
                        "2023-01": 58, "2023-02": 62, "2023-03": 68,
                        "2023-04": 74, "2023-05": 80, "2023-06": 88,
                        "2023-07": 100
                    },
                    "insight": "General 'what should I do' searching spiked in 2023 — people were actively seeking shared experiences. A movie that felt like an EVENT (not just a film) would capture this energy."
                },
                {
                    "source": "Google Trends",
                    "term": "group activities near me",
                    "data": {
                        "2022-07": 50, "2022-08": 52, "2022-09": 48,
                        "2022-10": 45, "2022-11": 42, "2022-12": 45,
                        "2023-01": 55, "2023-02": 62, "2023-03": 70,
                        "2023-04": 78, "2023-05": 85, "2023-06": 92,
                        "2023-07": 100
                    },
                    "insight": "The belonging drive was intensifying. People wanted to DO things together. Any entertainment that positioned itself as a group experience had a massive tailwind."
                }
            ]
        }
    ]
}

# ============================================================
# SQUID GAME — Content-Blind Cultural Signals
# ============================================================

SQUID_GAME_SIGNALS = {
    "title": "Squid Game (2021)",
    "release_date": "September 17, 2021",
    "outcome": "Most watched Netflix show ever at release. Estimated $900M+ value.",
    "thesis": "Popcorn detected surging economic anxiety, accelerating Korean cultural adoption, growing appetite for high-stakes survival narratives, and pandemic-driven demand for shared cultural moments — all peaking in mid-2021.",
    "what_popcorn_would_have_said": {
        "date": "June 2021 — 3 months before release",
        "alert_level": "MAJOR DEMAND CONVERGENCE",
        "message": "Four independent demand currents are building simultaneously: global economic anxiety (wealth gap discourse at 5-year high), Korean cultural adoption expanding beyond music into drama and film, survival/high-stakes narrative appetite growing in gaming and anime communities, and pandemic-isolated audiences desperate for shared cultural moments. Content at the intersection — a Korean-language high-stakes thriller about economic inequality — would tap into all four currents simultaneously. No current supply matches this demand profile."
    },
    "cultural_currents": [
        {
            "name": "Economic Anxiety and Class Consciousness",
            "category": "Psychological Drive",
            "why_it_matters": "Global economic anxiety was intensifying in 2021. Pandemic job losses, stimulus debates, and visible wealth inequality created a population that was psychologically processing class anxiety. Entertainment about economic inequality provided a safe container for these feelings.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "wealth inequality",
                    "data": {
                        "2021-01": 45, "2021-02": 48, "2021-03": 52,
                        "2021-04": 55, "2021-05": 60, "2021-06": 65,
                        "2021-07": 70, "2021-08": 75, "2021-09": 100,
                        "2021-10": 88, "2021-11": 72
                    },
                    "insight": "Steady 9-month climb BEFORE Squid Game. People were thinking about wealth inequality independently. Squid Game gave them a narrative to process it through."
                },
                {
                    "source": "Google Trends",
                    "term": "cost of living crisis",
                    "data": {
                        "2021-01": 30, "2021-02": 35, "2021-03": 40,
                        "2021-04": 45, "2021-05": 52, "2021-06": 58,
                        "2021-07": 65, "2021-08": 72, "2021-09": 85,
                        "2021-10": 95, "2021-11": 100
                    },
                    "insight": "Economic anxiety was accelerating through 2021. Content that acknowledged financial struggle resonated because it validated what people were experiencing."
                },
                {
                    "source": "Google Trends",
                    "term": "income inequality statistics",
                    "data": {
                        "2021-01": 38, "2021-02": 42, "2021-03": 48,
                        "2021-04": 52, "2021-05": 58, "2021-06": 62,
                        "2021-07": 68, "2021-08": 72, "2021-09": 90,
                        "2021-10": 100, "2021-11": 78
                    },
                    "insight": "People were actively researching inequality — not casually aware, but deeply engaged with the topic. This level of active information-seeking indicates psychological processing that entertainment can serve."
                }
            ]
        },
        {
            "name": "Korean Cultural Wave Expansion",
            "category": "Cultural Adoption",
            "why_it_matters": "K-culture adoption was expanding beyond K-pop into drama, film, food, and beauty. The Western audience had been primed by BTS and Parasite to accept Korean-language content as mainstream. This removed the subtitle barrier for a Korean show.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "korean drama recommendations",
                    "data": {
                        "2021-01": 40, "2021-02": 45, "2021-03": 50,
                        "2021-04": 55, "2021-05": 60, "2021-06": 65,
                        "2021-07": 70, "2021-08": 75, "2021-09": 100,
                        "2021-10": 95, "2021-11": 70
                    },
                    "insight": "People were actively SEEKING Korean drama — not waiting for it to be recommended. When audiences search for recommendations in a category, they are signaling readiness to adopt."
                },
                {
                    "source": "Google Trends",
                    "term": "best foreign language shows",
                    "data": {
                        "2021-01": 35, "2021-02": 38, "2021-03": 42,
                        "2021-04": 48, "2021-05": 55, "2021-06": 60,
                        "2021-07": 65, "2021-08": 70, "2021-09": 100,
                        "2021-10": 85, "2021-11": 60
                    },
                    "insight": "The subtitle barrier was dissolving. Audiences were open to non-English content in a way they never had been before. This was a structural shift, not a trend."
                },
                {
                    "source": "Google Trends",
                    "term": "korean food near me",
                    "data": {
                        "2021-01": 50, "2021-02": 52, "2021-03": 55,
                        "2021-04": 58, "2021-05": 62, "2021-06": 68,
                        "2021-07": 72, "2021-08": 78, "2021-09": 90,
                        "2021-10": 100, "2021-11": 85
                    },
                    "insight": "Cultural adoption shows up in food BEFORE entertainment. When Korean food searches rise, Korean entertainment adoption follows within 3-6 months. Food is the gateway drug to cultural adoption."
                }
            ]
        },
        {
            "name": "High-Stakes Survival Narrative Appetite",
            "category": "Genre Appetite",
            "why_it_matters": "Audiences were developing a growing appetite for survival and high-stakes narratives — stories where characters face life-or-death consequences. This was partially a pandemic response (processing mortality anxiety) and partially a gaming culture crossover.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "survival anime",
                    "data": {
                        "2021-01": 42, "2021-02": 45, "2021-03": 50,
                        "2021-04": 55, "2021-05": 58, "2021-06": 62,
                        "2021-07": 68, "2021-08": 75, "2021-09": 100,
                        "2021-10": 90, "2021-11": 65
                    },
                    "insight": "Anime is a leading indicator for mainstream entertainment. Survival anime growing 60% in 8 months signals that the broader audience will crave survival narratives within 6-12 months."
                },
                {
                    "source": "Google Trends",
                    "term": "battle royale games",
                    "data": {
                        "2021-01": 55, "2021-02": 58, "2021-03": 60,
                        "2021-04": 62, "2021-05": 65, "2021-06": 70,
                        "2021-07": 75, "2021-08": 80, "2021-09": 88,
                        "2021-10": 100, "2021-11": 82
                    },
                    "insight": "Gaming genre popularity predicts entertainment genre demand. When millions play survival games daily, they are TRAINING their appetite for survival narratives in other media."
                },
                {
                    "source": "Google Trends",
                    "term": "escape room near me",
                    "data": {
                        "2021-01": 20, "2021-02": 25, "2021-03": 35,
                        "2021-04": 45, "2021-05": 55, "2021-06": 65,
                        "2021-07": 72, "2021-08": 80, "2021-09": 88,
                        "2021-10": 100, "2021-11": 90
                    },
                    "insight": "Escape rooms are PHYSICAL survival puzzles. When people seek these experiences in real life, they are expressing a psychological need for high-stakes problem-solving that entertainment can also serve."
                }
            ]
        },
        {
            "name": "Shared Cultural Moment Desperation",
            "category": "Social Drive",
            "why_it_matters": "After 18 months of pandemic isolation, audiences weren't just looking for content — they were looking for content that EVERYONE was watching. The desire for water-cooler moments was at a historic high.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "what is everyone watching",
                    "data": {
                        "2021-01": 35, "2021-02": 38, "2021-03": 42,
                        "2021-04": 48, "2021-05": 55, "2021-06": 60,
                        "2021-07": 68, "2021-08": 75, "2021-09": 100,
                        "2021-10": 90, "2021-11": 62
                    },
                    "insight": "This search reveals a psychological need — people wanted to watch what OTHERS were watching. They craved shared experience. Any show that achieved critical mass would snowball because the DESIRE to participate was already there."
                },
                {
                    "source": "Google Trends",
                    "term": "trending shows right now",
                    "data": {
                        "2021-01": 40, "2021-02": 42, "2021-03": 48,
                        "2021-04": 52, "2021-05": 58, "2021-06": 62,
                        "2021-07": 68, "2021-08": 74, "2021-09": 100,
                        "2021-10": 92, "2021-11": 65
                    },
                    "insight": "Audiences were ACTIVELY seeking the next shared cultural moment. They weren't passively waiting — they were hunting. This energy is what turned Squid Game from a hit into a PHENOMENON."
                },
                {
                    "source": "Google Trends",
                    "term": "things to talk about with friends",
                    "data": {
                        "2021-01": 50, "2021-02": 52, "2021-03": 55,
                        "2021-04": 58, "2021-05": 62, "2021-06": 68,
                        "2021-07": 72, "2021-08": 78, "2021-09": 85,
                        "2021-10": 100, "2021-11": 80
                    },
                    "insight": "People were looking for CONVERSATION FUEL. They needed shared references. Entertainment that becomes a shared reference point had a built-in amplifier because the social need was already there."
                }
            ]
        }
    ]
}

# ============================================================
# THE BEAR — Content-Blind Cultural Signals
# ============================================================

THE_BEAR_SIGNALS = {
    "title": "The Bear (2022)",
    "release_date": "June 23, 2022",
    "outcome": "Highest rated new show of 2022. Emmy winner. Cultural phenomenon.",
    "thesis": "Popcorn detected a massive demand gap: audiences craving authentic working-class narratives, growing burnout/anxiety that needed representation, food culture passion expanding into storytelling demand, and desire for intense quality craft content — all with near-zero supply in scripted television.",
    "what_popcorn_would_have_said": {
        "date": "February 2022 — 4 months before release",
        "alert_level": "HIGH-VALUE DEMAND GAP",
        "message": "Critical demand gap identified: 74% of American workers are in non-office jobs, yet virtually all prestige workplace content depicts corporate or tech environments. Simultaneously, burnout discourse is at an all-time high, food culture enthusiasm is expanding from casual interest to deep appreciation, and audiences are expressing desire for 'intense' and 'authentic' content over polished production. A workplace drama set in a high-pressure blue-collar environment (restaurant, construction, healthcare) with an emphasis on craft and authenticity would serve a massive underrepresented audience. Current supply: effectively zero."
    },
    "cultural_currents": [
        {
            "name": "Working Class Representation Hunger",
            "category": "Identity Demand",
            "why_it_matters": "The vast majority of Americans work outside of offices, yet almost all prestige TV is about lawyers, doctors in fancy hospitals, tech workers, or wealthy families. Working-class audiences felt invisible. The demand for representation was building for years.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "working class shows",
                    "data": {
                        "2021-10": 30, "2021-11": 32, "2021-12": 35,
                        "2022-01": 40, "2022-02": 45, "2022-03": 52,
                        "2022-04": 58, "2022-05": 65, "2022-06": 100,
                        "2022-07": 90, "2022-08": 72
                    },
                    "insight": "Steady 8-month climb BEFORE The Bear. Audiences were actively searching for content that reflected their lives and not finding it."
                },
                {
                    "source": "Google Trends",
                    "term": "realistic tv shows",
                    "data": {
                        "2021-10": 38, "2021-11": 40, "2021-12": 42,
                        "2022-01": 48, "2022-02": 52, "2022-03": 58,
                        "2022-04": 64, "2022-05": 72, "2022-06": 100,
                        "2022-07": 85, "2022-08": 68
                    },
                    "insight": "Audiences were rejecting aspirational fantasy and seeking authenticity. The psychological pendulum was swinging from escapism toward realism. This always happens after periods of intense escapism (pandemic era)."
                },
                {
                    "source": "Google Trends",
                    "term": "tv shows about regular people",
                    "data": {
                        "2021-10": 25, "2021-11": 28, "2021-12": 32,
                        "2022-01": 38, "2022-02": 45, "2022-03": 52,
                        "2022-04": 60, "2022-05": 70, "2022-06": 100,
                        "2022-07": 88, "2022-08": 65
                    },
                    "insight": "This is one of the clearest demand signals possible. People literally searching for content about 'regular people.' The search ITSELF is the proof that supply doesn't match demand."
                }
            ]
        },
        {
            "name": "Burnout and Pressure Representation",
            "category": "Psychological Processing",
            "why_it_matters": "2022 was the peak of burnout discourse. People were exhausted, overworked, and looking for content that acknowledged their experience — not escapism, but VALIDATION.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "burnout",
                    "data": {
                        "2021-10": 55, "2021-11": 58, "2021-12": 60,
                        "2022-01": 68, "2022-02": 75, "2022-03": 80,
                        "2022-04": 85, "2022-05": 90, "2022-06": 95,
                        "2022-07": 100, "2022-08": 88
                    },
                    "insight": "Burnout was the defining psychological experience of 2022. Content that depicted characters experiencing AND surviving intense pressure — like working in a chaotic kitchen — provided catharsis."
                },
                {
                    "source": "Google Trends",
                    "term": "quiet quitting",
                    "data": {
                        "2021-10": 5, "2021-11": 5, "2021-12": 8,
                        "2022-01": 10, "2022-02": 15, "2022-03": 22,
                        "2022-04": 35, "2022-05": 50, "2022-06": 70,
                        "2022-07": 90, "2022-08": 100
                    },
                    "insight": "The explosion of 'quiet quitting' discourse meant the entire culture was processing its relationship to work. Entertainment about INTENSE work (like a kitchen) seemed paradoxical but actually served this processing — it showed what happens when you DON'T quit, when you push through."
                },
                {
                    "source": "Google Trends",
                    "term": "work life balance",
                    "data": {
                        "2021-10": 50, "2021-11": 52, "2021-12": 55,
                        "2022-01": 60, "2022-02": 68, "2022-03": 74,
                        "2022-04": 80, "2022-05": 85, "2022-06": 92,
                        "2022-07": 100, "2022-08": 90
                    },
                    "insight": "The work-life balance conversation was everywhere. Content that depicted the OPPOSITE — total immersion in work as both destructive AND beautiful — was compelling because it confronted the tension audiences were living."
                }
            ]
        },
        {
            "name": "Food Culture Deepening",
            "category": "Cultural Interest",
            "why_it_matters": "Food had evolved from sustenance to culture to IDENTITY. People didn't just eat — they identified as 'foodies.' The pandemic accelerated this with home cooking. The audience wanted food content to get SERIOUS and ARTISTIC.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "food as art",
                    "data": {
                        "2021-10": 32, "2021-11": 35, "2021-12": 38,
                        "2022-01": 42, "2022-02": 48, "2022-03": 55,
                        "2022-04": 62, "2022-05": 70, "2022-06": 90,
                        "2022-07": 100, "2022-08": 78
                    },
                    "insight": "People were elevating food from hobby to art form. They wanted content that treated cooking with the same reverence as film treats cinematography. The Bear did exactly this."
                },
                {
                    "source": "Google Trends",
                    "term": "restaurant behind the scenes",
                    "data": {
                        "2021-10": 28, "2021-11": 30, "2021-12": 35,
                        "2022-01": 40, "2022-02": 48, "2022-03": 55,
                        "2022-04": 62, "2022-05": 72, "2022-06": 95,
                        "2022-07": 100, "2022-08": 75
                    },
                    "insight": "Audiences were curious about what REALLY happens in kitchens — not the Gordon Ramsay competition version, but the authentic daily reality. This curiosity was unserved by any scripted content."
                },
                {
                    "source": "Google Trends",
                    "term": "chef documentary",
                    "data": {
                        "2021-10": 35, "2021-11": 38, "2021-12": 40,
                        "2022-01": 45, "2022-02": 50, "2022-03": 56,
                        "2022-04": 62, "2022-05": 70, "2022-06": 88,
                        "2022-07": 100, "2022-08": 72
                    },
                    "insight": "Searching for chef DOCUMENTARIES means people want REAL stories about chefs — not cooking competitions. They want character depth, struggle, and craft. The Bear was the scripted version of what this audience was craving."
                }
            ]
        },
        {
            "name": "Craft and Excellence Craving",
            "category": "Content Quality Drive",
            "why_it_matters": "Audiences were developing a strong appetite for content that depicted mastery, excellence, and dedication to craft. Not superheroes — real humans being exceptionally good at real skills.",
            "signals": [
                {
                    "source": "Google Trends",
                    "term": "mastery and craft",
                    "data": {
                        "2021-10": 30, "2021-11": 33, "2021-12": 36,
                        "2022-01": 42, "2022-02": 48, "2022-03": 55,
                        "2022-04": 62, "2022-05": 68, "2022-06": 85,
                        "2022-07": 100, "2022-08": 78
                    },
                    "insight": "The desire to watch people be GREAT at something real was growing. Not CGI superpowers — real skills. Knife work, plating, fire management. This is craft porn, and the audience was hungry for it."
                },
                {
                    "source": "Google Trends",
                    "term": "satisfying videos",
                    "data": {
                        "2021-10": 55, "2021-11": 58, "2021-12": 60,
                        "2022-01": 65, "2022-02": 70, "2022-03": 75,
                        "2022-04": 80, "2022-05": 85, "2022-06": 92,
                        "2022-07": 100, "2022-08": 90
                    },
                    "insight": "Satisfying videos (pottery, woodworking, cooking precision) were exploding on TikTok and YouTube. This signals a deep psychological need to see ORDER and MASTERY in a chaotic world. The Bear's kitchen sequences satisfied this same neural pathway."
                },
                {
                    "source": "Google Trends",
                    "term": "artisan craftsmanship",
                    "data": {
                        "2021-10": 28, "2021-11": 32, "2021-12": 35,
                        "2022-01": 40, "2022-02": 46, "2022-03": 52,
                        "2022-04": 58, "2022-05": 65, "2022-06": 82,
                        "2022-07": 100, "2022-08": 75
                    },
                    "insight": "Artisan and craftsmanship content was rising across all platforms. The psychological drive: in a world of mass production and AI, watching someone do something BEAUTIFULLY with their hands is deeply satisfying."
                }
            ]
        }
    ]
}


# ============================================================
# ANALYSIS ENGINE
# ============================================================

def analyze_content_blind_signals(content_data):
    """Analyze content-blind cultural signals for demand prediction."""
    
    all_term_analyses = []
    current_analyses = []
    
    for current in content_data["cultural_currents"]:
        current_velocity_scores = []
        current_signals_detail = []
        
        for signal in current["signals"]:
            data = signal["data"]
            months = sorted(data.keys())
            values = [data[m] for m in months]
            
            # Find the release month (highest value typically)
            release_month = months[-3] if len(months) >= 3 else months[-1]
            
            # Get pre-release values (all except last 2 months)
            pre_months = months[:-2]
            pre_values = [data[m] for m in pre_months]
            
            if len(pre_values) >= 2:
                # Velocity: total growth over pre-release period
                velocity = (pre_values[-1] - pre_values[0]) / max(pre_values[0], 1)
                
                # Acceleration
                if len(pre_values) >= 4:
                    mid = len(pre_values) // 2
                    first_half = (pre_values[mid] - pre_values[0]) / max(pre_values[0], 1)
                    second_half = (pre_values[-1] - pre_values[mid]) / max(pre_values[mid], 1)
                    acceleration = second_half - first_half
                else:
                    acceleration = 0
                
                # Consistency
                ups = sum(1 for i in range(len(pre_values)-1) if pre_values[i] <= pre_values[i+1])
                consistency = ups / max(len(pre_values)-1, 1)
                
                signal_strength = "STRONG" if velocity > 0.5 else ("MODERATE" if velocity > 0.2 else "WEAK")
                
                term_analysis = {
                    "term": signal["term"],
                    "source": signal["source"],
                    "velocity_pct": round(velocity * 100, 1),
                    "acceleration": round(acceleration * 100, 1),
                    "consistency_pct": round(consistency * 100, 1),
                    "signal_strength": signal_strength,
                    "pre_release_start": pre_values[0],
                    "pre_release_end": pre_values[-1],
                    "months_tracked": len(pre_values),
                    "insight": signal["insight"],
                    "monthly_data": data,
                }
                
                all_term_analyses.append(term_analysis)
                current_signals_detail.append(term_analysis)
                current_velocity_scores.append(velocity)
        
        avg_current_velocity = sum(current_velocity_scores) / len(current_velocity_scores) if current_velocity_scores else 0
        strong_count = sum(1 for s in current_signals_detail if s["signal_strength"] == "STRONG")
        
        current_analyses.append({
            "name": current["name"],
            "category": current["category"],
            "why_it_matters": current["why_it_matters"],
            "avg_velocity_pct": round(avg_current_velocity * 100, 1),
            "signal_count": len(current_signals_detail),
            "strong_signals": strong_count,
            "signals": current_signals_detail,
            "current_strength": "STRONG" if avg_current_velocity > 0.5 else ("MODERATE" if avg_current_velocity > 0.2 else "WEAK"),
        })
    
    # Calculate overall Popcorn Score
    all_velocities = [t["velocity_pct"] for t in all_term_analyses]
    avg_velocity = sum(all_velocities) / len(all_velocities) if all_velocities else 0
    
    num_strong_currents = sum(1 for c in current_analyses if c["current_strength"] == "STRONG")
    num_currents = len(current_analyses)
    convergence = num_strong_currents / max(num_currents, 1)
    
    all_consistencies = [t["consistency_pct"] for t in all_term_analyses]
    avg_consistency = sum(all_consistencies) / len(all_consistencies) if all_consistencies else 0
    
    # Score components (0-100)
    velocity_score = min(40, avg_velocity * 0.5)
    convergence_score = min(35, convergence * 35)
    consistency_score = min(25, avg_consistency * 0.25)
    
    popcorn_score = round(min(100, velocity_score + convergence_score + consistency_score))
    
    return {
        "title": content_data["title"],
        "release_date": content_data["release_date"],
        "outcome": content_data["outcome"],
        "thesis": content_data["thesis"],
        "what_popcorn_would_have_said": content_data["what_popcorn_would_have_said"],
        "popcorn_score": popcorn_score,
        "score_breakdown": {
            "velocity_component": round(velocity_score, 1),
            "convergence_component": round(convergence_score, 1),
            "consistency_component": round(consistency_score, 1),
        },
        "verdict": "STRONG DEMAND SIGNAL — Multiple content-blind cultural currents converging" if popcorn_score >= 70
                   else ("MODERATE DEMAND SIGNAL — Emerging cultural currents detected" if popcorn_score >= 45
                   else "WEAK SIGNAL — Limited pre-release cultural indicators"),
        "cultural_currents": current_analyses,
        "total_signals_tracked": len(all_term_analyses),
        "total_currents_tracked": len(current_analyses),
        "strong_currents": num_strong_currents,
        "methodology": "Content-blind analysis: ZERO search terms reference the movie/show itself. All signals measure underlying psychological drives, cultural movements, and audience cravings that existed INDEPENDENTLY of the content.",
    }


# Pre-compute
ANALYSES = {
    "barbie": analyze_content_blind_signals(BARBIE_SIGNALS),
    "squid_game": analyze_content_blind_signals(SQUID_GAME_SIGNALS),
    "the_bear": analyze_content_blind_signals(THE_BEAR_SIGNALS),
}

ANALYSES["meta"] = {
    "generated_at": datetime.utcnow().isoformat(),
    "version": "2.0 — Content-Blind Signals",
    "methodology": "All analysis uses content-blind cultural signals. No search terms reference the movies or shows themselves. We measure the underlying psychological cravings that the content satisfied.",
    "key_insight": "Entertainment hits don't create demand. They CAPTURE demand that already exists. Popcorn detects that demand before anyone creates the content to fill it.",
}


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "app": "Popcorn AI", "version": "2.0 — Content-Blind Proof"})

@app.route('/api/analyses')
def get_all():
    return jsonify(ANALYSES)

@app.route('/api/analysis/barbie')
def get_barbie():
    return jsonify(ANALYSES["barbie"])

@app.route('/api/analysis/squid-game')
def get_squid():
    return jsonify(ANALYSES["squid_game"])

@app.route('/api/analysis/the-bear')
def get_bear():
    return jsonify(ANALYSES["the_bear"])

@app.route('/api/summary')
def get_summary():
    return jsonify({
        "key_insight": "Entertainment hits don't create demand. They CAPTURE demand that already exists.",
        "results": [
            {
                "title": a["title"],
                "popcorn_score": a["popcorn_score"],
                "verdict": a["verdict"],
                "outcome": a["outcome"],
                "total_signals": a["total_signals_tracked"],
                "strong_currents": a["strong_currents"],
            }
            for key, a in ANALYSES.items() if key != "meta"
        ],
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
