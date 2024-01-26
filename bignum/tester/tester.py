import random
import os, sys
import time
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional

from .time_task import time_task
from .test_result import TestResult
from .multi_test_result import MultiTestResult
from .input_values import InputValues
from .num_properties import NumProperties
    

class Tester:
    def __init__(self, operation: str, operation_func):
        self.operation_func = operation_func
        self.operation = self.get_operation(operation)
        self.initial_res = self.get_initial_res()
        
    def get_operation(self, operation):
        if operation.lower() in ['+', 'add', 'addition']:
            return '+'
        if operation.lower() in ['-', 'sub', 'subtract', 'subtraction']:
            return '-'
        if operation.lower() in ['*', 'mul', 'multiply', 'multiplication']:
            return '*'
        if operation.lower() in ['/', 'div', 'divide', 'division']:
            return '/'
        
    def get_initial_res(self):
        if self.operation == '+':
            return '0'
        if self.operation == '-':
            return None
        if self.operation == '*':
            return '1'
        if self.operation == '/':
            return None
        
    def decide_types(self, num1, num2):
        num1_decimal = float(num1)%1 != 0
        num2_decimal = float(num2)%1 != 0
        if num1_decimal or num2_decimal:
            return Decimal(str(num1)), Decimal(str(num2))
        return int(num1), int(num2)
    
    def builtin_operation_result_two_values(self, num1, num2):
        num1, num2 = self.decide_types(num1, num2)
        if self.operation == '+':
            return num1 + num2
        if self.operation == '-':
            return num1 - num2
        if self.operation == '*':
            return num1 * num2
        if self.operation == '/':
            return num1 / num2

    def builtin_operation_result(self, *args):
        if len(args) == 2: return self.builtin_operation_result_two_values(args[0], args[1])
        res = self.initial_res
        if self.initial_res is None: res = args[0]
        for item in (args[1:] if self.initial_res is None else args):
            res = self.builtin_operation_result_two_values(res, item)
        return res
    
    def test_normal(self, *args, print_result=True):
        if len(args) < 2:
            raise ValueError("Not enough values. Minimum 2 required")
        
        alg_res, alg_time = time_task(lambda: self.operation_func(*args))
        builtin_res, builtin_time = time_task(lambda: self.builtin_operation_result(*args))
        correct = alg_res == builtin_res
        
        test_result = TestResult(
                                operation=self.operation,
                                input_values=args, 
                                algorithm_result=alg_res,
                                algorithm_time=alg_time,
                                builtin_result=builtin_res,
                                builtin_time=builtin_time,
                                matching=correct
                                )
        if print_result: print(test_result.as_str())
            
        return test_result
    
    def __print_results(self, test_results: MultiTestResult, only_false):
            if not only_false:
                for test in test_results.true_list:
                    print(test.as_str())
                if test_results.correct_results:
                    print(f"Correct Results: {test_results.correct_results}\n")
            for test in test_results.false_list:
                print(test.as_str())
            if test_results.incorrect_results:
                print(f"Incorrect Results: {test_results.incorrect_results}\n")
                
    def __print_stats(self, test_results: MultiTestResult):
        print("Average Built-In Time for 1 Operation: {}s".format(test_results.average_builtin_time))
        print("Total Time Taken by Built-In Calculation: {}s\n".format(test_results.total_builtin_time))
        print("Average Algorithm Time for 1 Operation: {}s (Best: {}x {}) (Worst: {}x {})".format(test_results.average_algorithm_time, test_results.best_time_difference[0], test_results.best_time_difference[1], test_results.worst_time_difference[0], test_results.worst_time_difference[1]))
        print("Total Time Taken by Algorithm: {}s ({}x {})".format(test_results.total_algorithm_time, test_results.time_difference[0], test_results.time_difference[1]))
        print("Total tests: {}".format(test_results.no_of_tests))
        print("Correct results: {}".format(test_results.correct_results))
        print("Incorrect results: {}".format(test_results.incorrect_results))
        print("Accuracy: {}%".format(test_results.accuracy))
    
    def test_random(self, 
                    no_of_tests=50, 
                    only_false=False, 
                    immediate_print=False, 
                    input_values: InputValues = None):

        if not input_values: input_values = InputValues()
        test_results = MultiTestResult()

        for _ in range(no_of_tests):
            res = self.test_normal(*input_values.generate(), print_result=False)
            if immediate_print and (res.matching != only_false):
                print(res.as_str())
            test_results.append_test(res)
            
        if not immediate_print:
            self.__print_results(test_results, only_false)
        self.__print_stats(test_results)
        
    def generate_large_file(self, num1_properties=None, num2_properties=None):
        if num1_properties is None: num1_properties = NumProperties(whole_no_len=100000, decimal=False, negative=False)
        if num2_properties is None: num2_properties = NumProperties(whole_no_len=100000, decimal=False, negative=False)
        with open(f"{os.path.expanduser('~')}\\.large_values.txt", 'w') as f:
            num1 = num1_properties.generate()
            num2 = num2_properties.generate()
            f.write(f"{num1}\n{num2}\n\n\n")
        return num1, num2
    