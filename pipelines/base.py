from typing import Dict, Any
from abc import ABC, abstractmethod
from core.state import MathConversationState
from core.llm import LLMManager
from core.math_executor_hybrid import MathExecutorHybrid
from core.self_consistency import SelfConsistencyEngine
from core.advanced_verifier import AdvancedVerifier
from core.confidence_engine import ConfidenceEngine
from core.ontology import MathOntology
from core.user_profile import UserProfile
from core.cognitive_diagnosis import CognitiveDiagnosisEngine

class BasePipeline(ABC):
    def __init__(
        self,
        llm: LLMManager,
        executor: MathExecutorHybrid,
        self_consistency: SelfConsistencyEngine,
        verifier: AdvancedVerifier,
        confidence_engine: ConfidenceEngine,
        ontology: MathOntology,
        user_profile: UserProfile = None,
        cognitive_diagnosis: CognitiveDiagnosisEngine = None,
    ):
        self.llm = llm
        self.executor = executor
        self.self_consistency = self_consistency
        self.verifier = verifier
        self.confidence_engine = confidence_engine
        self.ontology = ontology
        self.user_profile = user_profile
        self.cognitive_diagnosis = cognitive_diagnosis

    def run(self, state: MathConversationState, **kwargs) -> Dict:
        self._pre_process(state, **kwargs)
        result = self._execute_core(state, **kwargs)
        return self._post_process(state, result, **kwargs)

    def _pre_process(self, state: Dict, **kwargs):
        pass

    @abstractmethod
    def _execute_core(self, state: Dict, **kwargs) -> Dict:
        pass

    def _post_process(self, state: Dict, result: Dict, **kwargs) -> Dict:
        state.update(result)
        verification = self.verifier.verify(
            state["problem"],
            state.get("code", ""),
            state.get("result", ""),
            context={"domain": state.get("diagnosis", {}).get("dominio")}
        )
        state["verification"] = verification
        confidence_result = self.confidence_engine.calibrate(
            verifier_output=verification,
            consistency_score=state.get("consistency_score", 80.0),
            user_profile=self.user_profile.get_profile_summary() if self.user_profile else None,
            context={"domain": state.get("diagnosis", {}).get("dominio")}
        )
        state["confidence"] = confidence_result["score"]
        state["confidence_level"] = confidence_result["level"]
        return state
