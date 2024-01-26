from dataclasses import dataclass, field
from .test_result import TestResult
from decimal import Decimal

@dataclass
class MultiTestResult:
    tests: list[TestResult] = field(default_factory=list)
    
    def __post_init__(self):
        self.true_list = []
        self.false_list = []
        self.total_builtin_time = Decimal('0')
        self.total_algorithm_time = Decimal('0')
        self.best_time_difference = [None, None]
        self.worst_time_difference = [None, None]
        
        for test in self.tests:
            self.update_test_results(test)
            
    @property
    def no_of_tests(self):
        return len(self.tests)
    @property
    def correct_results(self):
        return len(self.true_list)
    @property
    def incorrect_results(self):
        return len(self.false_list)
    @property
    def accuracy(self):
        return self.correct_results/self.no_of_tests*100
    @property
    def average_algorithm_time(self):
        return self.total_algorithm_time/self.no_of_tests
    @property
    def average_builtin_time(self):
        return self.total_builtin_time/self.no_of_tests
    @property
    def time_difference(self):
        if self.total_algorithm_time > self.total_builtin_time:
            return [round(self.total_algorithm_time/self.total_builtin_time, 2), "Slower"]
        elif self.total_builtin_time > self.total_algorithm_time:
            return [round(self.total_builtin_time/self.total_algorithm_time, 2), "Faster"] 
        return [1, "Equal"]
            
    def append_test(self, test: TestResult, print_test=False):
        self.tests.append(test)
        self.update_test_results(test)
        if print_test:
            print(test.as_str())
            
    def _update_time_difference(self, test: TestResult):
        time_difference = test.time_difference
        if self.best_time_difference == [None, None]: self.best_time_difference = time_difference 
        if self.worst_time_difference == [None, None]: self.worst_time_difference = time_difference
            
        if self.best_time_difference[1] in ["Slower", "Equal"]:
            if (time_difference[1] == "Faster" and (self.best_time_difference[0] == "Equal" or time_difference[0] < self.best_time_difference[0])) or (time_difference[1] == "Equal") or (time_difference[0] < self.best_time_difference[0]):
                self.best_time_difference = time_difference
        elif time_difference[0] > self.best_time_difference[0]:
            self.best_time_difference = time_difference
            
        if self.worst_time_difference[1] in ["Faster", "Equal"]:
            if (time_difference[1] == "Slower" and (self.worst_time_difference[1] == "Equal" or time_difference[0] < self.worst_time_difference[0])) or (time_difference[1] == "Equal"):
                self.worst_time_difference = time_difference
        elif time_difference[0] > self.worst_time_difference[0]:
            self.worst_time_difference = time_difference
            
    def update_test_results(self, test: TestResult):
        if test.matching:
            self.true_list.append(test)
        else:
            self.false_list.append(test)
        self.total_builtin_time += test.builtin_time
        self.total_algorithm_time += test.algorithm_time
        self._update_time_difference(test)
