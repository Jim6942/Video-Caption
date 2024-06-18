import assemblyai as aai
from pathlib import Path
import os


aai.settings.api_key = f"c6c17a0cf468402c920453242a34cfe3"
transcriber = aai.Transcriber()

input_dir = Path.cwd()
pre_caption_path = str(input_dir) + "\\pre caption"
post_caption_path = str(input_dir) +"\\post caption"
count = 0
converted_files = []


for files in os.listdir(pre_caption_path):
    path = pre_caption_path + "\\" + files
    pcf_format = files.replace(".mp3", "") + ".txt"
    pcf_path = post_caption_path + "\\" + pcf_format
    if (os.path.isfile(pcf_path) == False):
        transcript = transcriber.transcribe(path)
        result = transcript.text
        with open(f'{post_caption_path}\\{pcf_format}', 'w') as k:
            k.write(result)
        count += 1
        converted_files.append(pcf_format)


print("Captioning Successful :D")
print("Total files converted - " + str(count))
for name in converted_files:
    print("- " + name)