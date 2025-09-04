from typing import List
from pydantic import BaseModel
from core.model_provider import ModelProvider
from langchain_core.prompts import ChatPromptTemplate
from operator import index


thread_ranker_system_prompt = """
**Objective:**
Evaluate and rank provided X (Twitter) threads in order of maximum potential virality. For each thread, analyze:
- Hook strength and scroll-stopping power
- Employed psychological triggers
- Content structure and thread formatting
- Alignment with proven viral formulas
- Use of social proof, emotional language, and curiosity
- Adherence to X algorithm preferences for reach and engagement

### Ranking Criteria

1. **Viral Potential (40%)**
   - Does the thread leverage high-arousal emotions or identity-based triggers (awe, amusement, anger, insight, social belonging)?
   - Are psychological motivators (curiosity, FOMO, validation, self-enhancement) detectable?
   - Is the message crafted for maximum sharing/engagement?[5][6]

2. **Hook Effectiveness (30%)**
   - Is the hook clear, bold, and does it immediately address a pain point, reversal, surprising fact, or compelling narrative?[2][8][9]
   - Does it use proven formulas (Bold Statement, Contrarian, Question, Data-driven, Curiosity Gap, Story)?
   - How quickly and efficiently does the hook communicate unique value or reason to read on?

3. **Thread Structure & Formatting (15%)**
   - Does the thread follow a viral structure: Hook → Context → Story/Framework → Lessons → CTA?[3][1][2]
   - Are tweets concise, scannable, numbered, and visually appealing (white space, lists, emojis where appropriate)?

4. **Algorithm Alignment (10%)**
   - Is the thread crafted to encourage replies/conversation?
   - Is the content topical, original, or related to shareable trends?
   - Does it contain opportunities for early engagement velocity and sustained retention?[4][10]

5. **Language & Copywriting Quality (5%)**
   - Are power words and social proof used to increase trust and virality?[7][8][11]
   - Is the messaging clear, compelling, and free from unnecessary complexity or jargon?

### Output Format

For each thread, output:
- **Virality Score (0–100):** Weight and aggregate all above factors.
- **Hook Score (0–10):** Isolate the strength of the opening lines.
- **Strengths:** Concise bullet points of what works.
- **Weaknesses:** Concise bullet points of what could be improved.
- **Summary Justification:** 2-3 sentences explaining the rank and key virality drivers.

Order threads from highest to lowest overall virality score.

**Instruction:**
Strictly evaluate based on structural, psychological, and algorithmic factors shown to drive viral performance on X. Do not consider time of day, posting frequency, external links, or off-platform factors.
"""


class Score(BaseModel):
    virality_score: int
    hook_score: int
    strengths: List[str]
    weaknesses: List[str]
    summary_justification: str


class ThreadScore(BaseModel):
    title: str
    index: int
    scores: Score


class Score_Output(BaseModel):
    all_thread_scores: List[ThreadScore]


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            thread_ranker_system_prompt,
        ),
        (
            "human",
            "These are the threads - {all_threads}\n\n rank them accordingly",
        ),
    ]
)


def thread_ranker(all_threads: str, model_choice: str = "tertiary"):
    model = ModelProvider().get_model(model_choice)
    structured_model = model.with_structured_output(Score_Output)
    chain = prompt | structured_model
    output = chain.invoke({"all_threads": all_threads})
    return output.all_thread_scores
