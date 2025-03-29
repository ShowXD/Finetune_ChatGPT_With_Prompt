from tqdm import tqdm
import os
import pandas as pd
import openai
import time
import logging
from read_data import read_pytutor_data, read_story_data, split_subtitle_with_count, split_subtitle_with_time
from create_prompt import fix_program_prompt, subtitle_to_topic_prompt
from create_jsonl import create_jsonl, create_when_the_topic_dataset, create_what_the_topic_dataset
from utils import num_tokens_from_messages, count_jsonl_tokens


# 二次處理 ChatGPT 回傳的重點，變得更加清楚
def process_chatGPT_response(filepath) -> pd.DataFrame:
    df = pd.read_excel(filepath, 'Sheet1')
    df['clear_content'] = df['topic'].str.split('\n').apply(lambda x: [line.lstrip("- ").lstrip("1234567890. ").lstrip("。") for line in x])
    return df


def prepare_problem_data() -> list:
    story_df = read_story_data()
    pytutor_df = read_pytutor_data()

    return fix_program_prompt(pytutor_df, story_df)


def prepare_prompt_subtitle_data(filepath) -> pd.DataFrame:
    df = split_subtitle_with_time(filepath)
    # df = split_subtitle_with_count(filepath)
    df['prompts'] = df.apply(subtitle_to_topic_prompt, axis=1)

    return df


def send_prompt_to_chatGPT(prompts) -> list:
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    success = False
    while not success:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompts,
                temperature=0,
                max_tokens=257,
                top_p=0.1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=["\n\n"]
            )
            success = True
            return response['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"\n發生錯誤: {str(e)}\n等待5秒後重試...")
            time.sleep(5)


def get_topic_of_subtitle(filepath) -> pd.DataFrame:
    df_prompt = prepare_prompt_subtitle_data(filepath)
    num_tokens = df_prompt['prompts'].apply(num_tokens_from_messages).sum()
    print(f"\n總共有{num_tokens}個tokens，需要{num_tokens / 500000}美金")
    tqdm.pandas()
    df_prompt['topic'] = df_prompt['prompts'].progress_apply(send_prompt_to_chatGPT)
    df_prompt.to_excel('output.xlsx', index=False)

    return df_prompt


def workflow_of_subtitle_topic():
    df_output = pd.DataFrame()
    for root, dirs, files in os.walk("dataset/caption"):
        for file in files:
            if file.endswith(".srt"):
                # filepath = "D:\\Saves\\GitHub\\ChatGPT\\dataset\\caption\\第五週\\5-1-1_模組化設計與函式宣告.srt"
                filepath = os.path.join(root, file)
                df = get_topic_of_subtitle(filepath)
                df_output = pd.concat([df_output, df], axis=0)

    df_output.to_excel("output/output.xlsx", index=False)


def workflow_of_subtitle_jsonl():
    filepath = "D:\\Saves\\GitHub\\ChatGPT\\output\\subtitle\\output-程式知識點.xlsx"
    df = process_chatGPT_response(filepath)  # 移除標號，放進 df['clear_content']
    jsonl_list = []

    focus_time_in_subtitle_dataset = create_when_the_topic_dataset(df)  # 生成 fine-tune 用的 list
    jsonl_list.extend(focus_time_in_subtitle_dataset)

    subtitle_focus_dataset = create_what_the_topic_dataset(df)  # 生成 fine-tune 用的 list
    jsonl_list.extend(subtitle_focus_dataset)

    create_jsonl(jsonl_list)  # 生成 jsonl 檔案


def main():
    # workflow_of_subtitle_topic()
    # workflow_of_subtitle_jsonl()
    count_jsonl_tokens(filepath='output/jsonl/subtitle_topic.jsonl')


if __name__ == '__main__':
    main()
