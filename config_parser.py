from pydantic import (BaseModel, Field, field_validator,
                      model_validator, ValidationError)
from typing import Any, Optional
import sys


class Configs(BaseModel):
    WIDTH: int = Field(gt=0)
    HEIGHT: int = Field(gt=0)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    ALGORITHM: str = "dfs"
    SEED: Optional[int] = None
    model_config = {'extra': 'forbid'}

    @field_validator('ENTRY', 'EXIT', mode='before')
    def cord_validator(cls: "Configs", v: Any) -> Any:
        """
        Validates the entry and exit coordinates string format.

        Args:
            v (Any): The input value, expected to be a string in "x,y" format
                or a tuple of two integers.

        Returns:
            Any: A tuple of two integers (x, y).

        Raises:
            ValueError: If the format is invalid or values are not integers.
        """
        if isinstance(v, str):
            splited = v.split(',')
            if len(splited) != 2:
                raise ValueError("Invalid coordinate format. Expected 'x,y'")
            try:
                x = int(splited[0])
                y = int(splited[1])
                return (x, y)
            except Exception:
                raise ValueError("Coordinates must be integers")
        else:
            if isinstance(v, tuple):
                return v
            else:
                raise ValueError("Value must be a string 'x,y' "
                                 "or a tuple of two integers")

    @model_validator(mode="after")
    def mod_validator(self) -> "Configs":
        """
        Performs post-validation checks on the maze configuration model.

        Checks if coordinates are non-negative, within maze bounds,
        and ensures entry and exit points are distinct.

        Returns:
            Configs: The validated configuration object.

        Raises:
            ValueError: If any constraint validation fails.
        """
        if self.ENTRY[0] < 0 or self.ENTRY[1] < 0:
            raise ValueError("Entry coordinates must be non-negative")
        if self.EXIT[0] < 0 or self.EXIT[1] < 0:
            raise ValueError("Exit coordinates must be non-negative")
        if (self.ENTRY[0] >= self.WIDTH) | (self.ENTRY[1] >= self.HEIGHT):
            raise ValueError("Entry coordinates out of bounds")
        if (self.EXIT[0] >= self.WIDTH) | (self.EXIT[1] >= self.HEIGHT):
            raise ValueError("Exit coordinates out of bounds")
        if (self.ENTRY == self.EXIT):
            raise ValueError("Entry and exit coordinates must be different")
        return self


def load_config(filename: str) -> Configs:
    """
    Loads and parses the maze configuration file.

    Reads a file with KEY=VALUE pairs, ignores lines starting with '#',
    and validates the content against the Configs model.

    Args:
        filename (str): The path to the configuration file.

    Returns:
        Configs: A validated Configs instance.

    Raises:
        SystemExit: If the file cannot be read or configuration is invalid.
    """
    data: dict[str, Any] = {}
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' not in line:
                    raise ValueError("Invalid line format")

                key, value = line.split('=', 1)
                data[key] = value
    except OSError as er:
        print(f"Cannot read configuration file '{filename}': {er}")
        sys.exit(1)
    except ValueError as er:
        print(f"Configuration file error: {er}")
        sys.exit(1)

    try:
        ret = Configs.model_validate(data)
        return ret
    except ValidationError as er:
        print("Configuration error:")
        for error in er.errors():
            loc = str(error['loc'][0]) if error['loc'] else "General"
            msg = error['msg']

            if error['type'] == 'extra_forbidden':
                print(f"- Parameter '{loc}' is not a valid setting.")
            else:
                print(f"- {loc}: {msg}")
        sys.exit(1)
