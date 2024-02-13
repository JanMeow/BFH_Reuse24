from collections import Counter
from itertools import chain

def find_combinations(nums, targets):
    def knapsack(items, capacity):
        dp = [0] * (capacity + 1) #[0,0,0,...,0,0,0] it has capacity number of 0
        item_included = [[] for _ in range(capacity + 1)] #[[],[],[],...,[],[],[]] it has capacity number of []

        print("dp: ", dp)
        print("itemList: ", item_included)
        
        for item in items:
            print("item is: " + str(item))
            
            for i in range(capacity, item - 1, -1):
                if dp[i - item] + item > dp[i]:
                    dp[i] = dp[i - item] + item 
                    item_included[i] = item_included[i - item] + [item]
            
            print("dp: ", dp)
            print("itemList: ", item_included)

        return item_included[capacity]

    def find_closest_number(remaining_nums, target):
        # Find the smallest number in remaining_nums that makes the sum >= target
        for num in sorted(remaining_nums):
            if num + sum(remaining_nums) >= target:
                return num
        return None

    all_combinations = []
    for target in targets:
        combination = knapsack(nums, target)
        combination_sum = sum(combination)

        if combination_sum < target:
            remaining_nums = Counter(nums) - Counter(combination)
            additional_num = find_closest_number(list(remaining_nums.elements()), target - combination_sum)
            if additional_num is not None:
                combination.append(additional_num)

        remaining_nums = Counter(nums) - Counter(combination)
        nums = list(remaining_nums.elements())
        random.shuffle(nums)


        all_combinations.append(combination)

    return all_combinations



#==========================================================================================
import random

def replicate_and_shuffle(input_list, quantity):
    # Replicate each element by the specified quantity
    replicated_list = [element for element in input_list for _ in range(quantity)]
    
    # Shuffle the list randomly
    random.shuffle(replicated_list)
    
    return replicated_list

# Example usage
input_list = [4,6,3,5,7,9,4,6,4,7,5,8,4,6,7]

# Example usage
extended_nums = input_list

targets = [17]


combinations = find_combinations(extended_nums, targets)
for target, combination in zip(targets, combinations):
    print("Target "+ str(target) + " constructed by: "+ str(combination) + " ,the sum is: " + str(sum(combination)))
