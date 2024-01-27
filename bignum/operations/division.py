from typing import Tuple, Union
from ..bignum import bignum  

class Divide:
    chunk_size = 500
    
    @staticmethod
    def raw_quotient(dividend: str, divisor: str) -> bignum:
        """
        Compute the quotient of dividing two string-based numerical inputs.

        Examples:
            >>> Divide.raw_quotient("090", "10")
            bignum('09')
            >>> Divide.raw_quotient("435", "29")
            bignum('15')
            >>> Divide.raw_quotient("15", "3")
            bignum('5')
        """
        return bignum(str(eval(dividend) / eval(divisor)))
    
    def divide_two_whole_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the quotient of dividing two whole numbers."""
        if int(num2) == 0:
            raise ValueError("Division by zero")
        if len(num1) <= self.chunk_size and len(num2) <= self.chunk_size:
            return bignum(int(num1) / int(num2))
        
        # Divide the large input into smaller chunks
        num1, num2 = sorted([num1, num2], key=len, reverse=True)
        num1_chunks = list(num1.chunk_whole(Divide.chunk_size, reverse=True))
        num2_chunks = list(num2.chunk_whole(Divide.chunk_size, reverse=True))

        result = bignum('0')

        # Loop through the chunks and add the result to the result list
        for idx, chunk1 in enumerate(num1_chunks):
            for _ in range(idx):
                chunk1 += '0'  # Shift left based on the position in the original number
            chunk_result = '0'
            while chunk1 >= num2:
                chunk1 -= num2
                chunk_result = str(int(chunk_result) + 1)
            result = result + chunk_result
        
        return result
    
    def divide_two_positive_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the quotient of dividing two positive numbers."""
        
        # If both are whole numbers, call the function for dividing whole numbers directly
        if not num1.has_decimal() and not num2.has_decimal(include_trailing_zeros=True):
            return self.divide_two_whole_nums(num1, num2).filtered()
        
        # Else, convert the decimals into whole numbers by removing the decimal point.
        num1_whole, num2_whole = num1.get_whole(), num2.get_whole()
        num1_dec, num2_dec = bignum.equalize_decimals(num1, num2, decimal_only=True)
        
        num1_combined = bignum(f"{num1_whole}{num1_dec}")
        num2_combined = bignum(f"{num2_whole}{num2_dec}")
        decimal_len = len(num1_dec)
        
        # Compute the result and add the decimal point back.
        return self.divide_two_whole_nums(num1_combined, num2_combined).shift_decimals_left(decimal_len)
    
    def divide_two_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the quotient of dividing two numbers."""
        
        # If any number is negative, switch to negative division. 
        # Else, call the function for dividing positive numbers.
        num1_positive, num2_positive = num1.is_positive(), num2.is_positive()
        if num1_positive and num2_positive:
            return self.divide_two_positive_nums(num1, num2)
        if num1_positive:
            # return divide.neg_divide(num1, num2.to_positive())
            raise ValueError("Negative numbers are not supported yet.")
        if num2_positive:
            # return divide.neg_divide(num2, num1.to_positive())
            raise ValueError("Negative numbers are not supported yet.")
        return bignum(self.divide_two_positive_nums(num1.to_positive(), num2.to_positive())).negate()
    
    def divide(self, dividend: Union[str, bignum], divisor: Union[str, bignum]) -> bignum:
        """Calculate the quotient of dividing the dividend by the divisor."""
        dividend, divisor = bignum(dividend), bignum(divisor)
        if divisor == 0:
            raise ValueError("Division by zero")
        
        if not dividend:
            return bignum('0')
        
        if divisor == 1:
            return dividend
        
        return self.divide_two_nums(dividend, divisor)

divide = Divide().divide

