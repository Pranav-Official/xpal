from pydantic import BaseModel
from typing import List, Optional
from langgraph.graph import StateGraph, START, END

from lib.embed_docs import retrive_doc_embeddings
from lib.question_generator import question_generator
from lib.report_compiler import report_compiler


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class DocumentState(BaseModel):
    document_scope: str
    questions: Optional[List[str]] = None
    question_answer: Optional[List[QuestionAnswer]] = None
    document_markdown: Optional[str] = None
    document_complete: Optional[bool] = None


def question_generator_wrap(state: DocumentState):
    outline = state.document_scope
    questions = question_generator(outline)
    return {"questions": questions}


def retrive_answers(state: DocumentState):
    questions = state.questions
    question_answer = []
    for question in questions:
        retrived_data = retrive_doc_embeddings(question)
        q_a = {"question": question, "answer": str(retrived_data)}
        question_answer.append(q_a)

    return {"question_answer": question_answer}


def compiler_report(state: DocumentState):
    question_answer = state.question_answer
    document_layout = state.document_scope
    report = report_compiler(document_layout, question_answer)

    return {"document_markdown": report}


def document_generator(document_scope: str):
    workflow = StateGraph(DocumentState)

    workflow.add_node("question_generator", question_generator_wrap)
    workflow.add_node("retrive_answers", retrive_answers)
    workflow.add_node("compiler_report", compiler_report)

    workflow.add_edge(START, "question_generator")
    workflow.add_edge("question_generator", "retrive_answers")
    workflow.add_edge("retrive_answers", "compiler_report")
    workflow.add_edge("compiler_report", END)

    chain = workflow.compile()
    result_state = chain.invoke({"document_scope": document_scope})
    return result_state["document_markdown"]
