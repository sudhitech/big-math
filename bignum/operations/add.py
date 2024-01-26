from typing import Tuple, Union
import sys, os

from ..bignum import bignum

class Add:
    chunk_size = 500
    
    @staticmethod
    def raw_sum(*nums: Tuple[str]) -> bignum:
        """
        Compute the sum of string-based numerical inputs, preserving leading zeros.

        Examples:
            >>> Add.raw_sum("009", "10")
            bignum('019')
            >>> Add.raw_sum("03", "005", "29")
            bignum('037')
            >>> Add.raw_sum("3", "5")
            bignum('8')
        """
        min_res_len = len(max(nums, key=len))
        return bignum(sum(int(num) for num in nums)).rjust(min_res_len, '0')   
        
    @staticmethod
    def result_and_carry(*nums: Tuple[str]) -> Tuple[bignum, int]:
        """
        Compute the result and carry of adding string-based numerical inputs.
        - If the length of the result exceeds the length of the largest number in `nums`, 
        then the part of the result beyond the length of the largest number is considered as the carry.
        
        Returns:
            Tuple[bignum, int]: A tuple containing the result and carry of the addition.
        
        Examples:
            >>> Add.result_and_carry("009", "10")
            (bignum('019'), 0)
            >>> Add.result_and_carry("03", "005", "29")
            (bignum('037'), 0)
            >>> Add.result_and_carry("9", "8")
            (bignum('7'), 1)
            >>> Add.result_and_carry("999", "1")
            (bignum('000'), 1)
        """
        nums = [str(num) for num in nums]
        result = Add.raw_sum(*nums)
        max_res_len = len(max(nums, key=len))
        if len(result) > max_res_len: 
            return result[1:], int(result[0])
        return result, 0
    
    def add_two_whole_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the sum of two whole numbers."""
        if len(num1) <= self.chunk_size and len(num2) <= self.chunk_size:
            return bignum(int(num1) + int(num2))
        
        # Divide the large input into smaller chunks
        num1, num2 = sorted([num1, num2], key=len, reverse=True)
        num1_chunks = list(num1.chunk_whole(Add.chunk_size, reverse=True))
        num2_chunks = list(num2.chunk_whole(Add.chunk_size, reverse=True))

        result = []
        carry = 0

        # Loop through the chunks and add the result to the result list
        for chunk1, chunk2 in zip(num1_chunks, num2_chunks):
            res, carry = Add.result_and_carry(chunk1, chunk2, carry)
            result.append(res)
        
        # Handle the remaining chunks.
        del num1_chunks[:len(num2_chunks)]
        for idx, item in enumerate(num1_chunks):
            # If there is no carry from the previous operations, 
            # directly append the remaining chunks to the result list
            if not carry:
                result.extend(num1_chunks[idx:])
                break
            # Else, evaluate the carry
            res, carry = Add.result_and_carry(item, carry)
            result.append(res)
        
        if carry:
            result.append(carry)
        
        # Combine the result list to produce an overall result.
        result = bignum("".join(reversed(list(map(str, result)))))
        return result  
    
    def add_two_positive_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the sum of two positive numbers."""
        
        # Filter out leading and trailing zero's to save computation
        num1, num2 = num1.filtered(), num2.filtered()
        
        # If both are whole numbers, call the function for adding whole numbers directly
        if not num1.has_decimal() and not num2.has_decimal(include_trailing_zeros=True):
            return self.add_two_whole_nums(num1, num2).filtered()
        
        # Else, convert the decimals into whole numbers by removing the decimal point.
        num1_whole, num2_whole = num1.get_whole(), num2.get_whole()
        num1_dec, num2_dec = bignum.equalize_decimals(num1, num2, decimal_only=True)
        
        num1_combined = bignum(f"{num1_whole}{num1_dec}")
        num2_combined = bignum(f"{num2_whole}{num2_dec}")
        decimal_len = len(num1_dec)
        
        # Compute the result and add the decimal point back.
        return self.add_two_whole_nums(num1_combined, num2_combined).shift_decimals_left(decimal_len)
    
    def add_two_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the sum of two numbers."""
        
        # If any number is negative, switch to subtraction. 
        # Else, call the function for adding positive numbers.
        num1_positive, num2_positive = num1.is_positive(), num2.is_positive()
        if num1_positive and num2_positive:
            return self.add_two_positive_nums(num1, num2)
        if num1_positive:
            # return sub.sub(num1, num2.to_positive())
            raise ValueError("Negative numbers are not supported yet.")
        if num2_positive:
            # return sub.sub(num2, num1.to_positive())
            raise ValueError("Negative numbers are not supported yet.")
        return bignum(f"-{self.add_two_positive_nums(num1.to_positive(), num2.to_positive())}")
    
    def add(self, *args) -> bignum:
        """Calculate the sum of the given numbers."""
        if not args: 
            return bignum('0')
        final_result = bignum(args[0])
        for item in args[1:]:
            final_result = self.add_two_nums(final_result, bignum(item))
        return final_result

add = Add().add
