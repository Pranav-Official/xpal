from typing import List
from pydantic import BaseModel
from core.model_provider import ModelProvider
from langchain_core.prompts import ChatPromptTemplate
from core.post_maker_prompt import thread_maker_prompt


model = ModelProvider().get_model()

class ThreadPost(BaseModel):
    post_number: int
    content: str

class Thread(BaseModel):
    title: str
    posts: List[ThreadPost]

class Scope_output(BaseModel):
    all_threads: List[Thread]


scope_definer_prompt = f"""
create 3 viral twitter/x post threads based on the following x post guide
{thread_maker_prompt}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            scope_definer_prompt,
        ),
        (
            "human",
            "This is teh information source - {scope}\n\n create 3 viral twitter/x post threads based on the following query - {qa} - the user instructions - {instructions}",
        ),
    ]
)


def thread_generator(scope: str, qa: str, instructions: str = ''):
    structured_model = model.with_structured_output(Scope_output)
    chain = prompt | structured_model
    output = chain.invoke({"scope": scope, "qa": qa, "instructions": instructions})
    return output.all_threads
