import json


def create_jsonl(input_list):
    try:
        with open(f'output/jsonl/subtitle_topic.jsonl', 'w', encoding='utf-8') as file:
            for item in input_list:
                json_str = json.dumps(item, ensure_ascii=False)
                file.write(json_str + '\n')
            file.close()
    except IOError as e:
        print(f'Json檔案建立失敗\n{e}')
    return None


def create_when_the_topic_dataset(df) -> list:
    dataset_rows = []
    for _, row in df.iterrows():
        for point in row['clear_content']:
            dataset_rows.append({
                "prompt":f"什麼時候有提到{point} \n\n###\n\n",
                "completion":f" 在{row['chapter']}章的{row['start']}到{row['end']}之間###"
            })

    return dataset_rows


def create_what_the_topic_dataset(df) -> list:
    dataset_rows = []
    for _, row in df.iterrows():
        for point in row['clear_content']:
            dataset_rows.append({
                "prompt":f"在{row['chapter']}的{row['start']}時候提到了什麼 \n\n###\n\n",
                "completion":f"提到關於{point}###"
            })

    return dataset_rows
