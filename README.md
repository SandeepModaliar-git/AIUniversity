# AI University 🎓

## Agentic AI Powered Learning Path Generator

AI University is an **Agentic AI system** that automatically generates a
structured **learning roadmap from YouTube videos** based on a user's
topic and experience level.

Instead of manually searching and organizing tutorials, the system:

1.  Searches YouTube
2.  Evaluates video authority
3.  Classifies learning material
4.  Builds a structured **weekly learning path**

The system is implemented using **LangGraph, FastAPI, Serper, and the
YouTube Data API**.

------------------------------------------------------------------------

# Features

-   Generate structured learning paths automatically
-   Supports **Beginner / Intermediate / Advanced** levels
-   Uses **YouTube search + metadata** to find educational content
-   Computes **authority scores** to rank videos
-   Classifies content into:
    -   Core curriculum
    -   Primary material
    -   Supporting material
    -   Optional material
-   Builds **weekly learning schedules**
-   Generates **learning objectives for each week**
-   Exposes functionality through a **FastAPI REST API**

------------------------------------------------------------------------

# Example Output

``` json
{
  "level": "BEGINNER",
  "query": "Agentic AI",
  "revised_query": "Beginner Agentic AI Concepts and Applications",
  "no_of_weeks": 5,
  "learning_path": [
    {
      "week": 1,
      "focus": "Introduction to AI Agents and fundamentals of Agentic AI",
      "videos": []
    }
  ]
}
```

------------------------------------------------------------------------

# System Architecture

    User Query
       │
       ▼
    Level Detection Node
       │
       ▼
    Query Expansion Node
       │
       ▼
    Serper Search (YouTube)
       │
       ▼
    YouTube Data API
       │
       ▼
    Authority Scoring
       │
       ▼
    Video Recommendation
       │
       ▼
    Learning Path Generator
       │
       ▼
    Save Results
       │
       ▼
    FastAPI Response

------------------------------------------------------------------------

# Technologies Used

  Technology         Purpose
  ------------------ -------------------------------------------
  LangGraph          Agent workflow orchestration
  FastAPI            REST API
  Serper API         YouTube search
  YouTube Data API   Video metadata
  Python             Core implementation
  LLM                Query expansion and curriculum generation

------------------------------------------------------------------------

# Authority Scoring

Videos are ranked using a weighted scoring system:

    Authority Score =
    0.5 × normalized views +
    0.3 × normalized likes +
    0.2 × normalized comments

This helps prioritize **high-quality educational content**.

------------------------------------------------------------------------

# Learning Path Structure

Each **week** contains a balanced set of materials:

  Category     Purpose
  ------------ -------------------------
  Core         Essential concepts
  Primary      Hands-on tutorials
  Supporting   Additional explanations
  Optional     Enrichment material

Example weekly schedule:

    Week 1
    Focus: Fundamentals of AI Agents

    Core
    • AI Agents Tutorial
    • Agentic AI Basics

    Primary
    • Building your first agent

    Supporting
    • LangGraph introduction
    • Automation workflows

------------------------------------------------------------------------

# Installation

Clone the repository:

``` bash
git clone https://github.com/yourusername/ai-university.git
cd ai-university
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# Environment Variables

Create a `.env` file:

    SERPER_API_KEY=your_serper_key
    YOUTUBE_API_KEY=your_youtube_key
    OPENAI_API_KEY=your_openai_key

------------------------------------------------------------------------

# Running the API

Start the FastAPI server:

``` bash
uvicorn app:api --reload
```

API will be available at:

    http://127.0.0.1:8000

Swagger documentation:

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# Example API Request

``` python
import requests

url = "http://127.0.0.1:8000/generate-learning-path"

payload = {
    "query": "Agentic AI",
    "level": "BEGINNER"
}

response = requests.post(url, json=payload)

print(response.json())
```

------------------------------------------------------------------------

# Project Structure

    AIUniversity/
    │
    ├── app.py
    ├── graph.py
    ├── nodes/
    │   ├── level_detection.py
    │   ├── query_expansion.py
    │   ├── serper_search.py
    │   ├── youtube_metadata.py
    │   ├── scoring.py
    │   ├── learning_path.py
    │   └── save_results.py
    │
    ├── utils/
    │   ├── youtube_utils.py
    │   └── authority_score.py
    │
    ├── results.json
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

# Future Improvements

-   Streaming responses from the agent
-   Personalized learning paths
-   Transcript-based video summarization
-   Frontend learning dashboard
-   Vector database for course memory
-   Multi-topic learning programs

------------------------------------------------------------------------

# License

MIT License

------------------------------------------------------------------------

# Author

Developed as part of an **Agentic AI Capstone Project**.
