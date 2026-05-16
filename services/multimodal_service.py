from typing import Dict
from core.llm import LLMManager
from core.prompts import assemble_prompt
from services.ocr_service import OCRService

class MultimodalService:
    def __init__(self, llm: LLMManager):
        self.llm = llm
        self.ocr = OCRService()

    def process_image(self, image_path: str) -> Dict:
        ocr_result = self.ocr.extract_text(image_path)
        if not ocr_result.get("success", False):
            return {"success": False, "problem_text": "", "ocr_text": "", "method": "error", "diagram_detected": False, "error": ocr_result.get("error")}
        ocr_text = ocr_result["text"]
        ocr_confidence = ocr_result["confidence"]
        diagram_detected = self._detect_diagram(ocr_text)
        prompt = assemble_prompt("multimodal_interpreter", ocr_text=ocr_text, ocr_confidence=ocr_confidence)
        interpretation = self.llm.invoke(prompt)
        interpretation = self._sanitize_interpretation(interpretation)
        return {"success": True, "problem_text": interpretation.strip() or ocr_text, "ocr_text": ocr_text, "method": "ocr+llm", "diagram_detected": diagram_detected, "ocr_confidence": ocr_confidence}

    def _detect_diagram(self, text: str) -> bool:
        if len(text) < 20: return True
        return any(kw in text.lower() for kw in ["figura", "gráfico", "diagrama", "desenho", "imagem", "plot"])

    def _sanitize_interpretation(self, text: str) -> str:
        if len(text) > 3000: text = text[:3000] + "..."
        for d in ["__import__", "os.", "subprocess", "eval(", "exec(", "system("]:
            text = text.replace(d, "[BLOCKED]")
        return text.strip()
