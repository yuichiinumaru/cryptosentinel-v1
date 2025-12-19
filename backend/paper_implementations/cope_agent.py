import re
import random
from collections import Counter
from typing import List, Tuple, Optional
import os

from agno.agent import Agent
from agno.models.base import Model
from backend.factory import create_agent
from backend.config import Config

class CopeAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.small_model = Config.get_model(os.getenv("SMALL_MODEL", "openai/gpt-4o-mini"))
        self.large_model = Config.get_model(os.getenv("LARGE_MODEL", "openai/gpt-4o"))

        self.planner = self._create_planner_agent(self.small_model)

        self.n_samples = 8
        self.threshold_1 = 0.75
        self.threshold_2 = 0.5

    def _create_planner_agent(self, model: Model) -> Agent:
        return create_agent(
            name="PlannerAgent",
            role="Planner",
            instructions_path="backend/paper_implementations/planner_instructions.md",
            model_id=model.id,
        )

    def _extract_answer(self, solution: str) -> str:
        return solution.strip()

    def _get_consensus_data(self, results: List[Tuple[str, str]], threshold: float) -> Tuple[Optional[str], Optional[str]]:
        if not results:
            return None, None

        answers = [r[1] for r in results if r[1]]
        if not answers:
            return None, None

        counts = Counter(answers)
        if not counts:
            return None, None

        most_common_answer, count = counts.most_common(1)[0]

        ratio = count / len(answers)

        winning_plans = [r[0] for r in results if r[1] == most_common_answer]
        selected_plan = random.choice(winning_plans) if winning_plans else None

        if ratio >= threshold:
            return most_common_answer, selected_plan
        else:
            return None, selected_plan

    def reason(self, task: str) -> str:
        """
        Orchestrates the multi-round planning and reasoning process.
        """
        # Round 1
        answer, plan_s = self._round_1(task)
        if answer:
            return answer

        # Round 2
        answer, plan_l = self._round_2(task, plan_s)
        if answer:
            return answer

        # Round 3
        return self._round_3(task, plan_l)

    def _round_1(self, task: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Small model planning and reasoning.
        """
        results = []
        reasoner_agent = create_agent(
            name="SmallReasoner",
            role="Reasoner",
            model_id=self.small_model.id,
        )
        for _ in range(self.n_samples):
            plan = self.planner.run(f"Generate a plan for this task:\n{task}")
            solution = reasoner_agent.run(f"Task: {task}\n\nPlan: {plan}\n\nProvide a solution following the plan.")
            answer = self._extract_answer(solution)
            results.append((plan, answer))

        return self._get_consensus_data(results, self.threshold_1)

    def _round_2(self, task: str, plan_s: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Large model planning, small model reasoning.
        """
        if plan_s is None:
            plan_s = self.planner.run(f"Generate a plan for this task:\n{task}")

        large_planner = self._create_planner_agent(self.large_model)
        plan_l = large_planner.run(f"Generate a plan for this task:\n{task}")

        results = []
        reasoner_agent = create_agent(
            name="SmallReasoner",
            role="Reasoner",
            model_id=self.small_model.id,
        )
        prompt = f"Task: {task}\n\nPlan from small model: {plan_s}\n\nPlan from large model: {plan_l}\n\nProvide a solution following the plans."
        for _ in range(self.n_samples):
            solution = reasoner_agent.run(prompt)
            answer = self._extract_answer(solution)
            results.append((plan_l, answer))

        majority_answer, _ = self._get_consensus_data(results, self.threshold_2)
        return majority_answer, plan_l

    def _round_3(self, task: str, plan_l: str) -> str:
        """
        Large model planning and reasoning.
        """
        if plan_l is None: # Fallback
            large_planner = self._create_planner_agent(self.large_model)
            plan_l = large_planner.run(f"Generate a plan for this task:\n{task}")

        large_reasoner = create_agent(
            name="LargeReasoner",
            role="Reasoner",
            model_id=self.large_model.id,
        )
        prompt = f"Task: {task}\n\nPlan: {plan_l}\n\nProvide a solution following the plan."
        solution = large_reasoner.run(prompt)
        return self._extract_answer(solution)
