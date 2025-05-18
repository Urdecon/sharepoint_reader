# interface_adapters/controllers/etl_controller.py
import logging
from typing import List, Dict, Any, Optional


class ETLStepInterface:
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class ETLController:
    """Orquesta la secuencia de Steps (Extract, Transform, Load…)."""

    def __init__(self, steps: List[ETLStepInterface]) -> None:
        if not steps:
            raise ValueError("Lista de steps vacía")
        self.logger = logging.getLogger(__name__)
        self.steps = steps

    def run_etl_process(
        self, initial_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = initial_context or {}
        for step in self.steps:
            step_name = step.__class__.__name__
            self.logger.info("▶ Ejecutando %s", step_name)
            context = step.run(context)
            self.logger.info("✓ %s OK", step_name)
        return context
