# Confidence Scoring Simulator

This Streamlit app compares two confidence scoring systems for an AI research agent that collects facts about loyalty programs from multiple web sources.

## What it shows

- Add sources one at a time from a dropdown
- See a live table of source types and weights
- Compare the naive source-count score against the weighted quality score
- View a bar chart that makes the difference between the two systems obvious
- Load scenario presets to quickly test common patterns

## Scoring systems

### Naive system

- 1 source = Low
- 2 to 3 sources = Medium
- 4 or more sources = High

### Weighted system

- Official Website = 3
- Press Release = 2.5
- News Article = 2
- Review Platform = 1
- Community Forum = 0.5

Weighted score bands:

- 0 to 2.5 = Low
- 2.5 to 5 = Medium
- 5+ = High

## Scenario presets

- All Forums: 5 community posts
- Mixed Sources: 1 official source, 2 news articles, 2 community posts
- Official Heavy: 3 official sources, 1 news article

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run app.py
```

## Files

- [app.py](app.py) - main Streamlit app
- [.streamlit/config.toml](.streamlit/config.toml) - dark theme configuration
- [requirements.txt](requirements.txt) - Python dependencies
