def get_story_by_contract_id(df_story, contract_id):
    story = df_story.loc[df_story['number'] == contract_id, 'story'].iloc[0]
    return story


# 建立故事資訊給 ChatGPT 的 message
def fix_program_prompt(df, df_story) -> list:
    chat_message_list = []
    for _, row in df.iterrows():
        story = get_story_by_contract_id(df_story, row['contract_id'])
        chat_message_list.append([
            {"role": "system", "content": "You are a college teaching assistant majoring in Python."},
            {"role": "assistant", "content": f"This is question: {story}"},
            {"role": "assistant", "content": f"This is my answer: {row['editorcode']}"},
            {"role": "user", "content": "根據上述的資訊，我該如何修正或改進程式碼，但不要給我程式碼?"},
        ])
    return chat_message_list


def subtitle_to_topic_prompt(row) -> list:
    prompts_list = [{"role": "system", "content": "你是善於從字幕中獲取程式相關重點的模型"}]
    for content in row.content:
        prompts_list.append(
            {"role": "assistant", "content": f"字幕:{content}"}
        )
    prompts_list.append({"role": "user", "content": f"以上字幕的時間為{row.start}到{row.end}，請條列這段時間的程式的知識點。"})
    return prompts_list

