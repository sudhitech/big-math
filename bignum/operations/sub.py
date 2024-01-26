from typing import List
from ..bignum import bignum
import sys

# sys.setrecursionlimit(999999999)

class Subtract:
    chunk_size = 500
    
    def raw_diff(self, num1, num2, contains_borrowed_digit=False) -> bignum:
        """
        Calculate the difference between two numbers while preserving leading zeros.
        
        num1 (str): The first number.
        num2 (str): The second number.
        contains_borrowed_digit (bool, optional): Whether a borrowed digit is present in the subtraction process (default: False).
        """
        res_len = max(len(str(num1)), len(str(num2)))
        if contains_borrowed_digit:
            res_len -= 1 # Borrowed digit should should not be considered in the minimum result length
        return bignum(int(num1)-int(num2)).rjust(res_len, '0')
         
    def borrow_from(self, chunks, idx) -> None:
        """Borrow from the chunk at the given index. If there is nothing to give, borrow from the next chunk and give."""
        borrowed = False
        if not int(chunks[idx]):
            self.borrow_for(chunks, idx)
            borrowed = True
        chunks[idx] = self.raw_diff(chunks[idx], 1, borrowed)
        
    def borrow_for(self, chunks, idx) -> None:
        """Borrow 1 from the next chunk for the chunk at the given index."""
        self.borrow_from(chunks, idx+1)
        chunks[idx] = f"1{chunks[idx]}"
        
    def eval_chunk(self, chunks1: List[str], chunks2: List[str], idx) -> bignum:
        """Evaluate the difference between two chunks at a given index."""
        borrowed = False
        if int(chunks1[idx]) < int(chunks2[idx]):
            borrowed = True
            self.borrow_for(chunks1, idx)
        result = self.raw_diff(chunks1[idx], chunks2[idx], borrowed)
        return result
    
    def sub_two_whole_nums(self, num1: bignum, num2: bignum) -> bignum:
        """
        Calculate the difference between two whole numbers.
        
        NOTE: num1 must be >= num2
        """
        if len(num1) <= self.chunk_size and len(num2) <= self.chunk_size:
            return bignum(int(num1) - int(num2))
        num1_chunks = num1.chunk_whole(Subtract.chunk_size, reverse=True)
        num2_chunks = num2.chunk_whole(Subtract.chunk_size, reverse=True)
        
        result = []
        for idx in range(len(num1_chunks)):
            if idx >= len(num2_chunks):
                result.extend(num1_chunks[idx:])
                break
            res = self.eval_chunk(num1_chunks, num2_chunks, idx)
            result.append(res)
            
        result = bignum("".join(reversed(list(map(str, result))))).filtered()
        return result  
    
    def sub_two_positive_nums(self, num1: bignum, num2: bignum) -> bignum:
        """
        Calculate the difference between two positive numbers.
        
        NOTE: num1 must be >= num2
        """
        if not num1.has_decimal() and not num2.has_decimal():
            return self.sub_two_whole_nums(num1, num2)
        num1_whole, num2_whole = num1.get_whole(), num2.get_whole()
        num1_dec, num2_dec = bignum.equalize_decimals(num1, num2, decimal_only=True)
        
        combined_num1 = bignum(f"{num1_whole}{num1_dec}")
        combined_num2 = bignum(f"{num2_whole}{num2_dec}")
        total_decimals = len(num1_dec)
        
        result = self.sub_two_whole_nums(combined_num1, combined_num2).shift_decimals_left(total_decimals)
        return result
    
    def sub_two_nums(self, num1: bignum, num2: bignum) -> bignum:
        """Calculate the difference between two numbers."""
        num1_positive, num2_positive = num1.is_positive(), num2.is_positive()
        if num1_positive and num2_positive:
            if num2 > num1:
                return bignum(f"-{self.sub_two_positive_nums(num2, num1)}")
            return self.sub_two_positive_nums(num1, num2)
        if num2_positive:
            return bignum(f"-{add(num1.to_positive(), num2)}")
        if num1_positive:
            return add(num1, num2.to_positive())
        if num1.is_negative() and num2.is_negative():
            return self.sub_two_nums(num2.to_positive(), num1.to_positive())
    
    def sub(self, *args) -> bignum:
        """Calculate the difference of given numbers."""
        if not args: 
            return bignum('0')
        final_result = bignum(args[0])
        for item in args[1:]:
            final_result = self.sub_two_nums(final_result, bignum(item))
        return final_result

sub = Subtract().sub
from .add import add