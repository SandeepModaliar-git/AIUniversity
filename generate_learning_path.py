#%%
import math
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import Annotated, TypedDict
from langgraph.graph import add_messages
from langgraph.types import Send
from langgraph.types import interrupt
import logging
from langgraph.graph import StateGraph, END, START
from IPython.display import Image, display
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import requests
import json
from urllib.parse import urlparse, parse_qs
from langchain_core.messages import AIMessage, ToolMessage
from googleapiclient.discovery import build
import httplib2
from copy import deepcopy
import operator


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='query_expansion_agent.log', # Saves to a file
    filemode='a'              # 'a' for append, 'w' to overwrite
)

logger = logging.getLogger(__name__)

#%%
load_dotenv(override=True)

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

API_KEY = os.getenv("YOUTUBE_API_KEY")
http = httplib2.Http(timeout=30, proxy_info=None)
youtube = build(
    "youtube",
    "v3",
    developerKey=os.environ["YOUTUBE_API_KEY"],
    http=http
)
#%%

class AgentState(TypedDict):
    level : str
    query : str
    duration : str
    roadmap_tasks : list[dict]
    results: Annotated[list, operator.add]
    final_roadmap : list[dict]
    serper_results : list[str]
    urls : dict[str, str]
    task: str
    week: int
    day: int
    focus: str

#%%

#%%
def roadmap_planner_node(state: AgentState) -> AgentState:

    system_prompt = f"""
    Generate a roadmap to learn {state["query"]}.

    Student level: {state["level"]}
    Duration: {state["duration"]}

    Return ONLY this markdown table:

    |Week|Day|Topic Name|Focus|
    |1|1|Topic|Focus|
    """

    response = llm.invoke(system_prompt)

    lines = response.content.split("\n")

    tasks = []

    for line in lines:

        if "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]

        if len(parts) < 5:
            continue

        if parts[1].lower() == "week":
            continue

        if parts[1].strip("-") == "":
            continue

        tasks.append(
            {
                "week": int(parts[1]),
                "day": int(parts[2]),
                "task": parts[3],
                "focus": parts[4],
            }
        )

    return {"roadmap_tasks": tasks}
#%%
def dispatch_node(state: AgentState):
    sends = []

    for task in state["roadmap_tasks"]:
        sends.append(
            Send(
                "roadmap_worker_node",
                {
                    "task": task["task"],
                    "week": task["week"],
                    "day": task["day"],
                    "focus": task["focus"]
                }
            )
        )
    return sends
#%%
def get_counts(video_ids):
    # request = youtube.videos().list(
    #         part="snippet,statistics,contentDetails",
    #         id=",".join([video for video in video_ids if video])
    #         )
    url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": os.environ["YOUTUBE_API_KEY"]
    }

    response = requests.get(url, params=params, timeout=30)
    response = response.json()

    #response = request.execute()
    video_summaries = {}
    for video in response["items"]:
        views = int(video.get("statistics", {}).get("viewCount", 0))
        likes = int(video.get("statistics", {}).get("likeCount", 0))
        comments = int(video.get("statistics", {}).get("commentCount", 0))
        video_summaries[video["id"]] = {"views" : views, "likes" : likes, "comments" : comments, "title": video["snippet"]["title"], "channelTitle" : video["snippet"]["channelTitle"], "description" : video["snippet"]["description"]}
    return video_summaries

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    return (value - min_val) / (max_val - min_val)


def get_authority_scores(video_ids_dict):

    authority_scores_dict = deepcopy(video_ids_dict)

    views = [v["views"] for v in video_ids_dict.values()]
    engagements = [
        (v["likes"] + v["comments"]) / max(v["views"], 1)
        for v in video_ids_dict.values()
    ]

    min_views, max_views = min(views), max(views)
    min_eng, max_eng = min(engagements), max(engagements)

    for video_id, data in authority_scores_dict.items():

        view_score = normalize(
                        math.log10(data["views"] + 1),
                        math.log10(min_views + 1),
                        math.log10(max_views + 1)
                    )
        engagement = (data["likes"] + data["comments"]) / max(data["views"], 1)
        engagement_score = normalize(engagement, min_eng, max_eng)

        authority_score = 0.6 * view_score + 0.4 * engagement_score

        authority_scores_dict[video_id]["authority"] = {"score" : round(authority_score, 2),
                                                        "views" : data["views"],
                                                        "likes" : data["likes"],
                                                        "comments" : data["comments"]}
    return authority_scores_dict

def get_video_summaries(authority_scores_dict, urls):
    authority_scores = []
    recommendations = []
    titles = []
    channels = []
    video_ids = []
    focus_list = []
    for video_id in authority_scores_dict.keys():
        video_ids.append(video_id)
        focus_list.append(authority_scores_dict[video_id]["description"])
        authority_scores.append(authority_scores_dict[video_id]["authority"])
        score = authority_scores_dict[video_id]["authority"]["score"]
        titles.append(authority_scores_dict[video_id]["title"])
        channels.append(authority_scores_dict[video_id]["channelTitle"])
        if score >= 0.6:
            recommendations.append("recommended as core curriculum material")
        elif score >= 0.4:
            recommendations.append("recommended as primary supporting material")
        elif score >= 0.2:
            recommendations.append("suitable as supplementary learning")
        else:
            recommendations.append("optional reference material")

    videos = []
    for video_id, title, channel, authority, recommendation, focus in zip(video_ids, titles, channels, authority_scores, recommendations, focus_list):
        video_dict = {"title" : title, "channel" : channel, "authority" : authority, "recommendation" : recommendation, "url" : urls[video_id], "description" : focus}
        videos.append(video_dict)
    videos = sorted(videos, key=lambda x: x["authority"]["score"], reverse=True)
    return {
        "videos" : videos[:5],
    }

def get_video_id(url):
    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        return None

    # Short links
    if hostname == "youtu.be":
        return parsed.path.lstrip("/").split("?")[0]

    # Standard YouTube links
    if "youtube.com" in hostname:

        # watch?v=
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]

        # /shorts/
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]

        # /embed/
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]

    return None


def roadmap_worker_node(state: AgentState) -> AgentState:
    task = state["task"]
    week = state["week"]
    day = state["day"]
    focus = state["focus"]

    url = "https://google.serper.dev/search"
    payload = {
      "q": f"site:youtube.com {task} tutorial OR course OR lecture OR explained"
    }
    headers = {
      'X-API-KEY': os.environ["SERPER_API_KEY"],
      'Content-Type': 'application/json'
    }
    videos = []
    session = requests.Session()
    session.trust_env = False   # ignores system proxy

    for page in range(1):
        payload["page"] = page + 1
        response = session.post(url, headers=headers, json=payload, timeout=30)
        results = json.loads(response.text)["organic"]
        for result in results:
            if "youtube.com" in result["link"]:
                videos.append(result["link"])
    video_ids = []
    urls = {}
    for video in videos:
        video_id = get_video_id(video)
        if not video_id:
            continue
        video_ids.append(video_id)
        urls[video_id] = video

    video_ids_dict = get_counts(video_ids)
    authority_scores_dict = get_authority_scores(video_ids_dict)
    video_summaries = get_video_summaries(authority_scores_dict, urls)

    return {
        "results": [{
            "task": task,
            "focus": focus,
            "week": week,
            "day": day,
            "videos" : video_summaries["videos"]
        }]
    }
#%%
def aggregate_node(state: AgentState):
    unique_tasks = {}
    for task in state["results"]:
        key = (task["week"], task["day"])
        unique_tasks[key] = task   # latest wins
    roadmap = sorted(
        unique_tasks.values(),
        key=lambda x: (x["week"], x["day"])
    )
    return {"final_roadmap": roadmap}
#%%
def save_results(state: AgentState):
    for key in ["serper_results", "urls"]:
        state.pop(key, None)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(state["final_roadmap"], f, indent=2)
    return state
#%%
workflow = StateGraph(AgentState)
workflow.add_node("roadmap_planner_node", roadmap_planner_node)
# workflow.add_node("dispatch_node", dispatch_node)
workflow.add_node("roadmap_worker_node", roadmap_worker_node)
workflow.add_node("aggregate_node", aggregate_node)
workflow.add_node("save_results", save_results)

workflow.set_entry_point("roadmap_planner_node")
workflow.add_edge(START, "roadmap_planner_node")
workflow.add_conditional_edges("roadmap_planner_node", dispatch_node)
workflow.add_edge("roadmap_worker_node", "aggregate_node")
workflow.add_edge("aggregate_node", "save_results")
#workflow.add_edge("dispatch_node", "save_results")
workflow.add_edge("save_results", END)
conn = sqlite3.connect("ai_university.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)
app = workflow.compile(checkpointer=memory)


