from pydantic import BaseModel
from core.model_provider import ModelProvider
from langchain_core.prompts import ChatPromptTemplate


model = ModelProvider().get_model()


class Scope_output(BaseModel):
    markdown: str


scope_definer_prompt = """
You are a expert researcher tasked to create the layout of a brief but comprehensive research document,
You will be given a search term related to health, it might be products, ingredients, chemicals, therapies etc.
You must construct the layout out of headings and subheadings and organise that in to a mardown text.

"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            scope_definer_prompt,
        ),
        ("human", "the search term is - {search_term}"),
    ]
)


def scope_definer(search_term: str):
    structured_model = model.with_structured_output(Scope_output)
    chain = prompt | structured_model
    output = chain.invoke({"search_term": search_term})
    return output.markdown
