from typing import Tuple, Union
from ..bignum import bignum  

class Multiply:
    chunk_size = 500
    
    @staticmethod
    def raw_product(*nums: Tuple[str]) -> bignum:
        """
        Calculate the product of string-based numerical inputs.

        Examples:
            >>> Multiply.raw_product("009", "10")
            bignum('090')
            >>> Multiply.raw_product("3", "5", "29")
            bignum('435')
            >>> Multiply.raw_product("3", "5")
            bignum('15')
        """

        return bignum(str(eval('*'.join(nums))))
    
    @staticmethod
    def result_and_carry(*nums: Tuple[str]) -> Tuple[bignum, int]:
        """
        Compute the result and carry of multiplying string-based numerical inputs.
        - If the length of the result exceeds the length of the largest number in `nums`, 
        then the part of the result beyond the length of the largest number is considered as the carry.

        Returns:
            Tuple[bignum, int]: A tuple containing the result and carry of the multiplication.

        Examples:
            >>> Multiply.result_and_carry("9", "10")
            (bignum('90'), 0)
            >>> Multiply.result_and_carry("03", "005", "29")
            (bignum('435'), 0)
            >>> Multiply.result_and_carry("9", "8")
            (bignum('72'), 0)
            >>> Multiply.result_and_carry("999", "1")
            (bignum('999'), 0)
        """
        nums = [str(num) for num in nums]
        result = Multiply.raw_product(*nums)
        max_res_len = len(max(nums, key=len))
        if len(result) > max_res_len: 
            return result[1:], int(result[0])
        return result, 0
    
    def multiply_two_whole_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the product of two whole numbers."""
        if len(num1) <= self.chunk_size and len(num2) <= self.chunk_size:
            return bignum(int(num1) * int(num2))
        
        # Divide the large input into smaller chunks
        num1, num2 = sorted([num1, num2], key=len, reverse=True)
        num1_chunks = list(num1.chunk_whole(Multiply.chunk_size, reverse=True))
        num2_chunks = list(num2.chunk_whole(Multiply.chunk_size, reverse=True))

        result = bignum('0')

        # Loop through the chunks and add the result to the result list
        for idx, chunk1 in enumerate(num1_chunks):
            for _ in range(idx):
                chunk1 += '0'  # Shift left based on the position in the original number
            for idx2, chunk2 in enumerate(num2_chunks):
                for _ in range(idx2):
                    chunk2 += '0'  # Shift left based on the position in the original number
                res, _ = Multiply.result_and_carry(chunk1, chunk2)
                result = result + res
        
        return result
    
    def multiply_two_positive_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the product of two positive numbers."""
        
        # If both are whole numbers, call the function for multiplying whole numbers directly
        if not num1.has_decimal() and not num2.has_decimal(include_trailing_zeros=True):
            return self.multiply_two_whole_nums(num1, num2).filtered()
        
        # Else, convert the decimals into whole numbers by removing the decimal point.
        num1_whole, num2_whole = num1.get_whole(), num2.get_whole()
        num1_dec, num2_dec = bignum.equalize_decimals(num1, num2, decimal_only=True)
        
        num1_combined = bignum(f"{num1_whole}{num1_dec}")
        num2_combined = bignum(f"{num2_whole}{num2_dec}")
        decimal_len = len(num1_dec)
        
        # Compute the result and add the decimal point back.
        return self.multiply_two_whole_nums(num1_combined, num2_combined).shift_decimals_left(decimal_len)
    
    def multiply_two_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the product of two numbers."""
        
        # If any number is negative, switch to negative multiplication. 
        # Else, call the function for multiplying positive numbers.
        num1_positive, num2_positive = num1.is_positive(), num2.is_positive()
        if num1_positive and num2_positive:
            return self.multiply_two_positive_nums(num1, num2)
        if num1_positive:
            # return multiply.neg_multiply(num1, num2.to_positive())
            raise ValueError("Negative numbers are not supported yet.")
        if num2_positive:
            # return multiply.neg_multiply(num2, num1.to_positive())
            raise ValueError("Negative numbers are not supported yet.")
        return bignum(self.multiply_two_positive_nums(num1.to_positive(), num2.to_positive())).negate()
    
    def multiply(self, *args) -> bignum:
        """Calculate the product of the given numbers."""
        if not args: 
            return bignum('1')
        final_result = bignum(args[0])
        for item in args[1:]:
            final_result = self.multiply_two_nums(final_result, bignum(item))
        return final_result

multiply = Multiply().multiply