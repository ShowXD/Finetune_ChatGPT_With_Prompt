import pandas as pd
import json
import pysrt
import os
import logging
import datetime
from datetime import timedelta

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)


# 讀取 Pytutor 資料
def read_pytutor_data():
    excel_path = "dataset/test.xlsx"
    # excel_path = "dataset/pytutor_usercode_backend_2023-02-06_11_58_45.xlsx"
    sheet_name = 'Sheet1'
    data_cols = ['contract_id', 'editorcode']
    try:
        df = pd.read_excel(excel_path, sheet_name, usecols=data_cols, nrows=1000)
        return df
    except Exception as e:
        logging.error(f"讀取Excel檔案失敗: {str(e)}")
        return None


class StoryDataReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


class StoryDataProcessor:
    def __init__(self, data):
        self.data = data

    def process_data(self):
        story_list = []
        number_list = []
        for row in self.data:
            number_list.append(self.data[row]['contract_id'])
            story_list.append(self.data[row]['contract_story'])
        return pd.DataFrame({'number': number_list, 'story': story_list})


# 讀取題目資料
def read_story_data():
    story_file_path = "dataset/story.json"

    reader = StoryDataReader(story_file_path)
    story_data = reader.read_json_file()

    processor = StoryDataProcessor(story_data)
    df = processor.process_data()

    return df


# 以時間切割字幕資料
def split_subtitle_with_time(srt_file, duration=1) -> pd.DataFrame:
    subs = pysrt.open(srt_file)
    data = []
    interval = timedelta(minutes=duration)

    tmp_start_time = None
    tmp_content = []
    for sub in subs:
        content = sub.text
        start = sub.start.to_time()
        end = sub.end.to_time()
        tmp_content.append(content)

        if tmp_start_time is None:
            tmp_start_time = start
            continue
        elif datetime.datetime.combine(datetime.date.today(), end) - datetime.datetime.combine(datetime.date.today(), tmp_start_time) >= interval:
            data.append([
                os.path.basename(srt_file).split("_")[0],
                tmp_content,
                tmp_start_time.strftime("%H:%M:%S"),
                end.strftime("%H:%M:%S")
            ])
            tmp_start_time = None
            tmp_content = []

    df = pd.DataFrame(data, columns=['chapter', 'content', 'start', 'end'])
    return df


# 以切割份數切割字幕資料
def split_subtitle_with_count(srt_file, num_segments=10) -> pd.DataFrame:
    subs = pysrt.open(srt_file)
    data = []
    total_subs = len(subs)
    subs_per_segment = total_subs // num_segments

    start_index = 0
    for i in range(num_segments):
        end_index = start_index + subs_per_segment if i < num_segments - 1 else total_subs
        segment_subs = subs[start_index:end_index]

        content = [sub.text for sub in segment_subs]
        start = segment_subs[0].start.to_time()
        end = segment_subs[-1].end.to_time()

        data.append([
            os.path.basename(srt_file).split("_")[0],
            content,
            start.strftime("%H:%M:%S"),
            end.strftime("%H:%M:%S")
        ])

        start_index = end_index

    df = pd.DataFrame(data, columns=['chapter', 'content', 'start', 'end'])
    return df
