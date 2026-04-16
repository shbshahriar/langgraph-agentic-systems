from pydantic import BaseModel, Field
from typing import Annotated, Literal


class DiagnosisOutput(BaseModel):
    issue_type: Annotated[
        Literal[
            "bug",
            "performance",
            "ux",
            "billing",
            "feature_request",
            "support",
            "other",
        ],
        Field(description="Type of issue reported"),
    ]

    tone: Annotated[
        Literal["angry", "frustrated", "confused", "neutral", "polite"],
        Field(description="Tone of the feedback"),
    ]

    urgency: Annotated[
        Literal["low", "medium", "high", "critical"],
        Field(description="Urgency level of the issue"),
    ]

    department: Annotated[
        Literal["engineering", "product", "support", "billing"],
        Field(description="Department to route the issue to"),
    ]

    summary: Annotated[
        str,
        Field(description="One-line description of the issue, used by response nodes"),
    ]
