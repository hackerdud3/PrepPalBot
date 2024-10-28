from ragas import SingleTurnSample
from ragas.metrics import ResponseRelevancy
from typing import List
import asyncio


# Calculate relevancy score
def calculate_relevancy(user_input: str, response: str, retrieved_contexts: List[str]):

    sample = SingleTurnSample(
        user_input=user_input, response=response, retrieved_contexts=retrieved_contexts
    )

    # Instance of ResponseRelevancy
    relevancy_scorer = ResponseRelevancy()

    # Compute and return the relevancy score
    async def get_score():
        return await relevancy_scorer.single_turn_ascore(sample)

    # Run the async function
    return asyncio.run(get_score())
