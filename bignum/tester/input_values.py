from dataclasses import dataclass, field
from typing import Optional
from .num_properties import NumProperties
import random

@dataclass
class InputValues:
    input_type: Optional[NumProperties] = field(default_factory=NumProperties)
    
    min_values: Optional[int] = 2
    max_values: Optional[int] = 5
    no_of_values: Optional[int] = None # Overrides min_nums and max_nums if not set to None
    
    ascending: Optional[bool] = False
    descending: Optional[bool] = False # Prioritized over ascending
    
    def generate(self):
        if self.max_values < 2:
            raise ValueError("Cannot generate < 2 values")
        self.min_values = max(self.min_values, 2)
        no_of_values = self.no_of_values if self.no_of_values is not None else random.randint(self.min_values, self.max_values)

        values = [
            self.input_type.generate()
            for _ in range(no_of_values)
        ]
        if self.descending: values.sort(reverse=True)
        elif self.ascending: values.sort()
        return values