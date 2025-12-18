"""
LLM Council - Multi-model deliberation with peer review.

Implements the 3-stage deliberation process:
1. Stage 1: Query all models in parallel
2. Stage 2: Anonymous peer review and ranking
3. Stage 3: Chairman synthesis

Inspired by external/llm-council but integrated with our unified architecture.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional
import re

from .llm_clients import OpenRouterClient, LLMResponse


@dataclass
class CouncilConfig:
    """Configuration for the LLM Council."""

    council_models: list[str]
    chairman_model: str


# Default configuration
DEFAULT_CONFIG = CouncilConfig(
    council_models=[
        "openai/gpt-4o",
        "anthropic/claude-3-5-sonnet",
        "google/gemini-2.0-flash-exp",
        "meta-llama/llama-3.3-70b-instruct",
    ],
    chairman_model="google/gemini-2.0-flash-thinking-exp",
)


@dataclass
class CouncilResult:
    """Complete result from council deliberation."""

    query: str
    stage1_responses: dict[str, LLMResponse]
    stage2_rankings: dict[str, dict]  # model -> {ranking: [...], reasoning: str}
    aggregate_rankings: list[tuple[str, float]]  # [(model, avg_rank), ...]
    final_answer: str
    chairman_model: str


class LLMCouncil:
    """
    LLM Council implementation.

    Example usage:
        council = LLMCouncil()
        result = await council.deliberate("What is the best programming language for beginners?")
        print(result.final_answer)
    """

    def __init__(self, config: Optional[CouncilConfig] = None, api_key: Optional[str] = None):
        self.config = config or DEFAULT_CONFIG
        self.api_key = api_key

        # Create clients for all council models
        self.council_clients = {
            model: OpenRouterClient(model=model, api_key=api_key)
            for model in self.config.council_models
        }

        # Create chairman client
        self.chairman_client = OpenRouterClient(
            model=self.config.chairman_model, api_key=api_key
        )

    async def stage1_collect_responses(self, query: str) -> dict[str, LLMResponse]:
        """
        Stage 1: Query all council models in parallel.

        Returns dict of model_id -> LLMResponse
        """
        tasks = []
        for model, client in self.council_clients.items():
            task = asyncio.create_task(client.query(query))
            tasks.append((model, task))

        responses = {}
        for model, task in tasks:
            try:
                response = await task
                responses[model] = response
            except Exception as e:
                # Graceful degradation - continue with successful responses
                print(f"Warning: {model} failed: {e}")

        return responses

    async def stage2_collect_rankings(
        self, query: str, responses: dict[str, LLMResponse]
    ) -> tuple[dict[str, dict], dict[str, str]]:
        """
        Stage 2: Anonymous peer review and ranking.

        Each model evaluates all responses (including their own, anonymized).
        Returns (rankings_dict, label_to_model mapping)
        """
        # Create anonymous labels
        models = list(responses.keys())
        labels = [chr(65 + i) for i in range(len(models))]  # A, B, C, ...
        label_to_model = dict(zip(labels, models))

        # Build anonymized responses text
        anonymized_text = ""
        for label, model in label_to_model.items():
            content = responses[model].content
            anonymized_text += f"\n\n--- Response {label} ---\n{content}"

        # Create ranking prompt
        ranking_prompt = f"""You are evaluating multiple AI responses to this question:

QUESTION: {query}

Here are the responses to evaluate:{anonymized_text}

Please evaluate each response for:
1. Accuracy and correctness
2. Completeness and depth
3. Clarity and helpfulness
4. Insight and unique value

Then provide your final ranking from best to worst.

IMPORTANT: Format your ranking exactly like this:
FINAL RANKING:
1. Response [letter]
2. Response [letter]
...

Provide brief reasoning for your ranking, then end with the FINAL RANKING section."""

        # Query all models for rankings in parallel
        tasks = []
        for model, client in self.council_clients.items():
            task = asyncio.create_task(client.query(ranking_prompt))
            tasks.append((model, task))

        rankings = {}
        for model, task in tasks:
            try:
                response = await task
                parsed_ranking = self._parse_ranking(response.content, labels)
                rankings[model] = {
                    "raw_text": response.content,
                    "parsed_ranking": parsed_ranking,
                }
            except Exception as e:
                print(f"Warning: Ranking from {model} failed: {e}")

        return rankings, label_to_model

    def _parse_ranking(self, text: str, valid_labels: list[str]) -> list[str]:
        """Parse ranking from model response."""
        # Look for FINAL RANKING section
        pattern = r"FINAL RANKING:(.+?)(?:\n\n|\Z)"
        ranking_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if ranking_match:
            ranking_text = ranking_match.group(1)
        else:
            ranking_text = text

        # Extract response letters in order
        pattern = r"Response\s+([A-Z])"
        matches = re.findall(pattern, ranking_text, re.IGNORECASE)

        # Filter to valid labels and remove duplicates while preserving order
        seen = set()
        ranking = []
        for label in matches:
            label = label.upper()
            if label in valid_labels and label not in seen:
                seen.add(label)
                ranking.append(label)

        return ranking

    def calculate_aggregate_rankings(
        self, rankings: dict[str, dict], label_to_model: dict[str, str]
    ) -> list[tuple[str, float]]:
        """Calculate aggregate ranking scores across all evaluations."""
        scores: dict[str, list[int]] = {model: [] for model in label_to_model.values()}

        for evaluator, ranking_data in rankings.items():
            parsed = ranking_data.get("parsed_ranking", [])
            for position, label in enumerate(parsed, 1):
                model = label_to_model.get(label)
                if model:
                    scores[model].append(position)

        # Calculate average position (lower is better)
        averages = []
        for model, positions in scores.items():
            if positions:
                avg = sum(positions) / len(positions)
                averages.append((model, avg))
            else:
                averages.append((model, float("inf")))

        # Sort by average position (ascending)
        averages.sort(key=lambda x: x[1])
        return averages

    async def stage3_synthesize(
        self,
        query: str,
        responses: dict[str, LLMResponse],
        rankings: dict[str, dict],
        aggregate_rankings: list[tuple[str, float]],
    ) -> str:
        """
        Stage 3: Chairman synthesizes final answer.

        Takes all responses and rankings to produce the best final answer.
        """
        # Build context for chairman
        responses_text = ""
        for model, response in responses.items():
            rank_index = None
            for i, (m, _) in enumerate(aggregate_rankings, start=1):
                if m == model:
                    rank_index = i
                    break

            rank_str = f" (Ranked #{rank_index})" if rank_index is not None else ""
            responses_text += f"\n\n--- {model}{rank_str} ---\n{response.content}"

        # Build rankings summary
        rankings_summary = "Aggregate Rankings (by peer review):\n"
        for i, (model, avg_rank) in enumerate(aggregate_rankings, 1):
            rankings_summary += f"{i}. {model} (avg position: {avg_rank:.2f})\n"

        synthesis_prompt = (
            "You are the Chairman of an LLM Council. "
            "Your role is to synthesize the best possible answer "
            "from multiple AI responses.\n\n"
            f"ORIGINAL QUESTION: {query}\n\n"
            "COUNCIL RESPONSES:\n"
            f"{responses_text}\n\n"
            "PEER REVIEW RESULTS:\n"
            f"{rankings_summary}\n\n"
            "Your task:\n"
            "1. Consider all responses, giving more weight to higher-ranked ones\n"
            "2. Identify the most accurate, complete, and insightful points\n"
            "3. Synthesize a comprehensive final answer that combines the best elements\n"
            "4. Ensure the answer is clear, well-structured "
            "and directly addresses the question\n\n"
            "Provide your synthesized answer:"
        )

        response = await self.chairman_client.query(synthesis_prompt)
        return response.content

    async def deliberate(self, query: str) -> CouncilResult:
        """
        Run full council deliberation.

        This is the main entry point that orchestrates all three stages.
        """
        # Stage 1: Collect individual responses
        print("Stage 1: Collecting responses from council...")
        responses = await self.stage1_collect_responses(query)

        if len(responses) < 2:
            raise ValueError("Not enough successful responses for deliberation")

        # Stage 2: Peer review and ranking
        print("Stage 2: Peer review and ranking...")
        rankings, label_to_model = await self.stage2_collect_rankings(query, responses)
        aggregate_rankings = self.calculate_aggregate_rankings(rankings, label_to_model)

        # Stage 3: Chairman synthesis
        print("Stage 3: Chairman synthesis...")
        final_answer = await self.stage3_synthesize(
            query, responses, rankings, aggregate_rankings
        )

        return CouncilResult(
            query=query,
            stage1_responses=responses,
            stage2_rankings=rankings,
            aggregate_rankings=aggregate_rankings,
            final_answer=final_answer,
            chairman_model=self.config.chairman_model,
        )

