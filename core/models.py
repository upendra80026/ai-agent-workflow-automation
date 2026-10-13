from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time


class WorkflowDefinition(BaseModel):
    workflow_id: str = Field(..., description="Unique Workflow Identifier, e.g. WF001")
    workflow_name: str = Field(..., description="Descriptive name of the workflow")
    trigger: str = Field(..., description="Trigger condition or intent description")
    inputs: str = Field(..., description="Required inputs or data sources")
    steps_raw: str = Field(..., description="Raw arrow-separated or comma-separated steps from Excel")
    steps: List[str] = Field(default_factory=list, description="Parsed ordered list of steps")
    decision_logic: str = Field(..., description="Business decision rules and branching conditions")
    tools_required: List[str] = Field(default_factory=list, description="List of required tools")
    expected_output: str = Field(..., description="Description of the expected output format")


class StepExecutionRecord(BaseModel):
    step_number: int
    step_name: str
    tool_called: Optional[str] = None
    input_params: Dict[str, Any] = Field(default_factory=dict)
    output_summary: Any = None
    status: str = "SUCCESS"  # SUCCESS, WARNING, FAILED, SKIPPED
    decision_notes: Optional[str] = None
    duration_ms: float = 0.0


class DecisionRecord(BaseModel):
    rule: str
    condition_met: bool
    evaluation_details: Dict[str, Any] = Field(default_factory=dict)
    action_taken: str


class ExecutionResult(BaseModel):
    user_request: str
    workflow_id: str
    workflow_name: str
    confidence_score: float = 1.0
    selection_reasoning: str = ""
    steps_executed: List[StepExecutionRecord] = Field(default_factory=list)
    decisions_made: List[DecisionRecord] = Field(default_factory=list)
    final_output: str = ""
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "SUCCESS"  # SUCCESS, FAILED, WARNING
    total_duration_ms: float = 0.0
    error: Optional[str] = None

    def to_readable_summary(self) -> str:
        lines = []
        lines.append(f"══════════════════════════════════════════════════════════════")
        lines.append(f"🎯 Selected Workflow: {self.workflow_id} - {self.workflow_name}")
        lines.append(f"📊 Confidence: {self.confidence_score * 100:.1f}%")
        lines.append(f"💡 Selection Reasoning: {self.selection_reasoning}")
        lines.append(f"──────────────────────────────────────────────────────────────")
        lines.append(f"📋 Steps Executed ({len(self.steps_executed)}):")
        for step in self.steps_executed:
            tool_info = f" [Tool: {step.tool_called}]" if step.tool_called else ""
            lines.append(f"  {step.step_number}. {step.step_name}{tool_info} ({step.status})")
            if step.decision_notes:
                lines.append(f"     ↳ Logic: {step.decision_notes}")
        lines.append(f"──────────────────────────────────────────────────────────────")
        if self.decisions_made:
            lines.append(f"⚖️ Conditions & Decisions Evaluated ({len(self.decisions_made)}):")
            for d in self.decisions_made:
                icon = "✓" if d.condition_met else "✗"
                lines.append(f"  [{icon}] {d.rule} -> {d.action_taken}")
            lines.append(f"──────────────────────────────────────────────────────────────")
        lines.append(f"🏁 Final Result:")
        lines.append(f"{self.final_output}")
        lines.append(f"══════════════════════════════════════════════════════════════")
        return "\n".join(lines)
