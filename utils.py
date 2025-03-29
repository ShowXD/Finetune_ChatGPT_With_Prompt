import tiktoken


# 計算 message 中的 token 數量
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the amount tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there is a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}.""")
    num_tokens = 0
    for token_message in messages:
        num_tokens += tokens_per_message
        for key, value in token_message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply primed with <|start|>assistant<|message|>
    return num_tokens


def count_jsonl_tokens(filepath):
    import json
    with open(filepath, 'r', encoding='UTF-8') as jsonl_file:
        jsonl_list = jsonl_file.readlines()
        count_tokens = 0
        for line in jsonl_list:
            json_data = json.loads(line)
            tokens = num_tokens_from_messages([json_data], 'gpt-3.5-turbo-0301')
            count_tokens += tokens
        print(f"總共有{len(jsonl_list)}項: {count_tokens}個tokens，curie需要{count_tokens * 0.000015497}美金")
    return count_tokens
