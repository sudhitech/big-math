from __future__ import annotations
from typing import Tuple, Union, Iterable
import gmpy2


class bignum:
    __slots__ = {'__val'}
    
    def __init__(self, value: str):
        self.__val = str(value)
        if not bignum.is_num(self.__val):
            raise ValueError("Invalid value. Provide a number.")
        
    def __str__(self) -> str:
        return self.__val
    
    def __repr__(self) -> str:
        return f"bignum('{self.__val}')"
    
    def __bool__(self) -> bool:
        return bool(self.__val)
        
    def __getitem__(self, idx: Union[int, slice]) -> bignum:
        return bignum(self.__val[idx])
    
    def __abs__(self) -> bignum:
        return bignum(self.__val[1:] if self.is_negative() else self.__val)
    
    def __len__(self) -> bignum:
        return len(self.__val)
    
    @staticmethod
    def is_num(val: str, scientific_notation=False) -> bool:
        try:
            gmpy2.mpfr(str(val))
            return bool(scientific_notation) if "e" in val else True
        except ValueError:
            return False
    
    def has_decimal(self, include_trailing_zeros=False) -> bool:
        return bool('.' in self.__val and (True if include_trailing_zeros else self.__val.split('.')[1].rstrip('0')))
    
    def get_decimal(self) -> bignum:
        return bignum(self.__val.split(".")[1] if self.has_decimal() else '0')
    
    def get_whole(self) -> bignum: 
        return bignum(self.__val.split('.')[0] if self.has_decimal(True) else self.__val)
    
    def is_negative(self) -> bool: 
        return self.__val.startswith('-')
    
    def is_positive(self) -> bool: 
        return not self.__val.startswith('-')
    
    def split(self, x: str) -> list[bignum]: 
        return [bignum(item) for item in self.__val.split(x)]
    
    def as_numerical_dtype(self):
        return float(self.__val) if self.has_decimal() else int(self.filtered())
    
    def chunk_whole(self, chunk_size: int, reverse=False) -> Iterable[int]:
        whole = self.get_whole()
        chunk_iterator = range(len(whole), 0, -chunk_size)
        if not reverse:
            chunk_iterator = reversed(chunk_iterator)
        chunks = (int(str(whole[max(i-chunk_size, 0):i])) for i in chunk_iterator)
        return chunks
    
    def chunk_decimal(self, chunk_size: int, reverse=False, filter_before_chunking=False) -> Iterable[int]:
        decimal = self.filter_decimal() if filter_before_chunking else self.get_decimal()
        return decimal.chunk_whole(chunk_size, reverse)
    
    @staticmethod
    def equalize_decimals(num1: bignum, num2: bignum, decimal_only=False) -> Tuple[bignum, bignum]:
        decimal_1 = num1.get_decimal()
        decimal_2 = num2.get_decimal()
        decimal_1 = f"{decimal_1}{'0'*(len(decimal_2)-len(decimal_1))}"
        decimal_2 = f"{decimal_2}{'0'*(len(decimal_1)-len(decimal_2))}"
        if decimal_only:
            tuple(map(bignum, (decimal1, decimal2)))
        res1 = f"{num1.get_whole()}.{decimal_1}"
        res2 = f"{num2.get_whole()}.{decimal_2}"
        return tuple(map(bignum, (res1, res2)))

    def shift_decimals_left(self, places: int, filter_=True) -> bignum:
        if places < 0:
            return self.shift_decimals_right(abs(places), filter_)
        whole = self.get_whole()
        decimal = self.get_decimal() if self.get_decimal().filtered() != '0' else ''
        if places >= len(whole):
            whole = bignum(f"0.{'0'*(places-len(whole))}{whole}{decimal}")
            return whole.filtered() if filter_ else whole
        num_left = whole[:~(places-1)]
        num_right = whole[~(places-1):]
        result = bignum(f"{num_left}.{num_right}{decimal}")
        return result.filtered() if filter_ else result
    
    def shift_decimals_right(self, places, filter_=True) -> bignum:
        places = int(places)
        if places < 0:
            return self.shift_decimals_left(abs(places), filter_)
        whole, decimal = self.get_whole(), self.get_decimal()
        if places > len(decimal):
            decimal += '0'*(places-len(decimal))
        whole = f"{whole}{decimal[:places]}"
        decimal = f"{decimal[places:]}"
        result = bignum(f"{whole}.{decimal}")
        return result.filtered() if filter_ else result
    
    def filter_whole(self) -> bignum: 
        result = bignum((f"-{str(self.get_whole()[1:]).lstrip('0')}" if self.get_whole().is_negative() else str(self.get_whole()).lstrip('0')) or '0')
        if str(result) == '-': result = bignum('0')
        return result
    
    def filter_decimal(self) -> bignum:
        return bignum(str(self.get_decimal()).rstrip('0') or '0')
    
    def filtered(self) -> bignum:
        whole = self.filter_whole()
        decimal = self.filter_decimal()
        result = bignum(f"{whole}.{decimal}" if str(decimal) != '0' else whole)
        return result
    
    def truncate_decimal(self, num_decimals: int) -> bignum:
        if num_decimals <= 0: 
            return self.get_whole()
        if not self.has_decimal(True):
            return bignum(f"{self}.{'0' * num_decimals}")
        result = bignum(f"{self.get_whole()}.{self.get_decimal()[:num_decimals]}{'0'*(num_decimals-len(self.get_decimal()))}")
        return result
    
    
    def __gt__(self, val: bignum) -> bool:
        def gt_positive(num1: bignum, num2: bignum) -> Tuple[bool, str]:
            chunk_size = 500
            
            num1 = num1.filtered()
            num2 = num2.filtered()

            num1_whole = num1.get_whole()
            num2_whole = num2.get_whole()
            if len(num1_whole) != len(num2_whole): 
                return len(num1_whole) > len(num2_whole)
            
            num1_whole_chunks = num1.chunk_whole(chunk_size)
            num2_whole_chunks = num2.chunk_whole(chunk_size)
            for (num1_whole_chunk, num2_whole_chunk) in zip(num1_whole_chunks, num2_whole_chunks):
                if num1_whole_chunk != num2_whole_chunk:
                    return (num1_whole_chunk > num2_whole_chunk, False)
            
            num1, num2 = bignum.equalize_decimals(num1, num2, decimal_only=True)
            num1_decimal_chunks = num1.chunk_decimal(chunk_size)
            num2_decimal_chunks = num1.chunk_decimal(chunk_size)
            for (num1_decimal_chunk, num2_decimal_chunk) in zip(num1_decimal_chunks, num2_decimal_chunks):
                if num1_decimal_chunk != num2_decimal_chunk:
                    return (num1_decimal_chunk > num2_decimal_chunk, False)
            
            return [False, True]
            
        val = bignum(val)
        if self.is_negative() and not val.is_negative(): 
            return False
        if not self.is_negative() and val.is_negative(): 
            return True
        if self.is_negative() and val.is_negative(): 
            gt, eq = gt_positive(abs(self), abs(val))
            return not gt if not eq else False
        return gt_positive(self, val)[0]
    
    
    def __lt__(self, val: bignum) -> bool:
        return bignum(val) > self
    
    def __eq__(self, val: bignum) -> bool:
        return str(self.filtered()) == str(bignum(val).filtered())
    
    def __ge__(self, val: bignum) -> bool:
        return (self > bignum(val) or self == bignum(val))
    
    def __le__(self, val: bignum) -> bool:
        return (self < bignum(val) or self == bignum(val))
    
        
if __name__ == '__main__':
    pass
    