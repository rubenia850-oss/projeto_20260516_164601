import json, re
from pipelines.base import BasePipeline
from core.state import MathConversationState
from core.prompts import assemble_prompt

class TechnicalConsultantPipeline(BasePipeline):
    def _execute_core(self, state: MathConversationState, **kwargs) -> Dict:
        problem = state["problem"]
        domain = state.get("diagnosis", {}).get("classification", {}).get("dominio", "")
        approaches_prompt = assemble_prompt("consultant_approaches", problem=problem, domain=domain)
        approaches_resp = self.llm.invoke(approaches_prompt)
        approaches = re.findall(r'\d+\.\s*(.*)', approaches_resp) or [approaches_resp]
        results = []
        for app in approaches[:3]:
            code_prompt = assemble_prompt("consultant_code", problem=problem, approach=app)
            code = self.llm.invoke(code_prompt)
            exec_res = self.executor.solve(code)
            verification = self.verifier.verify(problem, code, exec_res.get("result", ""))
            results.append({
                "approach": app,
                "result": exec_res.get("result", ""),
                "verification_score": verification.get("score", 0)
            })
        summary_prompt = assemble_prompt("consultant_summary", problem=problem,
                                         approaches=json.dumps(results, indent=2))
        summary = self.llm.invoke(summary_prompt)
        return {
            "result": summary,
            "approaches": results,
            "consistency_score": max(r["verification_score"] for r in results) if results else 0
        }
