import os
import google.generativeai as genai
from deepeval.models.base_model import DeepEvalBaseLLM
from dotenv import load_dotenv
load_dotenv()

class GeminiJudge(DeepEvalBaseLLM):
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        self.model_name = model_name
        # Now os.environ.get will actually find your key
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(
            prompt,
            # Force Gemini to output valid JSON for DeepEval
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return response.text

    async def a_generate(self, prompt: str) -> str:
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return response.text

    def get_model_name(self):
        return f"Google/{self.model_name}"

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall

def test_arima_schema_adherence():
    llm_tool_call = ToolCall(
        name="instantiate_estimator",
        input_parameters={"estimator_name": "ARIMA", "maxiter": "hundred"}  # Hallucination
    )
    test_case = LLMTestCase(
        input="Instantiate ARIMA with max iterations set to one hundred.",
        actual_output="I called instantiate_estimator with maxiter='hundred'.",
        tools_called=[llm_tool_call]
    )
    metric = GEval(
        name="MCP Schema Adherence",
        criteria=(
            "The tool parameters must match the JSON schema. "
            "'maxiter' must be an integer. A string value is a schema violation."
        ),
        evaluation_params=[LLMTestCaseParams.TOOLS_CALLED],
        model=GeminiJudge(),
        threshold=0.5
    )
    from deepeval import evaluate
    evaluate([test_case], [metric])

if __name__ == "__main__":
    test_arima_schema_adherence()
