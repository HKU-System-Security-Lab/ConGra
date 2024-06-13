from models import * 
from copy import deepcopy
import os 
models_tokens = {
    "openai": {
        "gpt-3.5-turbo-0125": 16385,
        "gpt-3.5": 4096,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-1106": 16385,
        "gpt-3.5-turbo-instruct": 4096,
        "gpt-4-0125-preview": 128000,
        "gpt-4-turbo-preview": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-2024-04-09": 128000,
        "gpt-4-1106-preview": 128000,
        "gpt-4-vision-preview": 128000,
        "gpt-4": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0613": 32768,
        "gpt-4o": 128000,
    },
    "azure": {
        "gpt-3.5-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0613": 32768,
        "gpt-4o": 128000,
    },
    "gemini": {
        "gemini-pro": 128000,
        "gemini-1.5-flash-latest":128000,
        "gemini-1.5-pro-latest":128000,
        "models/embedding-001": 2048
    },
    "ollama": {
        "command-r": 12800,
        "command-r-plus": 12800,
        "codellama": 16000,
        "dbrx": 32768,
        "dbrx:instruct": 32768,
        "deepseek-coder:33b": 16000,
        "dolphin-mixtral": 32000,
        "llama2": 4096,
        "llama3": 8192,
        "llama3:70b-instruct": 8192,
        "llava": 4096,
        "llava:34b": 4096,
        "llava_next": 4096,
        "mistral": 8192,
        "falcon": 2048,
        "codellama": 16000,
        "dolphin-mixtral": 32000,
        "mistral-openorca": 32000,
        "stablelm-zephyr": 8192,
        "command-r-plus": 12800,
        "command-r": 12800,
        "mistral:7b-instruct": 32768,
        "mistral-openorca": 32000,
        "mixtral:8x22b-instruct": 65536,
        "nous-hermes2:34b": 4096,
        "orca-mini": 2048,
        "phi3:3.8b": 12800,
        "phi3:14b": 12800,
        "qwen:0.5b": 32000,
        "qwen:1.8b": 32000,
        "qwen:4b": 32000,
        "qwen:14b": 32000,
        "qwen:32b": 32000,
        "qwen:72b": 32000,
        "qwen:110b": 32000,
        "stablelm-zephyr": 8192,
        "wizardlm2:8x22b": 65536,
        # embedding models
        "nomic-embed-text": 8192,
        "snowflake-arctic-embed:335m": 8192,
        "snowflake-arctic-embed:l": 8192,
        "mxbai-embed-large": 512,
    },
    "oneapi": {
        "qwen-turbo": 16380
    },
    "groq": {
        "llama3-8b-8192": 8192,
        "llama3-70b-8192": 8192,
        "mixtral-8x7b-32768": 32768,
        "gemma-7b-it": 8192,
    },
    "claude": {
        "claude_instant": 100000,
        "claude2": 9000,
        "claude2.1": 200000,
        "claude3": 200000
    },
    "bedrock": {
        "anthropic.claude-3-haiku-20240307-v1:0": 200000,
        "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
        "anthropic.claude-3-opus-20240229-v1:0": 200000,
        "anthropic.claude-v2:1": 200000,
        "anthropic.claude-v2": 100000,
        "anthropic.claude-instant-v1": 100000,
        "meta.llama3-8b-instruct-v1:0": 8192,
        "meta.llama3-70b-instruct-v1:0": 8192,
        "meta.llama2-13b-chat-v1": 4096,
        "meta.llama2-70b-chat-v1": 4096,
        "mistral.mistral-7b-instruct-v0:2": 32768,
        "mistral.mixtral-8x7b-instruct-v0:1": 32768,
        "mistral.mistral-large-2402-v1:0": 32768,
		# Embedding models
		"amazon.titan-embed-text-v1": 8000,
		"amazon.titan-embed-text-v2:0": 8000,
        "cohere.embed-english-v3": 512,
        "cohere.embed-multilingual-v3": 512
    },
    "mistral": {
        "mistralai/Mistral-7B-Instruct-v0.2": 32000
    },
    "hugging_face": {
        "meta-llama/Meta-Llama-3-8B": 8192,
        "meta-llama/Meta-Llama-3-8B-Instruct": 8192,
        "meta-llama/Meta-Llama-3-70B": 8192,
        "meta-llama/Meta-Llama-3-70B-Instruct": 8192,
        "meta-llama/CodeLlama-34b-Instruct-hf": 16384,
        "meta-llama/CodeLlama-7b-Instruct-hf": 16384,
        "google/gemma-2b": 8192,
        "google/gemma-2b-it": 8192,
        "google/gemma-7b": 8192,
        "google/gemma-7b-it": 8192,
        "microsoft/phi-2": 2048,
        "openai-community/gpt2": 1024,
        "openai-community/gpt2-medium": 1024,
        "openai-community/gpt2-large": 1024,
        "facebook/opt-125m": 2048,
        "petals-team/StableBeluga2": 8192,
        "distilbert/distilgpt2": 1024,
        "mistralai/Mistral-7B-Instruct-v0.2": 32768,
        "gradientai/Llama-3-8B-Instruct-Gradient-1048k": 1040200,
        "NousResearch/Hermes-2-Pro-Llama-3-8B": 8192,
        "NousResearch/Hermes-2-Pro-Llama-3-8B-GGUF": 8192,
        "nvidia/Llama3-ChatQA-1.5-8B": 8192,
        "microsoft/Phi-3-mini-4k-instruct": 4192,
        "microsoft/Phi-3-mini-128k-instruct": 131072,
        "mlabonne/Meta-Llama-3-120B-Instruct": 8192,
        "cognitivecomputations/dolphin-2.9-llama3-8b": 8192,
        "cognitivecomputations/dolphin-2.9-llama3-8b-gguf": 8192,
        "cognitivecomputations/dolphin-2.8-mistral-7b-v02": 32768,
        "cognitivecomputations/dolphin-2.5-mixtral-8x7b": 32768,
        "TheBloke/dolphin-2.7-mixtral-8x7b-GGUF": 32768,
        "deepseek-ai/DeepSeek-V2": 131072,
        "deepseek-ai/DeepSeek-V2-Chat": 131072,
        "claude-3-haiku": 200000
    },
    "deepseek": {
        "deepseek-chat": 32768,
        "deepseek-coder": 16384
    },
    "glm": {
        "glm-4": 128*1024,
        "glm-3-turbo": 128*1024
    }
}

def create_llm(llm_config: dict, chat=False) -> object:
    """
    Create a large language model instance based on the configuration provided.

    Args:
        llm_config (dict): Configuration parameters for the language model.

    Returns:
        object: An instance of the language model client.

    Raises:
        KeyError: If the model is not supported.
    """

    llm_defaults = {"temperature": 0, "streaming": False}
    llm_params = {**llm_defaults, **llm_config}

    # If model instance is passed directly instead of the model details
    if "model_instance" in llm_params:
        if chat:
            model_token = set_model_token(llm_params["model_instance"])
        return llm_params["model_instance"], model_token 

    # Instantiate the language model based on the model name
    if "gpt-" in llm_params["model"]:
        try:
            model_token = models_tokens["openai"][llm_params["model"]]
        except KeyError as exc:
            raise KeyError("Model not supported") from exc
        return OpenAI(llm_params), model_token 
    elif "claude-3-" in llm_params["model"]:
        try:
            model_token = models_tokens["claude"]["claude3"]
        except KeyError:
            print("model not found, using default token size (8192)")
            model_token = 8192
        return Anthropic(llm_params), model_token 
    elif "ollama" in llm_params["model"]:
        llm_params["model"] = llm_params["model"].split("ollama/")[-1]

        # allow user to set model_tokens in config
        try:
            if "model_tokens" in llm_params:
                model_token = llm_params["model_tokens"]
            elif llm_params["model"] in models_tokens["ollama"]:
                try:
                    model_token = models_tokens["ollama"][llm_params["model"]]
                except KeyError as exc:
                    print("model not found, using default token size (8192)")
                    model_token = 8192
            else:
                model_token = 8192
        except AttributeError:
            model_token = 8192

        return Ollama(llm_params), model_token
    elif "deepseek" in llm_params["model"]:
        try:
            model_token = models_tokens["deepseek"][llm_params["model"]]
        except KeyError:
            print("model not found, using default token size (8192)")
            model_token = 8192
        return DeepSeek(llm_params), model_token 
    elif "glm-" in llm_params["model"]:
        try:
            model_token = models_tokens["glm"][llm_params["model"]]
        except KeyError:
            print("model not found, using default token size (8192)")
            model_token = 8192
        return GLM(llm_params), model_token 
    elif "meta-llama/" in llm_params["model"]:
        try:
            model_token = models_tokens["hugging_face"][llm_params["model"]]
        except KeyError:
            print("model not found, using default token size (8192)")
            model_token = 8192
        return LLama(llm_params), model_token 
    else:
        raise ValueError("Model provided by the configuration not supported")

def set_model_token(llm):

    if "Azure" in str(type(llm)):
        try:
            model_token = models_tokens["azure"][llm.model_name]
        except KeyError:
            raise KeyError("Model not supported")

    elif "HuggingFaceEndpoint" in str(type(llm)):
        if "mistral" in llm.repo_id:
            try:
                model_token = models_tokens["mistral"][llm.repo_id]
            except KeyError:
                raise KeyError("Model not supported")
    elif "Google" in str(type(llm)):
        try:
            if "gemini" in llm.model:
                model_token = models_tokens["gemini"][llm.model]
        except KeyError:
            raise KeyError("Model not supported")
    return model_token 
#  This function has been deprecated.
def extract_resolution(conflict_file, resolved_file, k):
    """
    Args:
        conflict_file (str): 
        resolved_file (str): 
        k (int): the k-th conflict. 
    """
    with open(conflict_file, 'r', encoding='utf-8') as file:
        content = file.read()
        start_marker = "<<<<<<< a"
        end_marker = ">>>>>>> b"
        lines = content.split('\n')
        start_index = [] 
        end_index = []
        for index, line in enumerate(lines):
            if start_marker in line: 
                start_index.append(index)
            if end_marker in line: 
                end_index.append(index)
        assert len(start_index)==len(end_index), 'Error'
    with open(resolved_file, 'r', encoding='utf-8') as file: 
        resolved_content = file.read()
        resolved_lines = resolved_content.split('\n')
        # locate the start marker 
        t = start_index[k-1]-1
        while t>=0:
            if len(lines[t])==0:
                t = t-1
            else: 
                before_lines= lines[t]
                break         
        t = end_index[k-1]+1
        while t<=len(lines)-1:
            if len(lines[t])==0:
                t = t+1
            else: 
                after_lines= lines[t]
                break
        for idx, l in enumerate(resolved_lines):
            if l == before_lines:
                resolution = []
                for j in range(idx+1, len(resolved_lines)):
                    if not resolved_lines[j]==after_lines:
                        resolution.append(resolved_lines[j])
                    else: 
                        break 
                for j in range(len(resolution)-1,-1, -1):
                    if len(resolution[j])>=0:
                        resolution = resolution[:j+1]
                        break
    return resolution

def load_conflict_and_answer(source_path, file_path, k, n):
    region_path  = source_path.replace('merged_without_base','regions') + '.region'
    region_list = [] 
    with open(region_path,'r') as f:
        # file_content = f.readlines()
        for l in f:
            if '#' in l: 
                continue
            line = l.strip()
            region_list.append(eval(line))
    k_region = region_list[k-1]
    with open(file_path, 'r', encoding='utf-8', errors="ignore") as file:
        content = file.read()
    lines = content.split('\n')
    start_index, end_index = k_region[0]-1, k_region[1]
    conflict_text = '\n'.join(lines[start_index:end_index])
    conflict_context_text = '\n'.join(lines[max(0,start_index-n):end_index+n])
    
    with open(source_path.replace('regions','resolved'), 'r', encoding='utf-8', errors="ignore") as file:
        content = file.read()
    lines = content.split('\n')
    start_index, end_index = k_region[2]-1, k_region[3]
    resolved_text = '\n'.join(lines[max(0,start_index):end_index])
    return conflict_context_text, conflict_text, resolved_text