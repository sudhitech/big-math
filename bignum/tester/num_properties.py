from dataclasses import dataclass
from typing import Optional
import random
import os, sys

from ..bignum import bignum

@dataclass
class NumProperties:
    min_whole_no_len: Optional[int] = 1
    max_whole_no_len: Optional[int] = 10
    whole_no_len: Optional[int] = None # Use a specified length. Overrides min_whole_len and max_whole_len if not set to None. 
    
    # True=Yes, False=No, None=Random
    decimal: Optional[bool] = None
    negative: Optional[bool] = None
    
    min_decimal_len: Optional[int] = 1
    max_decimal_len: Optional[int] = 10
    decimal_len: Optional[int] = None # Use a specified length. Overrides min_whole_len and max_whole_len if not set to None.
    
    # Options for large number generation
    chunk_size: Optional[int] = 10000
    max_chunk_variety: Optional[int] = 20
    repeat_whole: Optional[int|str|bignum] = None # Repeats the given value
    repeat_decimal: Optional[int|str|bignum] = None
    
    def _validate_inputs(self):
        if (self.whole_no_len is not None and self.whole_no_len <= 0) or (self.max_whole_no_len <= 0): raise ValueError("Length of whole number cannot be < 1")
        if (self.decimal_len is not None and self.decimal_len <= 0) or (self.max_decimal_len <= 0): self.decimal = False
        self.min_whole_no_len = max(self.min_whole_no_len, 1)
        self.min_decimal_len = max(self.min_decimal_len, 1)
        
    def _generate_whole(self):
        whole_len = self.whole_no_len if self.whole_no_len is not None else random.randint(self.min_whole_no_len, self.max_whole_no_len)
        if self.repeat_whole is not None: return (str(self.repeat_whole)*((whole_len//len(str(self.repeat_whole)))+1))[:whole_len]
        if whole_len == 1:
            return random.randint(0, 9)
        chunk_size = min(self.chunk_size, whole_len)
        whole_chunks = [str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(chunk_size - 1)) for _ in range(min(whole_len // chunk_size + 1, self.max_chunk_variety))]
        return ''.join(random.choices(whole_chunks, k=(whole_len + chunk_size - 1) // chunk_size))[:whole_len]
        
    def _generate_decimal(self):
        if (self.decimal is True) or (self.decimal is None and random.choice([True, False]) is True):
            decimal_len = self.decimal_len if self.decimal_len is not None else random.randint(self.min_decimal_len, self.max_decimal_len)
            if self.repeat_decimal is not None: 
                return f'.{(str(self.repeat_decimal) * (decimal_len // len(str(self.repeat_decimal)) + 1))[:decimal_len]}'
            chunk_size = min(self.chunk_size, decimal_len)
            decimal_chunks = [''.join(str(random.randint(0, 9)) for _ in range(chunk_size-1)) + str(random.randint(1, 9)) for _ in range(min(decimal_len//self.chunk_size+1, self.max_chunk_variety))]
            decimal = ''.join(random.choices(decimal_chunks, k=(decimal_len + chunk_size - 1) // chunk_size))[:decimal_len]
            return f'.{decimal}'
        return ''
    
    def _generate_negative(self):
        return '-' if \
            (self.negative is True) or \
                (self.negative is None and random.choice([True, False]) is True) \
                    else ''
    
    def generate(self):
        self._validate_inputs()
        whole = self._generate_whole()
        decimal = self._generate_decimal()
        negative = self._generate_negative()
        return bignum(f"{negative}{whole}{decimal}").filtered()
