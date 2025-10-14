"""Study-related utility functions"""
import random
from datetime import datetime
from typing import List, Dict, Optional

def generate_study_tip() -> str:
    """Generate a random study tip"""
    tips = [
        "Break your study sessions into 25-minute focused intervals",
        "Review your notes within 24 hours of learning new material",
        "Teach concepts to others to reinforce your understanding",
        "Use active recall instead of passive reading",
        "Create mind maps to connect related concepts",
        "Take regular breaks to maintain focus",
        "Study in a quiet, well-lit environment",
        "Use multiple learning methods for better retention",
        "Get enough sleep to consolidate memories",
        "Stay hydrated and maintain good nutrition"
    ]
    return random.choice(tips)

def update_study_stats(stats: Dict, session_duration: int) -> Dict:
    """Update study statistics with new session data"""
    now = datetime.now()
    
    if not stats.get("study_sessions"):
        stats["study_sessions"] = []
    
    stats["study_sessions"].append({
        "date": now.strftime("%Y-%m-%d"),
        "duration": session_duration,
        "timestamp": now.isoformat()
    })
    
    stats["total_time"] = sum(session["duration"] for session in stats["study_sessions"])
    stats["session_count"] = len(stats["study_sessions"])
    stats["last_study_session"] = now.strftime("%Y-%m-%d %H:%M")
    
    # Calculate streak
    dates = sorted(set(session["date"] for session in stats["study_sessions"]))
    current_streak = 1
    max_streak = 1
    
    for i in range(1, len(dates)):
        date1 = datetime.strptime(dates[i-1], "%Y-%m-%d")
        date2 = datetime.strptime(dates[i], "%Y-%m-%d")
        if (date2 - date1).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    stats["current_streak"] = current_streak
    stats["max_streak"] = max_streak
    
    return stats

def get_learning_progress(topics: List[str], scores: Dict[str, List[int]]) -> Dict[str, float]:
    """Calculate learning progress per topic"""
    progress = {}
    for topic in topics:
        if topic in scores and scores[topic]:
            # Weight recent scores more heavily
            weighted_scores = []
            for i, score in enumerate(scores[topic]):
                weight = (i + 1) / len(scores[topic])  # More recent scores have higher weight
                weighted_scores.append(score * weight)
            progress[topic] = sum(weighted_scores) / sum(range(1, len(scores[topic]) + 1))
        else:
            progress[topic] = 0.0
    return progress