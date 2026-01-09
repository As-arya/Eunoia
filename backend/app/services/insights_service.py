"""Insights Service"""
from datetime import datetime, timedelta
from app.models import MoodEntry, Session, SessionInsight

MOOD_SCORES = {'Happy': 90, 'Calm': 80, 'Neutral': 60, 'Tired': 50, 'Anxious': 40, 'Sad': 30, 'Stress': 35, 'Overwhelmed': 20}

def get_mood_trend(user_id, period='weekly'):
    # Determine date range based on period
    if period == 'daily':
        days = 1
        num_points = 24  # hourly for daily
    elif period == 'monthly':
        days = 30
        num_points = 30
    else:  # weekly default
        days = 7
        num_points = 7
    
    start = datetime.utcnow() - timedelta(days=days)
    entries = MoodEntry.query.filter(MoodEntry.user_id == user_id, MoodEntry.created_at >= start).all()
    
    data = []
    if period == 'daily':
        # Show hourly data for today
        for i in range(7):
            hour = datetime.utcnow() - timedelta(hours=6-i)
            hour_e = [e for e in entries if e.created_at.hour == hour.hour]
            score = sum(MOOD_SCORES.get(e.mood, 50) for e in hour_e) / len(hour_e) if hour_e else 60
            data.append({'day': f'{hour.hour:02d}:00', 'score': round(score)})
    elif period == 'monthly':
        # Show weekly averages for month
        week_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        for i in range(4):
            week_start = datetime.utcnow() - timedelta(days=28-i*7)
            week_end = week_start + timedelta(days=7)
            week_e = [e for e in entries if week_start <= e.created_at < week_end]
            score = sum(MOOD_SCORES.get(e.mood, 50) for e in week_e) / len(week_e) if week_e else 60
            data.append({'day': week_labels[i], 'score': round(score)})
    else:  # weekly
        for i in range(7):
            d = datetime.utcnow() - timedelta(days=6-i)
            day_e = [e for e in entries if e.created_at.date() == d.date()]
            score = sum(MOOD_SCORES.get(e.mood, 50) for e in day_e) / len(day_e) if day_e else 60
            data.append({'day': ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d.weekday()], 'score': round(score)})
    
    return {'period': period, 'data': data}

def get_emotions(user_id, period='weekly'):
    start = datetime.utcnow() - timedelta(days=7 if period == 'weekly' else 30)
    entries = MoodEntry.query.filter(MoodEntry.user_id == user_id, MoodEntry.created_at >= start).all()
    
    counts = {}
    for e in entries:
        counts[e.mood] = counts.get(e.mood, 0) + 1
    total = sum(counts.values()) or 1
    
    emotions = [{'emotion': m, 'percentage': round(c/total*100), 'count': c} for m, c in sorted(counts.items(), key=lambda x: x[1], reverse=True)]
    return {'period': period, 'emotions': emotions[:5] or [{'emotion': 'Neutral', 'percentage': 100, 'count': 0}]}

def get_observations(user_id, limit=10):
    """Get AI observations based on session insights"""
    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.started_at.desc()).limit(limit).all()
    
    observations = []
    for s in sessions:
        if s.insight:
            # Determine observation type based on primary trigger
            primary = (s.insight.primary_trigger or '').lower()
            if 'anxious' in primary or 'stress' in primary or 'overwhelmed' in primary:
                obs_type = 'pattern'
            elif 'tired' in primary or 'exhausted' in primary or 'sleep' in primary:
                obs_type = 'sleep'
            elif 'sad' in primary or 'depressed' in primary or 'lonely' in primary:
                obs_type = 'emotion'
            else:
                obs_type = 'insight'
            
            # Create title based on trigger
            trigger_titles = {
                'anxious': 'Pola Kecemasan Terdeteksi',
                'stressed': 'Tingkat Stres Tinggi',
                'stress': 'Tingkat Stres Tinggi',
                'overwhelmed': 'Perasaan Kewalahan',
                'tired': 'Kelelahan Terdeteksi',
                'exhausted': 'Tingkat Energi Rendah',
                'sad': 'Emosi Sedih Dominan',
                'depressed': 'Mood Rendah Terdeteksi',
                'lonely': 'Perasaan Kesepian',
                'happy': 'Mood Positif! 🌟',
                'calm': 'Kondisi Emosional Stabil',
                'neutral': 'Kondisi Seimbang',
            }
            
            title = trigger_titles.get(primary, f'Observasi: {s.insight.primary_trigger or "Sesi"}')
            
            observations.append({
                'id': s.insight.id,
                'type': obs_type,
                'title': title,
                'description': s.insight.summary or 'Tidak ada detail',
                'session_id': s.id,
                'date': s.started_at.isoformat() if s.started_at else None
            })
    
    return observations

