from pipelines.base import BasePipeline
from core.state import MathConversationState
from core.prompts import assemble_prompt

class ProbabilityPipeline(BasePipeline):
    def _execute_core(self, state: MathConversationState, **kwargs) -> Dict:
        problem = state["problem"]
        diagnosis = state.get("diagnosis", {}).get("classification", {})
        domain = diagnosis.get("dominio", "")
        eqs = getattr(self, 'knowledge_base', None)
        eq_context = ""
        if eqs:
            items = eqs.retrieve(problem, k=4, min_confidence=2)
            eq_context = "\n".join([item.content for item in items])
        prompt = assemble_prompt("probability_solver", problem=problem, plan=domain, equations=eq_context)
        sc_result = self.self_consistency.generate_and_select(prompt)
        return {
            "code": sc_result.get("code", ""),
            "result": sc_result.get("result", ""),
            "consistency_score": sc_result.get("consistency_score", 0)
        }
