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
        """
        Check if a given value is a valid number.
        
        Args:
            val (str): The value to be checked.
            scientific_notation (bool): Whether scientific notation is allowed (default: False).
        """
        try:
            gmpy2.mpfr(str(val))
            return bool(scientific_notation) if "e" in val else True
        except ValueError:
            return False
    
    def has_decimal(self, include_trailing_zeros=False) -> bool:
        """
        Check if the value has a decimal point.

        Args:
            include_trailing_zeros (bool): Whether to consider trailing zeros after the decimal point (default: False).
        """
        return bool('.' in self.__val and (True if include_trailing_zeros else self.__val.split('.')[1].rstrip('0')))
    
    def get_decimal(self) -> bignum:
        """Get the decimal part of the value."""
        return bignum(self.__val.split(".")[1] if self.has_decimal() else '0')
    
    def get_whole(self) -> bignum:
        """Get the whole part of the value."""
        return bignum(self.__val.split('.')[0] if self.has_decimal(True) else self.__val)
    
    def is_negative(self) -> bool: 
        """Check if the value is negative."""
        return self.__val.startswith('-')
    
    def is_positive(self) -> bool: 
        """Check if the value is positive."""
        return not self.__val.startswith('-')
    
    def split(self, x: str) -> list[bignum]: 
        """
        Split the value into a list of bignum instances based on a delimiter.

        Args:
            x (str): The delimiter to split the value.

        Returns:
            list[bignum]: A list of bignum instances resulting from the split.
        """
        return [bignum(item) for item in self.__val.split(x)]
    
    def as_numerical_dtype(self) -> Union[float, int]:
        """Returns an integer or a float, based on the presence of a decimal part."""
        return float(self.__val) if self.has_decimal() else int(self.filtered())
    
    def chunk_whole(self, chunk_size: int, reverse=False) -> Iterable[int]:
        """
        Split the whole part of the value into smaller chunks of integers.

        Args:
            chunk_size (int): The size of each chunk.
            reverse (bool): Whether to iterate from least significant digit (default: False).

        Returns:
            Iterable[int]: An iterable of integers representing the chunks.
            
        Examples:
            >>> b = bignum("1234567890.123400")
            >>> list(b.chunk_whole(chunk_size=3))
            [1, 234, 567, 890]
            >>> list(b.chunk_whole(chunk_size=3, reverse=True))
            [890, 567, 234, 1]

        """
        whole = self.get_whole()
        chunk_iterator = range(len(whole), 0, -chunk_size)
        if not reverse:
            chunk_iterator = reversed(chunk_iterator)
        chunks = (int(str(whole[max(i-chunk_size, 0):i])) for i in chunk_iterator)
        return chunks
    
    def chunk_decimal(self, chunk_size: int, reverse=False, filter_before_chunking=False) -> Iterable[int]:
        """
        Split the decimal part of the value into smaller chunks of integers.

        Args:
            chunk_size (int): The size of each chunk.
            reverse (bool): Whether to iterate from least significant digit (default: False).

        Returns:
            Iterable[int]: An iterable of integers representing the chunks.
            
        Examples:
            >>> b = bignum("1234567890.123400")
            >>> list(b.chunk_decimal(chunk_size=3))
            [123, 400]
            >>> list(b.chunk_decimal(chunk_size=3, reverse=True))
            [400, 123]
            >>> list(b.chunk_decimal(chunk_size=3, filter_before_chunking=True))
            [1, 234]

        """
        decimal = self.filter_decimal() if filter_before_chunking else self.get_decimal()
        return decimal.chunk_whole(chunk_size, reverse)
    
    @staticmethod
    def equalize_decimals(num1: bignum, num2: bignum, decimal_only=False) -> Tuple[bignum, bignum]:
        """
        Equalize the decimal parts of two bignum instances by adding zero's.

        Args:
            num1 (bignum): The first bignum instance.
            num2 (bignum): The second bignum instance.
            decimal_only (bool): Whether to equalize only the decimal parts (default: False).

        Returns:
            Tuple[bignum, bignum]: A tuple of two bignum instances with equalized decimal parts.
            
        Examples:
            >>> bignum.equalize_decimals("7.120", "5.4")
            (bignum('7.120'), bignum('5.400'))
            >>> bignum.equalize_decimals("7.120", "5.4", decimal_only=True)
            (bignum('120'), bignum('400'))
        """
        num1, num2 = map(bignum, (num1, num2))
        decimal_1 = num1.get_decimal()
        decimal_2 = num2.get_decimal()
        decimal_1 = f"{decimal_1}{'0'*(len(decimal_2)-len(decimal_1))}"
        decimal_2 = f"{decimal_2}{'0'*(len(decimal_1)-len(decimal_2))}"
        if decimal_only:
            return tuple(map(bignum, (decimal_1, decimal_2)))
        res1 = f"{num1.get_whole()}.{decimal_1}"
        res2 = f"{num2.get_whole()}.{decimal_2}"
        return tuple(map(bignum, (res1, res2)))

    def shift_decimals_left(self, places: int, filter_=False) -> bignum:
        """
        Shift the decimal point of the value to the left by a specified number of places.

        Args:
            places (int): The number of places to shift the decimal point.
            filter_ (bool): Whether to filter the resulting value (default: True).

        Returns:
            bignum: The value with the decimal point shifted to the left.
            
        Examples:
        >>> b = bignum("123450010")
        >>> b.shift_decimals_left(4)
        bignum('12345.0010')
        >>> b.shift_decimals_left(4, filter_=True)
        bignum('12345.001')
        >>> b.shift_decimals_left(10)
        bignum('0.0123450010')
        """
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
    
    def shift_decimals_right(self, places, filter_=False) -> bignum:
        """
        Shift the decimal point of the value to the right by a specified number of places.

        Args:
            places (int): The number of places to shift the decimal point.
            filter_ (bool): Whether to filter the resulting value (default: True).

        Returns:
            bignum: The value with the decimal point shifted to the right.
            
        Examples:
        >>> b = bignum("12.3450")
        >>> b.shift_decimals_right(2)
        bignum('1234.50')
        >>> b.shift_decimals_right(2, filter_=True)
        bignum('1234.5')
        >>> b.shift_decimals_right(6)
        bignum('12345000')
        """
        places = int(places)
        if places < 0:
            return self.shift_decimals_left(abs(places), filter_)
        whole, decimal = self.get_whole(), self.get_decimal()
        if places > len(decimal):
            decimal = str(decimal) + '0'*(places-len(decimal))
        whole = f"{whole}{decimal[:places]}"
        decimal = f"{decimal[places:]}"
        result = bignum(f"{whole}.{decimal}" if decimal else whole)
        return result.filtered() if filter_ else result
    
    def filter_whole(self) -> bignum:
        """
        Filter the whole part of the value by removing leading zeros and applying the appropriate sign.

        Returns:
            bignum: The filtered whole part of the value.
            
        Examples:
            >>> bignum("000120.3450").filter_whole()
            bignum('120')
            >>> bignum("-00192").filter_whole()
            bignum('-192')
        """
        result = bignum((f"-{str(self.get_whole()[1:]).lstrip('0')}" if self.get_whole().is_negative() else str(self.get_whole()).lstrip('0')) or '0')
        if str(result) == '-': result = bignum('0')
        return result
    
    def filter_decimal(self) -> bignum:
        """
        Filter the decimal part of the value by removing trailing zeros.

        Returns:
            bignum: The filtered decimal part of the value.
        
        Examples:
            >>> bignum("2.01900").filter_decimal()
            bignum('019')
        """
        return bignum(str(self.get_decimal()).rstrip('0') or '0')
    
    def filtered(self) -> bignum:
        """
        Filter the value by removing leading zeros in the whole part and trailing zeros in the decimal part.
        
        Examples:
            >>> bignum("-0020.01900").filtered()
            bignum('-20.019')
        """
        whole = self.filter_whole()
        decimal = self.filter_decimal()
        result = bignum(f"{whole}.{decimal}" if str(decimal) != '0' else whole)
        return result
    
    def truncate_decimal(self, num_decimals: int) -> bignum:
        """
        Truncate the decimal part to the specified number of decimal places.
        
        Args:
            num_decimals (int): The number of decimals to keep.
            
        Examples:
            >>> b = bignum('123.456')
            >>> b.truncate_decimal(2)
            bignum('123.45')
            >>> b.truncate_decimal(5)
            bignum('123.45600')
        """
        if num_decimals <= 0: 
            return self.get_whole()
        if not self.has_decimal(True):
            return bignum(f"{self}.{'0' * num_decimals}")
        result = bignum(f"{self.get_whole()}.{self.get_decimal()[:num_decimals]}{'0'*(num_decimals-len(self.get_decimal()))}")
        return result
    
    
    def __gt__(self, val: bignum) -> bool:
        """Check if the value is greater than another value"""
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
        """Check if a value is less than another value."""
        return bignum(val) > self
    
    def __eq__(self, val: bignum) -> bool:
        """Check if a value is equal to another value."""
        return str(self.filtered()) == str(bignum(val).filtered())
    
    def __ge__(self, val: bignum) -> bool:
        """Check if a value is greater than or equal to another value."""
        return (self > bignum(val) or self == bignum(val))
    
    def __le__(self, val: bignum) -> bool:
        """Check if a value is less than or equal to another value."""
        return (self < bignum(val) or self == bignum(val))
    
        
if __name__ == '__main__':
    b = bignum("-0020.01900")
    print(b.filtered())