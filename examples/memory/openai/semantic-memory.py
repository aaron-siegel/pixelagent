# pip install sentence-transformers

import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.functions.huggingface import sentence_transformer

from pixelagent.openai import Agent

embed_model = sentence_transformer.using(model_id="intfloat/e5-large-v2")

# First Create the Agent
agent = Agent(
    name="semantic_bot", system_prompt="You’re my assistant.", reset=False
)

# Get the Agents Memory table and add embedding index to the content
memory = pxt.get_table("semantic_bot.memory")

memory.add_computed_column(
    user_content=pxtf.string.format(
        "{0}: {1}: {2}", memory.timestamp, memory.role, memory.content
    ),
    if_exists="ignore",
)

memory.add_embedding_index(
    column="user_content",
    idx_name="user_content_idx",
    string_embed=embed_model,
    if_exists="ignore",
)


def semantic_search(query: str) -> list[dict]:
    sim = memory.user_content.similarity(query, idx="user_content_idx")
    res = (
        memory.order_by(sim, asc=False)
        .select(memory.user_content, sim=sim)
        .limit(5)
        .collect()
    )
    result_str = "\n".join(
        f"Previous conversations: {user_content}"
        for user_content in res["user_content"]
    )
    return result_str


# Load some data into memory
agent.chat("What are your favorite travel destinations?")
agent.chat("Can you recommend some activities in Paris?")

# test the semantic search
query = "vacation ideas"
context_from_previous_conversations = semantic_search(query)
print(context_from_previous_conversations)
