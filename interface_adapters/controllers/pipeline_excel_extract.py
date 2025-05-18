from typing import Dict, Any
from interface_adapters.controllers.etl_controller import ETLStepInterface


class ExtractExcelStep(ETLStepInterface):
    def __init__(self, excel_use_cases, out_context_key: str = "excel_df"):
        self.uc = excel_use_cases
        self.out_key = out_context_key

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context[self.out_key] = self.uc.get_excel_dataframe()["value"]
        return context
