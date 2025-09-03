from typing import List
from pydantic import BaseModel
from core.model_provider import ModelProvider
from langchain_core.prompts import ChatPromptTemplate


model = ModelProvider().get_model()


class Scope_output(BaseModel):
    questions: List[str]


scope_definer_prompt = """
You are a expert researcher tasked to create a set of questions that you can ask to get infomration to complete a document.
you will be given a document with headline and subheads which indicates teh layout for teh documnet. you task is to generate a set of short questiosn that will allow you to get information to fill teh documnet

"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            scope_definer_prompt,
        ),
        ("human", "the document outline is - {scope}"),
    ]
)


def question_generator(scope: str):
    structured_model = model.with_structured_output(Scope_output)
    chain = prompt | structured_model
    output = chain.invoke({"scope": scope})
    return output.questions
