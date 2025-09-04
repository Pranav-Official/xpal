from typing import List
from pydantic import BaseModel
from core.model_provider import ModelProvider
from langchain_core.prompts import ChatPromptTemplate


class Scope_output(BaseModel):
    report_markdown: str


scope_definer_prompt = """
You are a expert researcher tasked to create create a comprehensive docuemnt given the layout and a set of question and answers.
You will be given a markdown layout outline of a docuemnt containing heading and subheadeings required to create a docuemnt.
You are also given a set of questions and answers.
Your job is to add relevent content under teh relevet headings refering the questions and answers.
make it really comprehensive with addition factual information. fill all the sections
if questions related to any sectios dont have appropriate asnwer. then under that section mention (required addition research).

then you just return the full report as report_markdown
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            scope_definer_prompt,
        ),
        (
            "human",
            "the document outline is - {scope} and the set of questions and answers are - {qa}",
        ),
    ]
)


def report_compiler(scope: str, qa: str, model_choice: str = "primary"):
    model = ModelProvider().get_model(model_choice)
    structured_model = model.with_structured_output(Scope_output)
    chain = prompt | structured_model
    output = chain.invoke({"scope": scope, "qa": qa})
    return output.report_markdown
