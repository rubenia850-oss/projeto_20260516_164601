from io import BytesIO
import base64
import matplotlib.pyplot as plt
import sympy as sp
from pipelines.base import BasePipeline
from core.state import MathConversationState
from core.prompts import assemble_prompt
from core.tools import extract_code

class GeometryPipeline(BasePipeline):
    def _execute_core(self, state: MathConversationState, **kwargs) -> Dict:
        problem = state["problem"]
        diagnosis = state.get("diagnosis", {}).get("classification", {})
        domain = diagnosis.get("dominio", "")
        prompt = assemble_prompt("geometry_solver", problem=problem, plan=domain, equations="")
        sc_result = self.self_consistency.generate_and_select(prompt)
        code = sc_result.get("code", "")
        result = sc_result.get("result", "")
        plot_prompt = assemble_prompt("geometry_plot", problem=problem)
        plot_code = self.llm.invoke(plot_prompt)
        plot_url = None
        if plot_code:
            try:
                clean_plot = extract_code(plot_code)
                exec_env = {'sp': sp, 'plt': plt, 'np': __import__('numpy')}
                exec(clean_plot, exec_env)
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
                buf.seek(0)
                plot_url = f"data:image/png;base64,{base64.b64encode(buf.read()).decode()}"
                plt.close('all')
            except Exception:
                pass
        return {
            "code": code,
            "result": result,
            "consistency_score": sc_result.get("consistency_score", 0),
            "plot_url": plot_url
        }
