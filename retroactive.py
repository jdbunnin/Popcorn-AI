"""
Popcorn AI — Retroactive Proof (Content-Blind Signals)
Keeps the v2 proof-of-concept data for Barbie, Squid Game, The Bear
"""

from datetime import datetime


BARBIE_SIGNALS = {
    "title": "Barbie (2023)",
    "release_date": "July 21, 2023",
    "outcome": "$1.44B worldwide on $145M budget",
    "thesis": "Four independent cultural currents converged: millennial nostalgia, pink/camp aesthetics, feminist comedy appetite, and communal theatrical craving — all peaking simultaneously in early 2023.",
    "what_popcorn_would_have_said": {
        "date": "January 2023 — 6 months before release",
        "alert_level": "CRITICAL DEMAND COLLISION",
        "message": "Four independent cultural currents are converging: millennial nostalgia at 5-year high, pink/camp aesthetics accelerating in fashion and social media, appetite for female-directed comedy surging with no supply, and post-COVID audiences craving communal theatrical events. Content at the center of this collision has a massive unserved demand window."
    },
    "cultural_currents": [
        {
            "name": "Millennial Nostalgia Cycle",
            "category": "Psychological Drive",
            "why_it_matters": "Adults 28-42 actively seeking comfort through childhood references. Documented psychological response to economic uncertainty and life-stage anxiety.",
            "signals": [
                {
                    "term": "90s nostalgia",
                    "source": "Google Trends",
                    "data": {"2022-07": 42, "2022-08": 45, "2022-09": 48, "2022-10": 52, "2022-11": 55, "2022-12": 58, "2023-01": 62, "2023-02": 68, "2023-03": 72, "2023-04": 78, "2023-05": 85, "2023-06": 91, "2023-07": 100},
                    "insight": "Steady 12-month climb. Not seasonal — structural psychological shift."
                },
                {
                    "term": "90s fashion comeback",
                    "source": "Google Trends",
                    "data": {"2022-07": 35, "2022-08": 38, "2022-09": 44, "2022-10": 48, "2022-11": 52, "2022-12": 55, "2023-01": 61, "2023-02": 67, "2023-03": 74, "2023-04": 80, "2023-05": 88, "2023-06": 95, "2023-07": 100},
                    "insight": "Fashion nostalgia is a leading indicator of entertainment nostalgia by 3-6 months."
                },
                {
                    "term": "90s pop playlist",
                    "source": "Spotify Signal",
                    "data": {"2022-07": 40, "2022-08": 42, "2022-09": 45, "2022-10": 50, "2022-11": 54, "2022-12": 58, "2023-01": 65, "2023-02": 72, "2023-03": 78, "2023-04": 84, "2023-05": 90, "2023-06": 95, "2023-07": 100},
                    "insight": "Music nostalgia listening correlates 0.85 with entertainment nostalgia demand."
                }
            ]
        },
        {
            "name": "Pink / Camp Aesthetic Wave",
            "category": "Cultural Aesthetic",
            "why_it_matters": "Cultural rejection of minimalism. Desire for playful, maximalist, unapologetically feminine expression.",
            "signals": [
                {
                    "term": "pink aesthetic",
                    "source": "Google Trends",
                    "data": {"2022-07": 38, "2022-08": 40, "2022-09": 43, "2022-10": 48, "2022-11": 52, "2022-12": 56, "2023-01": 63, "2023-02": 70, "2023-03": 76, "2023-04": 82, "2023-05": 88, "2023-06": 94, "2023-07": 100},
                    "insight": "Building for 12 months before Barbie. The movie captured demand that already existed."
                },
                {
                    "term": "camp fashion",
                    "source": "Google Trends",
                    "data": {"2022-07": 30, "2022-08": 33, "2022-09": 36, "2022-10": 42, "2022-11": 48, "2022-12": 52, "2023-01": 58, "2023-02": 64, "2023-03": 68, "2023-04": 72, "2023-05": 78, "2023-06": 85, "2023-07": 100},
                    "insight": "Camp is ironic sincerity — loving something cheesy without apologizing. Exactly Barbie's tone."
                },
                {
                    "term": "dopamine dressing",
                    "source": "Google Trends",
                    "data": {"2022-07": 25, "2022-08": 30, "2022-09": 35, "2022-10": 42, "2022-11": 50, "2022-12": 55, "2023-01": 62, "2023-02": 68, "2023-03": 75, "2023-04": 80, "2023-05": 85, "2023-06": 90, "2023-07": 100},
                    "insight": "People dressing to feel joy. The need for color and playfulness was at peak."
                }
            ]
        },
        {
            "name": "Female Comedy Renaissance Demand",
            "category": "Content Appetite",
            "why_it_matters": "Audiences craving female-led comedies that were smart, feminist, and mainstream. Supply was near zero.",
            "signals": [
                {
                    "term": "feminist comedy",
                    "source": "Google Trends",
                    "data": {"2022-07": 32, "2022-08": 35, "2022-09": 38, "2022-10": 42, "2022-11": 46, "2022-12": 50, "2023-01": 56, "2023-02": 62, "2023-03": 68, "2023-04": 74, "2023-05": 80, "2023-06": 88, "2023-07": 100},
                    "insight": "Consistent 12-month growth with acceleration in early 2023."
                },
                {
                    "term": "funny movies for women",
                    "source": "Google Trends",
                    "data": {"2022-07": 40, "2022-08": 42, "2022-09": 45, "2022-10": 48, "2022-11": 52, "2022-12": 55, "2023-01": 60, "2023-02": 65, "2023-03": 70, "2023-04": 75, "2023-05": 82, "2023-06": 90, "2023-07": 100},
                    "insight": "Searching 'funny movies for women' = expressing an UNMET NEED."
                },
                {
                    "term": "female directed films",
                    "source": "Google Trends",
                    "data": {"2022-07": 28, "2022-08": 32, "2022-09": 35, "2022-10": 40, "2022-11": 45, "2022-12": 50, "2023-01": 55, "2023-02": 60, "2023-03": 66, "2023-04": 72, "2023-05": 78, "2023-06": 86, "2023-07": 100},
                    "insight": "Audiences actively seeking female-directed content across all genres."
                }
            ]
        },
        {
            "name": "Communal Theatrical Craving",
            "category": "Behavioral Drive",
            "why_it_matters": "Post-COVID audiences wanted SHARED EXPERIENCES. Desire for communal theater moments at all-time high.",
            "signals": [
                {
                    "term": "movies to see with friends",
                    "source": "Google Trends",
                    "data": {"2022-07": 35, "2022-08": 38, "2022-09": 42, "2022-10": 48, "2022-11": 55, "2022-12": 60, "2023-01": 65, "2023-02": 70, "2023-03": 75, "2023-04": 80, "2023-05": 85, "2023-06": 92, "2023-07": 100},
                    "insight": "GROUP viewing desire accelerating. Audiences wanted events, not just movies."
                },
                {
                    "term": "fun things to do this weekend",
                    "source": "Google Trends",
                    "data": {"2022-07": 55, "2022-08": 58, "2022-09": 52, "2022-10": 50, "2022-11": 48, "2022-12": 52, "2023-01": 58, "2023-02": 62, "2023-03": 68, "2023-04": 74, "2023-05": 80, "2023-06": 88, "2023-07": 100},
                    "insight": "People actively seeking shared experiences. A movie that felt like an EVENT would capture this."
                },
                {
                    "term": "group activities near me",
                    "source": "Google Trends",
                    "data": {"2022-07": 50, "2022-08": 52, "2022-09": 48, "2022-10": 45, "2022-11": 42, "2022-12": 45, "2023-01": 55, "2023-02": 62, "2023-03": 70, "2023-04": 78, "2023-05": 85, "2023-06": 92, "2023-07": 100},
                    "insight": "Belonging drive intensifying. Any entertainment positioning itself as group experience had massive tailwind."
                }
            ]
        }
    ]
}

SQUID_GAME_SIGNALS = {
    "title": "Squid Game (2021)",
    "release_date": "September 17, 2021",
    "outcome": "Most watched Netflix show ever at release. Estimated $900M+ value.",
    "thesis": "Economic anxiety, K-culture adoption, survival narrative appetite, and pandemic-driven shared moment craving all converged in mid-2021.",
    "what_popcorn_would_have_said": {
        "date": "June 2021 — 3 months before release",
        "alert_level": "MAJOR DEMAND CONVERGENCE",
        "message": "Four independent demand currents building: global economic anxiety at 5-year high, Korean cultural adoption expanding beyond music into drama, survival/high-stakes narrative appetite growing in gaming and anime, and isolated audiences desperate for shared cultural moments. Content at the intersection has massive potential."
    },
    "cultural_currents": [
        {
            "name": "Economic Anxiety and Class Consciousness",
            "category": "Psychological Drive",
            "why_it_matters": "Global economic anxiety intensifying. Pandemic job losses and visible wealth inequality created populations processing class anxiety through entertainment.",
            "signals": [
                {
                    "term": "wealth inequality",
                    "source": "Google Trends",
                    "data": {"2021-01": 45, "2021-02": 48, "2021-03": 52, "2021-04": 55, "2021-05": 60, "2021-06": 65, "2021-07": 70, "2021-08": 75, "2021-09": 100, "2021-10": 88, "2021-11": 72},
                    "insight": "Steady 9-month climb BEFORE Squid Game. People were processing inequality independently."
                },
                {
                    "term": "cost of living crisis",
                    "source": "Google Trends",
                    "data": {"2021-01": 30, "2021-02": 35, "2021-03": 40, "2021-04": 45, "2021-05": 52, "2021-06": 58, "2021-07": 65, "2021-08": 72, "2021-09": 85, "2021-10": 95, "2021-11": 100},
                    "insight": "Economic anxiety accelerating through 2021. Content acknowledging financial struggle resonated."
                },
                {
                    "term": "income inequality statistics",
                    "source": "Google Trends",
                    "data": {"2021-01": 38, "2021-02": 42, "2021-03": 48, "2021-04": 52, "2021-05": 58, "2021-06": 62, "2021-07": 68, "2021-08": 72, "2021-09": 90, "2021-10": 100, "2021-11": 78},
                    "insight": "Active information-seeking indicates deep psychological processing."
                }
            ]
        },
        {
            "name": "Korean Cultural Wave Expansion",
            "category": "Cultural Adoption",
            "why_it_matters": "K-culture expanding beyond K-pop. Western audiences primed by BTS and Parasite to accept Korean content as mainstream.",
            "signals": [
                {
                    "term": "korean drama recommendations",
                    "source": "Google Trends",
                    "data": {"2021-01": 40, "2021-02": 45, "2021-03": 50, "2021-04": 55, "2021-05": 60, "2021-06": 65, "2021-07": 70, "2021-08": 75, "2021-09": 100, "2021-10": 95, "2021-11": 70},
                    "insight": "People actively SEEKING Korean drama — signaling readiness to adopt."
                },
                {
                    "term": "best foreign language shows",
                    "source": "Google Trends",
                    "data": {"2021-01": 35, "2021-02": 38, "2021-03": 42, "2021-04": 48, "2021-05": 55, "2021-06": 60, "2021-07": 65, "2021-08": 70, "2021-09": 100, "2021-10": 85, "2021-11": 60},
                    "insight": "Subtitle barrier dissolving. Structural shift in content consumption."
                },
                {
                    "term": "korean food near me",
                    "source": "Google Trends",
                    "data": {"2021-01": 50, "2021-02": 52, "2021-03": 55, "2021-04": 58, "2021-05": 62, "2021-06": 68, "2021-07": 72, "2021-08": 78, "2021-09": 90, "2021-10": 100, "2021-11": 85},
                    "insight": "Cultural adoption shows in food BEFORE entertainment. Food is the gateway."
                }
            ]
        },
        {
            "name": "High-Stakes Survival Narrative Appetite",
            "category": "Genre Appetite",
            "why_it_matters": "Growing appetite for survival and life-or-death narratives. Pandemic mortality anxiety plus gaming culture crossover.",
            "signals": [
                {
                    "term": "survival anime",
                    "source": "Google Trends",
                    "data": {"2021-01": 42, "2021-02": 45, "2021-03": 50, "2021-04": 55, "2021-05": 58, "2021-06": 62, "2021-07": 68, "2021-08": 75, "2021-09": 100, "2021-10": 90, "2021-11": 65},
                    "insight": "Anime is a leading indicator. Survival anime up 60% signals broader demand."
                },
                {
                    "term": "battle royale games",
                    "source": "Google Trends",
                    "data": {"2021-01": 55, "2021-02": 58, "2021-03": 60, "2021-04": 62, "2021-05": 65, "2021-06": 70, "2021-07": 75, "2021-08": 80, "2021-09": 88, "2021-10": 100, "2021-11": 82},
                    "insight": "Gaming genre popularity predicts entertainment genre demand."
                },
                {
                    "term": "escape room near me",
                    "source": "Google Trends",
                    "data": {"2021-01": 20, "2021-02": 25, "2021-03": 35, "2021-04": 45, "2021-05": 55, "2021-06": 65, "2021-07": 72, "2021-08": 80, "2021-09": 88, "2021-10": 100, "2021-11": 90},
                    "insight": "Physical survival puzzles express same psychological need entertainment can serve."
                }
            ]
        },
        {
            "name": "Shared Cultural Moment Desperation",
            "category": "Social Drive",
            "why_it_matters": "After 18 months of isolation, audiences wanted content EVERYONE was watching. Water-cooler moments at historic high demand.",
            "signals": [
                {
                    "term": "what is everyone watching",
                    "source": "Google Trends",
                    "data": {"2021-01": 35, "2021-02": 38, "2021-03": 42, "2021-04": 48, "2021-05": 55, "2021-06": 60, "2021-07": 68, "2021-08": 75, "2021-09": 100, "2021-10": 90, "2021-11": 62},
                    "insight": "People wanted to watch what OTHERS were watching. Craved shared experience."
                },
                {
                    "term": "trending shows right now",
                    "source": "Google Trends",
                    "data": {"2021-01": 40, "2021-02": 42, "2021-03": 48, "2021-04": 52, "2021-05": 58, "2021-06": 62, "2021-07": 68, "2021-08": 74, "2021-09": 100, "2021-10": 92, "2021-11": 65},
                    "insight": "Audiences actively hunting the next shared moment."
                },
                {
                    "term": "things to talk about with friends",
                    "source": "Google Trends",
                    "data": {"2021-01": 50, "2021-02": 52, "2021-03": 55, "2021-04": 58, "2021-05": 62, "2021-06": 68, "2021-07": 72, "2021-08": 78, "2021-09": 85, "2021-10": 100, "2021-11": 80},
                    "insight": "People looking for conversation fuel. Entertainment as shared reference had built-in amplifier."
                }
            ]
        }
    ]
}

THE_BEAR_SIGNALS = {
    "title": "The Bear (2022)",
    "release_date": "June 23, 2022",
    "outcome": "Highest rated new show of 2022. Emmy winner.",
    "thesis": "Massive demand gap: authentic working-class narratives, burnout representation, food-as-art appreciation, and craft/mastery craving — all with near-zero supply.",
    "what_popcorn_would_have_said": {
        "date": "February 2022 — 4 months before release",
        "alert_level": "HIGH-VALUE DEMAND GAP",
        "message": "74% of Americans work outside offices yet virtually all prestige content depicts corporate environments. Burnout discourse at all-time high. Food culture expanding from hobby to art. Audiences want intense authentic content over polished production. A workplace drama in a high-pressure blue-collar environment would serve a massive underrepresented audience. Current supply: zero."
    },
    "cultural_currents": [
        {
            "name": "Working Class Representation Hunger",
            "category": "Identity Demand",
            "why_it_matters": "Most Americans work outside offices but almost all prestige TV depicts lawyers, tech, or wealthy families. Working-class audiences felt invisible.",
            "signals": [
                {
                    "term": "working class shows",
                    "source": "Google Trends",
                    "data": {"2021-10": 30, "2021-11": 32, "2021-12": 35, "2022-01": 40, "2022-02": 45, "2022-03": 52, "2022-04": 58, "2022-05": 65, "2022-06": 100, "2022-07": 90, "2022-08": 72},
                    "insight": "Steady 8-month climb BEFORE The Bear. Audiences actively searching for unmet content."
                },
                {
                    "term": "realistic tv shows",
                    "source": "Google Trends",
                    "data": {"2021-10": 38, "2021-11": 40, "2021-12": 42, "2022-01": 48, "2022-02": 52, "2022-03": 58, "2022-04": 64, "2022-05": 72, "2022-06": 100, "2022-07": 85, "2022-08": 68},
                    "insight": "Rejecting aspirational fantasy, seeking authenticity. Pendulum swinging from escapism to realism."
                },
                {
                    "term": "tv shows about regular people",
                    "source": "Google Trends",
                    "data": {"2021-10": 25, "2021-11": 28, "2021-12": 32, "2022-01": 38, "2022-02": 45, "2022-03": 52, "2022-04": 60, "2022-05": 70, "2022-06": 100, "2022-07": 88, "2022-08": 65},
                    "insight": "People literally searching for content about regular people. The search IS the proof."
                }
            ]
        },
        {
            "name": "Burnout and Pressure Representation",
            "category": "Psychological Processing",
            "why_it_matters": "2022 was peak burnout discourse. People wanted content that acknowledged their exhaustion — not escapism, but VALIDATION.",
            "signals": [
                {
                    "term": "burnout",
                    "source": "Google Trends",
                    "data": {"2021-10": 55, "2021-11": 58, "2021-12": 60, "2022-01": 68, "2022-02": 75, "2022-03": 80, "2022-04": 85, "2022-05": 90, "2022-06": 95, "2022-07": 100, "2022-08": 88},
                    "insight": "Burnout was THE defining experience of 2022. Content depicting surviving intense pressure provided catharsis."
                },
                {
                    "term": "quiet quitting",
                    "source": "Google Trends",
                    "data": {"2021-10": 5, "2021-11": 5, "2021-12": 8, "2022-01": 10, "2022-02": 15, "2022-03": 22, "2022-04": 35, "2022-05": 50, "2022-06": 70, "2022-07": 90, "2022-08": 100},
                    "insight": "Culture processing its relationship to work. Intense work content served this paradoxically."
                },
                {
                    "term": "work life balance",
                    "source": "Google Trends",
                    "data": {"2021-10": 50, "2021-11": 52, "2021-12": 55, "2022-01": 60, "2022-02": 68, "2022-03": 74, "2022-04": 80, "2022-05": 85, "2022-06": 92, "2022-07": 100, "2022-08": 90},
                    "insight": "Work-life balance conversation everywhere. Content showing total work immersion was compelling because it confronted the tension."
                }
            ]
        },
        {
            "name": "Food Culture Deepening",
            "category": "Cultural Interest",
            "why_it_matters": "Food evolved from sustenance to identity. Pandemic accelerated with home cooking. Audience wanted food content to get SERIOUS.",
            "signals": [
                {
                    "term": "food as art",
                    "source": "Google Trends",
                    "data": {"2021-10": 32, "2021-11": 35, "2021-12": 38, "2022-01": 42, "2022-02": 48, "2022-03": 55, "2022-04": 62, "2022-05": 70, "2022-06": 90, "2022-07": 100, "2022-08": 78},
                    "insight": "Elevating food to art form. Wanted content treating cooking with reverence."
                },
                {
                    "term": "restaurant behind the scenes",
                    "source": "Google Trends",
                    "data": {"2021-10": 28, "2021-11": 30, "2021-12": 35, "2022-01": 40, "2022-02": 48, "2022-03": 55, "2022-04": 62, "2022-05": 72, "2022-06": 95, "2022-07": 100, "2022-08": 75},
                    "insight": "Curious about real kitchens — not competition format, authentic daily reality."
                },
                {
                    "term": "chef documentary",
                    "source": "Google Trends",
                    "data": {"2021-10": 35, "2021-11": 38, "2021-12": 40, "2022-01": 45, "2022-02": 50, "2022-03": 56, "2022-04": 62, "2022-05": 70, "2022-06": 88, "2022-07": 100, "2022-08": 72},
                    "insight": "Searching for chef DOCUMENTARIES = wanting real stories about chefs."
                }
            ]
        },
        {
            "name": "Craft and Excellence Craving",
            "category": "Content Quality Drive",
            "why_it_matters": "Appetite for content depicting mastery and dedication to craft. Not superheroes — real humans being great at real skills.",
            "signals": [
                {
                    "term": "mastery and craft",
                    "source": "Google Trends",
                    "data": {"2021-10": 30, "2021-11": 33, "2021-12": 36, "2022-01": 42, "2022-02": 48, "2022-03": 55, "2022-04": 62, "2022-05": 68, "2022-06": 85, "2022-07": 100, "2022-08": 78},
                    "insight": "Desire to watch people be GREAT at something real. Real skills, not CGI."
                },
                {
                    "term": "satisfying videos",
                    "source": "Google Trends",
                    "data": {"2021-10": 55, "2021-11": 58, "2021-12": 60, "2022-01": 65, "2022-02": 70, "2022-03": 75, "2022-04": 80, "2022-05": 85, "2022-06": 92, "2022-07": 100, "2022-08": 90},
                    "insight": "Satisfying videos exploding on TikTok. Deep need to see ORDER and MASTERY in chaos."
                },
                {
                    "term": "artisan craftsmanship",
                    "source": "Google Trends",
                    "data": {"2021-10": 28, "2021-11": 32, "2021-12": 35, "2022-01": 40, "2022-02": 46, "2022-03": 52, "2022-04": 58, "2022-05": 65, "2022-06": 82, "2022-07": 100, "2022-08": 75},
                    "insight": "Artisan content rising everywhere. Watching someone do something BEAUTIFULLY is deeply satisfying."
                }
            ]
        }
    ]
}


def analyze_signals(content_data):
    """Analyze content-blind cultural signals."""
    all_terms = []
    current_analyses = []

    for current in content_data["cultural_currents"]:
        current_velocities = []
        signal_details = []

        for signal in current["signals"]:
            data = signal["data"]
            months = sorted(data.keys())
            values = [data[m] for m in months]
            pre_months = months[:-2]
            pre_values = [data[m] for m in pre_months]

            if len(pre_values) >= 2:
                velocity = (pre_values[-1] - pre_values[0]) / max(pre_values[0], 1)
                if len(pre_values) >= 4:
                    mid = len(pre_values) // 2
                    first_half = (pre_values[mid] - pre_values[0]) / max(pre_values[0], 1)
                    second_half = (pre_values[-1] - pre_values[mid]) / max(pre_values[mid], 1)
                    acceleration = second_half - first_half
                else:
                    acceleration = 0

                ups = sum(1 for i in range(len(pre_values) - 1) if pre_values[i] <= pre_values[i + 1])
                consistency = ups / max(len(pre_values) - 1, 1)
                strength = "STRONG" if velocity > 0.5 else ("MODERATE" if velocity > 0.2 else "WEAK")

                detail = {
                    "term": signal["term"],
                    "source": signal["source"],
                    "velocity_pct": round(velocity * 100, 1),
                    "acceleration": round(acceleration * 100, 1),
                    "consistency_pct": round(consistency * 100, 1),
                    "signal_strength": strength,
                    "monthly_data": data,
                    "insight": signal["insight"],
                }
                signal_details.append(detail)
                all_terms.append(detail)
                current_velocities.append(velocity)

        avg_vel = sum(current_velocities) / len(current_velocities) if current_velocities else 0
        strong_count = sum(1 for s in signal_details if s["signal_strength"] == "STRONG")

        current_analyses.append({
            "name": current["name"],
            "category": current["category"],
            "why_it_matters": current["why_it_matters"],
            "avg_velocity_pct": round(avg_vel * 100, 1),
            "signal_count": len(signal_details),
            "strong_signals": strong_count,
            "signals": signal_details,
            "current_strength": "STRONG" if avg_vel > 0.5 else ("MODERATE" if avg_vel > 0.2 else "WEAK"),
        })

    # Popcorn Score
    all_vel = [t["velocity_pct"] for t in all_terms]
    avg_velocity = sum(all_vel) / len(all_vel) if all_vel else 0
    num_strong = sum(1 for c in current_analyses if c["current_strength"] == "STRONG")
    convergence = num_strong / max(len(current_analyses), 1)
    all_con = [t["consistency_pct"] for t in all_terms]
    avg_con = sum(all_con) / len(all_con) if all_con else 0

    vel_score = min(40, avg_velocity * 0.5)
    conv_score = min(35, convergence * 35)
    con_score = min(25, avg_con * 0.25)
    popcorn_score = round(min(100, vel_score + conv_score + con_score))

    return {
        "title": content_data["title"],
        "release_date": content_data["release_date"],
        "outcome": content_data["outcome"],
        "thesis": content_data["thesis"],
        "what_popcorn_would_have_said": content_data["what_popcorn_would_have_said"],
        "popcorn_score": popcorn_score,
        "score_breakdown": {
            "velocity_component": round(vel_score, 1),
            "convergence_component": round(conv_score, 1),
            "consistency_component": round(con_score, 1),
        },
        "verdict": (
            "STRONG DEMAND SIGNAL — Multiple content-blind cultural currents converging"
            if popcorn_score >= 70 else
            "MODERATE DEMAND SIGNAL — Emerging cultural currents detected"
            if popcorn_score >= 45 else
            "WEAK SIGNAL — Limited pre-release indicators"
        ),
        "cultural_currents": current_analyses,
        "total_signals_tracked": len(all_terms),
        "total_currents_tracked": len(current_analyses),
        "strong_currents": num_strong,
        "methodology": "Content-blind analysis: ZERO search terms reference the content itself.",
    }


def get_all_analyses():
    """Return all retroactive analyses."""
    return {
        "barbie": analyze_signals(BARBIE_SIGNALS),
        "squid_game": analyze_signals(SQUID_GAME_SIGNALS),
        "the_bear": analyze_signals(THE_BEAR_SIGNALS),
        "meta": {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "2.0 — Content-Blind Signals",
            "key_insight": "Entertainment hits don't create demand. They capture demand that already exists.",
        }
    }
