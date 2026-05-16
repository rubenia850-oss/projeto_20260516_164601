from pipelines.base import BasePipeline
from core.state import MathConversationState
from core.prompts import assemble_prompt

class ReflectivePipeline(BasePipeline):
    def _execute_core(self, state: MathConversationState, **kwargs) -> Dict:
        recent = state.get("_trace", {}).get("recent_interactions", [])
        if not recent:
            return {"result": "Ainda não há interações suficientes para uma autoavaliação."}
        analysis = self.cognitive_diagnosis.analyze_session(recent) if self.cognitive_diagnosis else {}
        strengths = self.user_profile.get_strong_concepts() if self.user_profile else []
        weaknesses = self.user_profile.get_weaknesses() if self.user_profile else []
        prompt = assemble_prompt("reflective_report",
                                 patterns=analysis.get("patterns", []),
                                 gaps=analysis.get("gaps", []),
                                 strengths=strengths,
                                 weaknesses=weaknesses,
                                 proficiency=self.user_profile.get_profile_summary() if self.user_profile else {})
        report = self.llm.invoke(prompt)
        return {"result": report, "cognitive_diagnosis": analysis}
