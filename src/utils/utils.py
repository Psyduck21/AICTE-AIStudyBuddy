"""Utility functions for AI Study Buddy Pro"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Set
import random
from typing import Optional

from ..utils.logger import logger

def save_json(data: Dict, filename: str) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Dictionary to save
        filename: Target file path
        
    Returns:
        bool: Success status
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.debug(f"Saved JSON to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")
        return False


def load_json(filename: str) -> Dict:
    """
    Load data from JSON file.
    
    Args:
        filename: Source file path
        
    Returns:
        Dict: Loaded data or empty dict
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            logger.debug(f"Loaded JSON from {filename}")
            return data
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
    return {}


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to readable string.
    
    Args:
        dt: Datetime object (default: current time)
        
    Returns:
        str: Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_time_ago(timestamp_str: str) -> str:
    """
    Calculate time elapsed since timestamp.
    
    Args:
        timestamp_str: Timestamp string
        
    Returns:
        str: Human readable time difference
    """
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        elapsed = datetime.now() - dt
        
        if elapsed.days > 0:
            return f"{elapsed.days}d ago"
        elif elapsed.seconds > 3600:
            hours = elapsed.seconds // 3600
            return f"{hours}h ago"
        elif elapsed.seconds > 60:
            minutes = elapsed.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"
    except Exception as e:
        logger.error(f"Error calculating time ago: {e}")
        return "unknown"


def calculate_average(numbers: List[float]) -> float:
    """
    Calculate average of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        float: Average value
    """
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def format_structured_content(content: Dict) -> str:
    """
    Format structured content from retrieved documents.
    
    Args:
        content: Dictionary containing text and metadata
        
    Returns:
        str: Formatted content with proper markdown
    """
    formatted_text = []
    
    # Add source information if available
    if "source" in content:
        formatted_text.append(f"**Source:** {content['source']}")
    
    # Add headers if available
    if "headers" in content and content["headers"]:
        formatted_text.append("\n**Context:**")
        formatted_text.extend([f"- {header}" for header in content["headers"]])
    
    # Format main text content
    if "text" in content:
        text = content["text"]
        
        # Check if content appears to be tabular
        if any(marker in text for marker in ["|\n", "\t"]):
            # Convert to markdown table format
            lines = text.split("\n")
            cleaned_lines = []
            for line in lines:
                # Clean up spacing issues
                line = " ".join(line.split())
                if line:
                    cleaned_lines.append(line)
            
            formatted_text.append("\n**Content:**\n")
            formatted_text.append("| " + " | ".join(cleaned_lines) + " |")
        else:
            # Clean up spacing issues
            text = " ".join(text.split())
            # Break into paragraphs
            paragraphs = text.split(". ")
            formatted_text.append("\n**Content:**\n")
            formatted_text.extend([f"{p}." for p in paragraphs if p])
    
    return "\n".join(formatted_text)

def truncate_text(content: Union[str, Dict], max_length: int = 300) -> str:
    """
    Format and truncate content with proper structure.
    
    Args:
        content: Input content (string or dictionary)
        max_length: Maximum length for text content
        
    Returns:
        str: Formatted and truncated text
    """
    if isinstance(content, dict):
        formatted = format_structured_content(content)
        if len(formatted) > max_length:
            # Preserve headers and metadata, truncate main content
            lines = formatted.split("\n")
            content_start = next((i for i, line in enumerate(lines) if "**Content:**" in line), -1)
            
            if content_start != -1:
                # Keep headers and metadata
                prefix = "\n".join(lines[:content_start + 1])
                remaining_length = max_length - len(prefix)
                content_text = "\n".join(lines[content_start + 1:])
                
                if remaining_length > 50:  # Ensure we have enough space for meaningful content
                    truncated_content = content_text[:remaining_length] + "..."
                    return prefix + "\n" + truncated_content
            
            # Fallback to simple truncation
            return formatted[:max_length] + "..."
        return formatted
    
    # Handle plain text
    text = str(content)
    text = " ".join(text.split())  # Clean up spacing
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def format_score(score: int, total: int) -> str:
    """
    Format quiz score nicely.
    
    Args:
        score: Points earned
        total: Total possible points
        
    Returns:
        str: Formatted score with emoji
    """
    percentage = (score / total * 100) if total > 0 else 0
    
    if percentage >= 90:
        emoji = "🌟"
        status = "Excellent"
    elif percentage >= 75:
        emoji = "👍"
        status = "Good"
    elif percentage >= 60:
        emoji = "💪"
        status = "Fair"
    else:
        emoji = "📚"
        status = "Keep Practicing"
    
    return f"{emoji} {score}/{total} ({percentage:.1f}%) - {status}"


def get_difficulty_color(difficulty: str) -> str:
    """
    Get color emoji for difficulty level.
    
    Args:
        difficulty: Difficulty level
        
    Returns:
        str: Color emoji
    """
    colors = {
        "Easy": "🟢",
        "Medium": "🟡",
        "Hard": "🔴",
        "Mixed": "🔵",
        "ELI5 (Very Simple)": "🟢",
        "High School": "🟡",
        "College": "🟠",
        "Advanced": "🔴"
    }
    return colors.get(difficulty, "⚪")


def generate_study_tip(topic: str = None) -> str:
    """
    Generate a random study tip, optionally contextualized to a topic.
    
    Args:
        topic: Optional topic or concept to tailor the tip
    Returns:
        str: Study tip with emoji
    """
    tips = [
        "💡 Break complex topics into smaller chunks for better understanding",
        "🔄 Review material regularly to strengthen memory retention",
        "✍️ Write summary notes to reinforce learning",
        "🎯 Use active recall - test yourself on material",
        "🌙 Study during your peak alertness hours",
        "📚 Create mind maps to visualize connections",
        "🎓 Teach concepts to others to deepen understanding",
        "⏱️ Use the Pomodoro technique for focused study sessions",
        "🎴 Flashcards are great for memorization",
        "📊 Track progress to stay motivated"
    ]
    if topic:
        topic_tips = [
            f"🔍 When studying '{topic}', focus on key definitions and examples.",
            f"📝 Summarize the main points of '{topic}' in your own words.",
            f"🤔 Ask yourself questions about '{topic}' to test your understanding.",
            f"📖 Relate '{topic}' to real-life scenarios for better retention."
        ]
        tips.extend(topic_tips)
    return random.choice(tips)


def validate_pdf(file_path: str) -> Dict[str, Any]:
    """
    Validate PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dict[str, Any]: Validation results
    """
    result = {
        "valid": False,
        "message": "",
        "size_mb": 0
    }
    
    try:
        if not os.path.exists(file_path):
            result["message"] = "File not found"
            return result
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        result["size_mb"] = file_size_mb
        
        if file_size_mb > 50:
            result["message"] = "File too large (max 50MB)"
            return result
        
        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            result["message"] = "Not a PDF file"
            return result
        
        result["valid"] = True
        result["message"] = "File is valid"
        
    except Exception as e:
        logger.error(f"Error validating PDF: {e}")
        result["message"] = f"Error validating file: {str(e)}"
    
    return result


def export_to_csv(data: List[Dict], filename: str) -> bool:
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries
        filename: Target file path
        
    Returns:
        bool: Success status
    """
    try:
        import csv
        if not data:
            return False
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
        logger.info(f"Data exported to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False


def calculate_study_streak(quiz_history: List[Dict]) -> int:
    """
    Calculate consecutive study days.
    
    Args:
        quiz_history: List of quiz attempts
        
    Returns:
        int: Number of consecutive days
    """
    if not quiz_history:
        return 0
    
    quiz_dates: Set[datetime] = set()
    for quiz in quiz_history:
        try:
            date = datetime.strptime(quiz["date"], "%Y-%m-%d %H:%M").date()
            quiz_dates.add(date)
        except Exception as e:
            logger.error(f"Error parsing quiz date: {e}")
            continue
    
    if not quiz_dates:
        return 0
    
    sorted_dates = sorted(quiz_dates, reverse=True)
    streak = 1
    today = datetime.now().date()
    
    for i, date in enumerate(sorted_dates):
        if i == 0 and date != today:
            continue
        if i > 0 and sorted_dates[i-1] - date == timedelta(days=1):
            streak += 1
        else:
            break
    
    return streak


def format_study_summary(quiz_history: List[Dict], flashcard_count: int) -> str:
    """
    Generate a study summary.
    
    Args:
        quiz_history: List of quiz attempts
        flashcard_count: Number of flashcards
        
    Returns:
        str: Formatted summary
    """
    if not quiz_history and flashcard_count == 0:
        return "📌 Get started by uploading a PDF and asking your first question!"
    
    num_quizzes = len(quiz_history)
    avg_score = calculate_average([q["percentage"] for q in quiz_history]) if quiz_history else 0
    streak = calculate_study_streak(quiz_history)
    
    summary = f"""
    📊 **Your Study Summary**
    
    - Total Quizzes Completed: {num_quizzes}
    - Average Score: {avg_score:.1f}%
    - Flashcards Created: {flashcard_count}
    - Study Streak: {streak} days 🔥
    """
    
    return summary.strip()


def get_learning_recommendation(search_term: str, results: List[Dict] = None, quiz_history: List[Dict] = None) -> str:
    """
    Get personalized learning recommendation based on search term and available content.
    
    Args:
        search_term: The concept being explored
        results: List of relevant content chunks
        quiz_history: List of quiz attempts
        
    Returns:
        str: Learning recommendation
    """
    recommendations = []
    
    # Add content-based recommendations
    if search_term and results:
        content_based = f"📚 Found {len(results)} relevant sections about '{search_term}'. "
        if len(results) > 3:
            content_based += "Consider breaking this topic into smaller sub-topics for better understanding."
        elif len(results) == 0:
            content_based += "Try exploring related concepts or checking different terminology."
        recommendations.append(content_based)
    
    # Add performance-based recommendations
    if quiz_history:
        recent_quizzes = quiz_history[-5:] if len(quiz_history) >= 5 else quiz_history
        
        # Calculate average score safely
        total_score = 0
        total_count = 0
        
        for quiz in recent_quizzes:
            try:
                score = quiz.get("score", 0)
                total = quiz.get("total", 1)
                if total > 0:  # Avoid division by zero
                    total_score += (score / total) * 100
                    total_count += 1
            except (TypeError, ZeroDivisionError):
                continue
        
        # Only add performance-based recommendation if we have valid scores
        if total_count > 0:
            avg_score = total_score / total_count
            if avg_score < 60:
                recommendations.append("🎯 Focus on reviewing fundamental concepts before advancing.")
            elif avg_score < 80:
                recommendations.append("📈 You're making good progress. Try challenging yourself with harder questions.")
            else:
                recommendations.append("🌟 Great work! Consider exploring advanced topics or helping others learn.")
    
    if not recommendations:
        recommendations.append("📚 Start by exploring topics and taking quizzes to get personalized recommendations!")
    
    # Combine all recommendations and return
    return " ".join(recommendations)