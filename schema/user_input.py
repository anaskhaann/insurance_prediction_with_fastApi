from typing import Annotated, Literal

from pydantic import BaseModel, Field, computed_field, field_validator

from config.city_tier import tier_1_cities, tier_2_cities

# ************************ Pydantic Model


class UserData(BaseModel):
    age: Annotated[int, Field(..., description="Age of the User", gt=0, le=80)]
    weight: Annotated[float, Field(..., description="Weight of the User", gt=0)]
    height: Annotated[float, Field(..., description="Height of the User", gt=0)]
    income_lpa: Annotated[
        float, Field(..., description="Annual Salary of the User In LPA", gt=0)
    ]
    smoker: Annotated[bool, Field(..., description="Is User a Smoker")]
    city: Annotated[str, Field(..., description="City of the User")]
    occupation: Annotated[
        Literal[
            "retired",
            "freelancer",
            "student",
            "government_job",
            "business_owner",
            "unemployed",
            "private_job",
        ],
        Field(..., description="Occupation of the User"),
    ]

    """
    Add Field Validator to Handle casing of the city name
    """

    @field_validator("city")
    @classmethod
    def city(cls, value: str) -> str:
        v = value.strip().title()
        return v

    """
    Compute Feature Values
    """

    # BMI Feild
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)

    # Age Group Field
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    # Lifestyle Field
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    # City Tier
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3
