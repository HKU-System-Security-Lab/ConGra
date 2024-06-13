import torch
import os
import re
import sys
from transformers import AutoTokenizer, AutoModel
from hashlib import sha1
from typing import Union, List


def get_embeddings(model, tokenizer, code: Union[str, List[str]]) -> torch.Tensor:
    if isinstance(code, str):
        code = [code]

    inputs = tokenizer(code, return_tensors="pt", padding=True, truncation=True).to('cuda:0')
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :]

def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.cosine_similarity(a, b)

def compute_code_similarity(tokenizer,model,code1: Union[str, List[str]], code2: Union[str, List[str]],
                            ) -> torch.Tensor: 
    embeddings1 = get_embeddings(model, tokenizer, code1)
    embeddings2 = get_embeddings(model, tokenizer, code2)
    return cosine_similarity(embeddings1, embeddings2)


def get_file_content(file_path: str) -> str:
    
    with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
        ret = f.read()
    return ret

def remove_invisible_characters(input_str):
    pattern = r'[\s\x00-\x1f\x7f-\x9f]+'
    
    cleaned_str = re.sub(pattern, '', input_str)
    return cleaned_str

def get_language_by_suffix(file: str):
    if file.endswith(".py"):
        return "python"
    elif file.endswith(".java"):
        return "java"
    elif file.endswith(".c") or file.endswith(".h"):
        return "c"
    else:
        return "cpp"

def metric_edit_distance(gen_str: str, standard_str: str) -> float:
    gen_str = remove_invisible_characters(gen_str)
    standard_str = remove_invisible_characters(standard_str)
    
    if len(gen_str) == 0 or len(standard_str) == 0:
        return 0.
    
    mark = []
    for i in range(len(gen_str)):
        mark.append([0 for j in range(len(standard_str))])
    for i in range(len(gen_str)):
        mark[i][0] = i
    for j in range(len(standard_str)):
        mark[0][j] = j
    for i in range(1, len(gen_str)):
        for j in range(1, len(standard_str)):
            if gen_str[i] == standard_str[j]:
                mark[i][j] = mark[i - 1][j - 1]
            else:
                mark[i][j] = min(mark[i - 1][j], mark[i][j - 1], mark[i - 1][j - 1]) + 1
                
    min_distance = mark[len(gen_str) - 1][len(standard_str) - 1]
    return 1.0 - min_distance / max(len(gen_str), len(standard_str)) 

def metric_winnowing(gen_str: str, standard_str: str) -> float:
    gen_str = remove_invisible_characters(gen_str)
    standard_str = remove_invisible_characters(standard_str)
    if len(gen_str) == 0 and len(standard_str) == 0:
        return 0
    elif len(gen_str) == 0 or len(standard_str) == 0:
        return 1
    k_size = 5
    win_size = 4
    
    def hash_fun(text):
        hs = sha1(text.encode("utf-8"))
        hs = hs.hexdigest()[-4:]
        hs = int(hs, 16)
        return hs


    def kgrams(text, n):
        text = list(text)
        return zip(*[text[i:] for i in range(n)])


    def do_hashing(kgrams):
        hashlist = []
        for i,kg in enumerate(list(kgrams)):
            ngram_text = "".join(kg)
            hashvalue = hash_fun(ngram_text)
            hashlist.append((hashvalue, i))
        return hashlist


    def sl_window(hashes, n):
        return zip(*[hashes[i:] for i in range(n)])


    def get_min(windows):
        result = []
        prev_min = ()
        for w in windows:
            min_h = min(w, key=lambda x: (x[0], -x[1])) 

            if min_h != prev_min:
                result.append(min_h)
            prev_min = min_h
        return result

    def winnowing(text, size_k, window_size):
        hashes = (do_hashing(kgrams(text,size_k)))
        return set(get_min(sl_window(hashes, window_size)))


    def intersection(lst1, lst2): 
        temp = set(lst2) 
        lst3 = [value for value in lst1 if value in temp] 
        return len(lst3) 

    w1 = winnowing(gen_str, k_size, win_size)
    w2 = winnowing(standard_str, k_size, win_size)
    
    hash_list_a = [x[0] for x in w1]
    hash_list_b = [x[0] for x in w2]

    intersect = intersection(hash_list_a, hash_list_b) + intersection(hash_list_b, hash_list_a)
    union = len(hash_list_a) + len(hash_list_b)
    return (intersect / union)


if __name__ == "__main__":
    code1 = "def add(a, b):\n    return a + b"
    code2 = "def sum(a, b):\n    return a + b"
    code3 = "def subtract(a, b):\n    return a - b"

    similarity1 = compute_code_similarity(code1, code2)
    similarity2 = compute_code_similarity(code1, code3)

    print(f"Similarity between code1 and code2: {similarity1.item()}")
    print(f"Similarity between code1 and code3: {similarity2.item()}")