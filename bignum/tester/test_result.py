from dataclasses import dataclass, field
from decimal import Decimal

from bignum.bignum import bignum

@dataclass
class TestResult:
    operation: str
    input_values: list[int | str | bignum]
    
    algorithm_result: bignum
    algorithm_time: Decimal|float
    
    builtin_result: int | float | Decimal
    # builtin_result_type: type
    builtin_time: Decimal|float
    
    matching: bool
    
    @property
    def time_difference(self):
        if self.algorithm_time > self.builtin_time:
            return [round(self.algorithm_time/self.builtin_time, 2), "Slower"]
        elif self.builtin_time > self.algorithm_time:
            return [round(self.builtin_time/self.algorithm_time, 2), "Faster"] 
        return [1, "Equal"]
    
    def as_str(self, 
                   include_input_values=True,
                   include_results=True,
                   include_matching=True,
                   include_algorithm_time=False, 
                   include_builtin_time=False, 
                   include_speed_difference=True):
        result = []
        if include_input_values: result.append(f"{f' {self.operation} '.join((str(val) for val in self.input_values))} = {self.algorithm_result}")
        if include_results: 
            if not include_input_values: result.append(self.algorithm_result)
            result.append(self.builtin_result)
        if include_matching: result.append(self.matching)
        if include_algorithm_time: result.append(f"{bignum(self.algorithm_time).truncate_decimal_to_significant_digit(4)}s")
        if include_builtin_time: result.append(f"{bignum(self.builtin_time).truncate_decimal_to_significant_digit(4)}s")
        if include_speed_difference:
            if self.builtin_time > self.algorithm_time: result.append(f"{round(float(self.builtin_time/self.algorithm_time), 2)}x faster")
            else: result.append(f"{round(float(self.algorithm_time/self.builtin_time), 2)}x slower")
        result = " | ".join((str(item) for item in result))
        return result
