from pydantic import BaseModel
from typing import List, Optional
from langgraph.graph import StateGraph, START, END
import uuid
import pandas as pd


from lib.article_search import SearchResultItem, search_articles
from lib.markdown_convert import MarkdownConverter
from lib.scope_definer import scope_definer
from lib.generate_thread import thread_generator
from lib.thread_ranker import thread_ranker
from lib.generate_thread import Thread

from core.sql_lite_conf import sqllite_conn


class State(BaseModel):
    user_search_term: str
    instructions: str = ""
    search_count: int = 10
    search_results: Optional[List[SearchResultItem]] = None
    research_scope: Optional[str] = None
    all_articles: Optional[List[str]] = None
    threads: Optional[List[Thread]] = None
    ranked_thread: Optional[Thread] = None
    model_choice: str = "primary"


def search_articles_wrap(state: State):
    search_term = state.user_search_term
    if search_term:
        search_results = search_articles(search_term, state.search_count)
        return {"search_results": search_results}


def research_scope_definer(state: State):
    search_term = state.user_search_term
    scope = scope_definer(search_term, state.model_choice)

    return {"research_scope": scope}


def fetch_search_results(state: State):
    search_results = state.search_results
    mdCon = MarkdownConverter()
    total = []
    for result in search_results:
        try:
            markdown = mdCon.convert_url_to_markdown(result.url).text_content
            total.append(markdown)
        except Exception as e:
            continue

    return {"all_articles": total}


def display_search(state: State):
    print(state.search_results)


def generate_threads(state: State):
    threads = thread_generator(
        str(state.all_articles), state.user_search_term, state.instructions, state.model_choice
    )
    return {"threads": threads}


def rank_threads(state: State):
    threads = state.threads
    if not threads:
        return {"ranked_threads": []}
    ranked_threads = thread_ranker(str(threads), state.model_choice)
    score = 0
    selected_index = 0
    for thread in ranked_threads:
        ranked_score = thread.scores.virality_score + thread.scores.hook_score
        if ranked_score > score:
            score = ranked_score
            selected_index = thread.index
    selected_thread = threads[selected_index - 1]
    print("selected_thread:", selected_thread)
    return {"ranked_thread": selected_thread}


def start_research_workflow(search_term: str, count: int, instructions: str, model_choice: str = "primary"):

    job_id = uuid.uuid1()
    df = pd.DataFrame(
        {
            "job_id": [str(job_id)],
            "user_search_term": [search_term],
            "search_count": [count],
            "instructions": [instructions],
        }
    )
    df.to_sql("jobs", con=sqllite_conn, if_exists="append", index=False)

    workflow = StateGraph(State)

    workflow.add_node("search_articles", search_articles_wrap)
    workflow.add_node("display_search", display_search)
    workflow.add_node("fetch_search_results", fetch_search_results)
    workflow.add_node("generate_threads", generate_threads)
    workflow.add_node("rank_threads", rank_threads)

    workflow.add_edge(START, "search_articles")
    workflow.add_edge("search_articles", "display_search")
    workflow.add_edge("display_search", "fetch_search_results")
    workflow.add_edge("fetch_search_results", "generate_threads")
    workflow.add_edge("generate_threads", "rank_threads")
    workflow.add_edge("rank_threads", END)

    chain = workflow.compile()

    # image_bytes = chain.get_graph().draw_mermaid_png()
    # with open("graph.png", "wb") as f:
    #     f.write(image_bytes)

    result_state = chain.invoke(
        {
            "user_search_term": search_term,
            "search_count": count,
            "instructions": instructions,
            "model_choice": model_choice,
        }
    )
    print(result_state["threads"])
    return result_state["ranked_thread"]
