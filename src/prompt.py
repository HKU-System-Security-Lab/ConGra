SYSTEM_PROMPT = "You are an expert in code merge conflicts, providing the merged code based on the conflict and its context."

CONFLICT_RESOLUTION_PROMPT = """
Please provide the merged code based on the specified conflict and its context. 
Please provide the merged code following the chain of thought:
1. Understand the cause of the conflict: Examine the conflicting code and its context to understand why the conflict occurred.
2. Decide how to merge: Based on the functionality and logic of the code, determine which changes should be kept or how the changes from both sides can be combined.
3. Provide the merged code, using "```{language}" as the beginning and "```" as the end of the merged code. You only need to output the resolution of the conflict without providing any context.
For example, 
Conflict Context is:
```python
def quick_sort(arr):
    <<<<<<< a
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quick_sort(left) + [pivot] + quick_sort(right)
    =======
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1] :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    >>>>>>> b
    return arr
```
Conflict is:
```python
    <<<<<<< a
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quick_sort(left) + [pivot] + quick_sort(right)
    =======
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1] :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    >>>>>>> b
```
You need to output:
```python
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quick_sort(left) + [pivot] + quick_sort(right)
```
Here is the context related to the conflict:
```{language}
{conflict_context}
```
Here is the conflict that needs to be resolved:
```{language}
{conflict_text}
```
"""



CONFLICT_RESOLUTION_WO_CONTEXT_PROMPT = """
Please provide the merged code based on the specified conflict and its context. 
Please provide the merged code following the chain of thought:

1. Understand the cause of the conflict: Examine the conflicting code to understand why the conflict occurred.
2. Decide how to merge: Based on the functionality and logic of the code, determine which changes should be kept or how the changes from both sides can be combined.
3. Provide the merged code, using "```{language}" as the beginning and "```" as the end of the merged code. You only need to output the resolution of the conflict without providing any context.
For example, 

Conflict is:
```python
    <<<<<<< a
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quick_sort(left) + [pivot] + quick_sort(right)
    =======
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1] :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    >>>>>>> b
```
You need to output:
```python
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quick_sort(left) + [pivot] + quick_sort(right)
```
Here is the conflict that needs to be resolved:
```{language}
{conflict_text}
```
"""
