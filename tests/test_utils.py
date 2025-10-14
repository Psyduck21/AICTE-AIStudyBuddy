"""Tests for utils module"""
import pytest
from datetime import datetime, timedelta
from src.utils.utils import (
    format_timestamp,
    get_time_ago,
    calculate_average,
    truncate_text,
    format_score,
    get_difficulty_color
)

def test_format_timestamp():
    """Test timestamp formatting"""
    # Test with specific datetime
    dt = datetime(2025, 10, 13, 14, 30, 0)
    assert format_timestamp(dt) == "2025-10-13 14:30:00"
    
    # Test without datetime (should use current time)
    result = format_timestamp()
    assert isinstance(result, str)
    assert len(result) == 19  # YYYY-MM-DD HH:MM:SS


def test_get_time_ago():
    """Test time ago calculations"""
    now = datetime.now()
    
    # Test days ago
    two_days = now - timedelta(days=2)
    assert get_time_ago(two_days.strftime("%Y-%m-%d %H:%M:%S")) == "2d ago"
    
    # Test hours ago
    three_hours = now - timedelta(hours=3)
    assert get_time_ago(three_hours.strftime("%Y-%m-%d %H:%M:%S")) == "3h ago"
    
    # Test minutes ago
    five_minutes = now - timedelta(minutes=5)
    assert get_time_ago(five_minutes.strftime("%Y-%m-%d %H:%M:%S")) == "5m ago"
    
    # Test just now
    assert get_time_ago(now.strftime("%Y-%m-%d %H:%M:%S")) == "just now"
    
    # Test invalid format
    assert get_time_ago("invalid-date") == "unknown"


def test_calculate_average():
    """Test average calculation"""
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert calculate_average([0, 100]) == 50.0
    assert calculate_average([]) == 0.0
    assert calculate_average([1.5, 2.5, 3.5]) == 2.5


def test_truncate_text():
    """Test text truncation"""
    text = "This is a long text that needs to be truncated"
    
    # Test no truncation needed
    assert truncate_text(text, 100) == text
    
    # Test truncation
    assert truncate_text(text, 10) == "This is a ..."
    
    # Test empty string
    assert truncate_text("") == ""
    
    # Test exactly at limit
    assert truncate_text("12345", 5) == "12345"


def test_format_score():
    """Test score formatting"""
    # Test excellent score
    assert "🌟" in format_score(95, 100)
    assert "Excellent" in format_score(95, 100)
    
    # Test good score
    assert "👍" in format_score(80, 100)
    assert "Good" in format_score(80, 100)
    
    # Test fair score
    assert "💪" in format_score(65, 100)
    assert "Fair" in format_score(65, 100)
    
    # Test needs practice
    assert "📚" in format_score(40, 100)
    assert "Keep Practicing" in format_score(40, 100)
    
    # Test zero total
    assert format_score(0, 0) == "📚 0/0 (0.0%) - Keep Practicing"


def test_get_difficulty_color():
    """Test difficulty color mapping"""
    assert get_difficulty_color("Easy") == "🟢"
    assert get_difficulty_color("Medium") == "🟡"
    assert get_difficulty_color("Hard") == "🔴"
    assert get_difficulty_color("Mixed") == "🔵"
    assert get_difficulty_color("Unknown") == "⚪"
    assert get_difficulty_color("College") == "🟠"