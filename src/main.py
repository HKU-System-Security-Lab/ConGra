import os 
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import numpy as np 
import argparse
from utils import create_llm, load_conflict_and_answer
from langchain_core.messages import SystemMessage, HumanMessage
from prompt import * #SYSTEM_PROMPT, CONFLICT_RESOLUTION_PROMPT, CONFLICT_RESOLUTION_WO_CONTEXT_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser 
import re 
import json
import multiprocessing
import time 
from transformers import AutoTokenizer
import sys 
import traceback
from metrics import metric_edit_distance, metric_winnowing
def get_args():
    parser = argparse.ArgumentParser(description='')
    # LLM Parameter 
    parser.add_argument('--llm_model', default='deepseek-code',type=str, help='')
    parser.add_argument('--temperature', type=float, default=0.7, help='')
    parser.add_argument('--api_key', type=str, help='', default='')
    parser.add_argument('--language', choices=['python','java','cpp','c'],default='python')
    parser.add_argument('--type',choices=['text','text_func','text_sytx','text_sytx_func',
                                          'func','sytx','sytx_func'
                                          ], default='text',help='conflict types')
    parser.add_argument('--context_line', type=int, default=5)
    parser.add_argument('--worker', type=int, default=1)
    args = parser.parse_args()
    return args 

def extract_code_block(text):
    pattern = r'```(.*?)\n([\s\S]*?)```'
    match = re.search(pattern, text)
    if match:
        return match.group(2)
    else:
        return ""
    


def solve_a_conflict(llm_config,resolution_root, data_root, source_path, hash_idx, conflict_idx, args):
    try:
        if os.path.exists(os.path.join(resolution_root,hash_idx+'-{}'.format(conflict_idx))):
            return 
        llm_model, model_token = create_llm(llm_config)
        resolution_dict = {}
        cl = args.context_line
        if model_token<=8*1024: 
            max_input_tokens = model_token - 2*1024 # for output 
        else:
            max_input_tokens = model_token - 5*1024 # for output 
        processable_flag = True
        while cl>=0:
            conflict_context_text, conflict_text, resolved_text = load_conflict_and_answer(source_path, os.path.join(data_root,hash_idx),conflict_idx,cl)
            tokenizer = AutoTokenizer.from_pretrained('./',trust_remote_code=True, TOKENIZERS_PARALLELISM=False)
            if cl == args.context_line: 
                tokens = tokenizer.tokenize(conflict_text)
                if len(tokens)>max_input_tokens:
                    processable_flag = False 
                    break
            tokens = tokenizer.tokenize(conflict_context_text+conflict_text)
            if len(tokens)>max_input_tokens: 
                cl = cl-1
                continue
            else: 
                break
        if processable_flag:
            if cl<0:
                user_prompt = CONFLICT_RESOLUTION_WO_CONTEXT_PROMPT
            else:
                user_prompt = CONFLICT_RESOLUTION_PROMPT
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),    
                ("user", user_prompt)
            ])

            chain = prompt | llm_model # | output_parser
            print("Begin...")
            t1 = time.time()
            response = chain.invoke({
                "language": args.language,
                "conflict_context": conflict_context_text,
                "conflict_text": conflict_text
            })
            try:
                completion_tokens = response.response_metadata['token_usage']['completion_tokens']
                prompt_tokens = response.response_metadata['token_usage']['prompt_tokens']
                total_tokens = response.response_metadata['token_usage']['total_tokens']
            except:
                completion_tokens, prompt_tokens, total_tokens = -1, -1, -1
            response = response.content
            try:
                resolution = extract_code_block(response)
            except:
                resolution = ""
            if resolution is None: 
                resolution = ""
            t2 = time.time()
            fix_time = t2-t1
            resolution_dict['source_hash'] = hash_idx
            resolution_dict['conflict_idx'] = conflict_idx
            resolution_dict['conflict'] = conflict_text
            resolution_dict['conflict_type'] = args.type 
            resolution_dict['fix_time'] = t2-t1
            resolution_dict['context_line'] = cl
            resolution_dict['temperature'] = args.temperature
            resolution_dict['resolution'] = resolution
            resolution_dict['completion_tokens'] = completion_tokens
            resolution_dict['prompt_tokens'] = prompt_tokens
            resolution_dict['total_tokens'] = total_tokens
            resolution_dict['resolved_text'] = resolved_text

        else:
            resolution = ""
            fix_time = 0 
            resolution_dict['source_hash'] = hash_idx
            resolution_dict['conflict_idx'] = conflict_idx
            resolution_dict['conflict'] = conflict_text
            resolution_dict['conflict_type'] = args.type 
            resolution_dict['fix_time'] = fix_time
            resolution_dict['context_line'] = cl
            resolution_dict['temperature'] = args.temperature
            resolution_dict['resolution'] = resolution
            resolution_dict['resolved_text'] = resolved_text
        try:
            winnowing_distance = metric_winnowing(resolution, resolved_text)
        except:
            winnowing_distance = -1             
        try:
            edit_distance = metric_edit_distance(resolution, resolved_text)
        except:
            edit_distance = -1 
        resolution_dict['winnowing'] = winnowing_distance
        resolution_dict['edit_distance'] = edit_distance
        # logger.info("winnowing distance:{}".format(winnowing_distance))
        # logger.info("edit distance:{}".format(edit_distance))
        with open(os.path.join(resolution_root,'resolutions.jsonl'),'a') as f: 
            f.write(json.dumps(resolution_dict) + '\n')
        with open(os.path.join(resolution_root,hash_idx+'-{}'.format(conflict_idx)),'w') as f:
            f.write(resolution)
    except Exception as e:
        print("Error:", str(e), source_path, hash_idx, conflict_idx)
        print("resolution:", resolution)
        print("-"*128)
        print("resolve:", resolved_text, len(resolved_text))
        print("-"*128)

        traceback.print_exc()
        raise SystemExit
def main(args):
    # Load Data 
    data_root = '../data/congra_full_datasets/{}/{}'.format(args.language, (args.type).replace('_','+'))
    resolution_root = '../output/{}/{}/{}'.format(args.language, (args.type).replace('_','+'),'{}_{}'.format(
        args.llm_model, args.temperature))
    os.makedirs(resolution_root,exist_ok=True)
    meta_data_path = os.path.join(data_root,'meta_list.txt')
    meta_data = [] 
    with open(meta_data_path,'r') as f:
        for line in f:
            source_path, hash_idx, conflict_idx = line.strip().split(': ')
            # filter data without groundtruth 
            source_path = os.path.join('../data/raw_datasets/',source_path)
            source_path = source_path.replace('merged_without_base','regions')
            region_path = source_path + '.region'
            if not os.path.exists(region_path):
                continue
            else:
                meta_data.append((source_path, hash_idx, int(conflict_idx)))
    print("The number of samples({}-{}):{}".format(args.language, args.type, len(meta_data)))
    # Model Config 
    api_key = args.api_key if len(args.api_key)>10 else 'EMPTY'
    if 'deepseek' in args.llm_model:
        openai_api_base = 'https://api.deepseek.com/v1'
    elif 'glm-' in args.llm_model:
        openai_api_base = 'https://open.bigmodel.cn/api/paas/v4/'
    elif 'meta-llama/' in args.llm_model:
        openai_api_base = 'http://localhost:1234/v1'
    else: 
        openai_api_base = 'http://localhost:1234/v1'
    llm_config = {
        "model": args.llm_model,
        "openai_api_key": api_key,
        "openai_api_base": openai_api_base,
        "temperature": args.temperature 
    }
    # Create LLM Models 
    # for source_path, hash_idx, conflict_idx in meta_data: 
        # solve_a_conflict(llm_config, resolution_root,data_root, source_path, hash_idx, conflict_idx, args)
    if args.worker==1:
        for source_path, hash_idx, conflict_idx in meta_data: 
            solve_a_conflict(llm_config, resolution_root,data_root, source_path, hash_idx, conflict_idx, args)
    else:
        with multiprocessing.Pool(args.worker) as pool:
            pool.starmap(solve_a_conflict, 
                        [(llm_config, resolution_root, data_root, source_path, hash_idx, conflict_idx, args) 
                        for source_path, hash_idx, conflict_idx in meta_data])

if __name__ == '__main__':
    args = get_args()
    main(args)