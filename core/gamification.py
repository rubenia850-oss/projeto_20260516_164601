from typing import List, Dict
from core.user_profile import UserProfile

class GamificationEngine:
    def __init__(self, user_profile: UserProfile):
        self.profile = user_profile

    def check_achievements(self, state: dict) -> List[str]:
        unlocked = []
        for key, ach in self.achievements.items():
            if ach["condition"](self.profile, state):
                unlocked.append(ach["name"])
        return unlocked

    @property
    def achievements(self) -> Dict[str, dict]:
        return {
            "primeiro_problema": {
                "name": "🚀 Primeiro Problema",
                "condition": lambda p, s: len(p.session_history) >= 1
            },
            "mestre_calculo": {
                "name": "🧮 Mestre em Cálculo",
                "condition": self._master_calculus
            },
            "explorador": {
                "name": "🌳 Explorador Genealógico",
                "condition": self._used_explorer
            },
            "desafiante": {
                "name": "🎯 Desafiante",
                "condition": self._used_challenge
            },
            "10_problemas": {
                "name": "💪 10 Problemas Resolvidos",
                "condition": lambda p, s: len(p.session_history) >= 10
            },
        }

    def _master_calculus(self, profile, state):
        calculus = [cid for cid, prof in profile.proficiencias.items() if cid.startswith("derivada") or cid.startswith("integra")]
        strong = [cid for cid in calculus if profile.proficiencias[cid].mean() > 0.8]
        return len(strong) >= 2

    def _used_explorer(self, profile, state):
        count = sum(1 for e in state.get("events", []) if e.get("type") == "MODE_TRANSITION" and e.get("to") == "explorador")
        return count >= 2

    def _used_challenge(self, profile, state):
        used = any(e.get("type") == "MODE_TRANSITION" and e.get("to") == "desafio" for e in state.get("events", []))
        completed = state.get("current_mode") == "desafio" and state.get("confidence", 0) > 0.5
        return used and completed
