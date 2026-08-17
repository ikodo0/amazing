from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal, Any


class Config(BaseModel):
    WIDTH: int = Field(gt=0)
    HEIGHT: int = Field(gt=0)
    ENTRY: tuple[int, int] = Field()
    EXIT: tuple[int, int] = Field()
    PERFECT: bool = Field()
    OUTPUT_FILE: str = Field()
    SEED: Optional[int] = Field(default=None)
    PATTERN: Optional[bool] = Field(default=True)
    MODE: Literal["dfs", "dfs_gt"] = Field(default="dfs")
    WINDOW_HEIGHT: int = Field(gt=0, lt=1000)
    WINDOW_WIDTH: int = Field(gt=0, lt=1001)

    @field_validator("ENTRY", "EXIT", mode="before")
    @classmethod
    def parse_coords(cls, value: Any) -> Any:
        return value.split(",")

    @model_validator(mode="after")
    def borders_check(self) -> "Config":
        def isoutofbound(obj: tuple[int, int]) -> bool:
            x, y = obj
            return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT
        if self.ENTRY == self.EXIT:
            raise ValueError("ENTRY and EXIT must differ.")
        if not isoutofbound(self.ENTRY):
            raise ValueError("Entry point is out of bound.")
        if not isoutofbound(self.EXIT):
            raise ValueError("Exit point is out of bound.")
        return self


def read_config(config: str) -> Config:
    with open(config) as file:
        items = file.read().split("\n")
        data = dict()
        for item in items:
            item = item.strip()
            if item == "":
                continue
            if item.startswith('#'):
                continue
            if "=" not in item:
                raise ValueError(
                    f"{config}: expected KEY=VALUE, got '{item}'"
                    )
            key, value = item.split("=", 1)
            data[key] = value
        return Config.model_validate(data)
