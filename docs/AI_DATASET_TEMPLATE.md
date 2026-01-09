# Enhanced Eunoia AI Mental Health Dataset
## Evidence-Based Mental Health Training Data

> **Based on research from:** PHQ-9, GAD-7, Columbia-Suicide Severity Rating Scale (C-SSRS), NLP emotion detection studies, and empathetic AI chatbot research.

**Version**: 2.0 (Evidence-Based Enhancement)  
**Last Updated**: December 2025

---

## Dataset Files

| File | Purpose | Location |
|------|---------|----------|
| `empathy_responses.json` | Varied empathetic responses by emotion | `backend/data/` |
| `crisis_detection.json` | Crisis keywords and safety protocols | `backend/data/` |
| `questions.py` | PHQ-9/GAD-7 screening questions | `backend/app/seeds/` |

---

## 1. Enhanced Screening Questions (PHQ-9/GAD-7 Adapted)

15 evidence-based questions covering:
- **Depression** (PHQ-9 Items 1-4, 6-7): Anhedonia, mood, sleep, energy, guilt, concentration
- **Anxiety** (GAD-7 Items 1-2, 4, 6): Nervousness, worry control, relaxation, irritability
- **Stress, Social Support, Functional Impairment**

### Scoring Guidelines
- **Score Range**: 0-45 (15 questions × max 3 points)
- **0-7**: Minimal - maintain wellness
- **8-14**: Mild - self-help strategies
- **15-21**: Moderate - consider professional help
- **22+**: Severe - recommend professional consultation

---

## 2. Empathy Response Categories

Each emotion has multiple responses with:
- `intensity`: high/medium/low
- `empathy_type`: cognitive/affective/grounding/exploratory
- `follow_up`: true/false

### Supported Emotions
- Happy, Anxious, Sad, Stressed, Tired, Overwhelmed, Angry, Hopeless

---

## 3. Crisis Detection

### High Risk Keywords (Immediate Action)
```
bunuh diri, suicide, mengakhiri hidup, mati saja, 
ingin mati, rencana bunuh diri, self harm, etc.
```

### Moderate Risk Keywords
```
putus asa, hopeless, tidak ada harapan, 
tidak berguna, lelah hidup, pengen hilang, etc.
```

### Crisis Resources (Indonesia)
- **Hotline Kesehatan Jiwa**: 119 ext 8 (24/7)
- **Indonesia Suicide Hotline**: 021-500-454 (24/7)
- **Yayasan Pulih**: +62 811-1711-555

---

## 4. How to Expand the Dataset

### Adding Empathy Responses
Edit `backend/data/empathy_responses.json`:

```json
{
  "NewEmotion": [
    {
      "response": "Your empathetic response here",
      "follow_up": true,
      "intensity": "high",
      "empathy_type": "cognitive"
    }
  ]
}
```

### Adding Crisis Keywords
Edit `backend/data/crisis_detection.json`:

```json
{
  "crisis_keywords": {
    "high_risk": {
      "keywords": ["new keyword", ...],
      "immediate_action": "crisis_protocol"
    }
  }
}
```

### Adding Screening Questions
Edit `backend/app/seeds/questions.py` and run:
```bash
python reseed_questions.py
```

---

## 5. Implementation Notes

The `gemini_service.py` automatically:
1. Loads JSON datasets on startup
2. Detects crisis keywords in user responses
3. Selects empathy responses based on detected emotion
4. Generates score-based summaries and recommendations
5. Falls back gracefully when Gemini API is unavailable

---

## Research References

- Kroenke et al. (2001). PHQ-9 validity study
- Spitzer et al. (2006). GAD-7 measure
- Posner et al. (2011). Columbia-Suicide Severity Rating Scale
- WHO (2022). Mental Health Gap Action Programme

---

## Future Enhancements

- [ ] Machine Learning emotion detection model
- [ ] Multi-language support (English/Indonesian)
- [ ] Voice input recognition
- [ ] Longitudinal symptom tracking
- [ ] Integration with telemed services
