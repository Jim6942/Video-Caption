YouTube Video Captioning Project
-

This project is designed to automate the process of generating captions for YouTube videos by leveraging Assembly AI's API. The program takes MP3 files as input, processes them to generate captions, and outputs SRT files that can be used for video captioning. The entire workflow is organized into pre-caption and post-caption stages.

--------------------------------------------------------------------------------------------------------------------------------------------------------
Project Structure
-

main.py: The main script that orchestrates the captioning process.

pre_caption: A directory where users place their MP3 files to be captioned.

post_caption: A directory where the generated SRT caption files are saved.

--------------------------------------------------------------------------------------------------------------------------------------------------------
How the Program Works
-

Input Preparation

Place your MP3 files in the pre_caption folder.

--------------------------------------------------------------------------------------------------------------------------------------------------------
Running the Script: 

Execute main.py to start the captioning process.

--------------------------------------------------------------------------------------------------------------------------------------------------------
Caption Generation:

The script loops through all MP3 files in the pre_caption folder.
For each file, it calls the Assembly AI API to transcribe the audio.
The transcription result is saved as an SRT file in the post_caption folder.

--------------------------------------------------------------------------------------------------------------------------------------------------------
Skipping Already Captioned Files: 

If an MP3 file has already been captioned, the program will skip it to save time.

--------------------------------------------------------------------------------------------------------------------------------------------------------

Instructions for Running the Program
-

Clone the repository:

git clone https://github.com/Jim6942/Video-Caption.git

cd Video-Captioning

--------------------------------------------------------------------------------------------------------------------------------------------------------
Set up the environment:

Ensure you have Python installed.

--------------------------------------------------------------------------------------------------------------------------------------------------------
Install the required packages:

pip install assemblyai

--------------------------------------------------------------------------------------------------------------------------------------------------------
Place your MP3 files:

Copy your MP3 files into the pre_caption folder.

--------------------------------------------------------------------------------------------------------------------------------------------------------
Run the script:

Execute the main script to start captioning:

python main.py

--------------------------------------------------------------------------------------------------------------------------------------------------------
Output Summary: 

At the end of the process, the program displays the total number of videos captioned along with their names.

--------------------------------------------------------------------------------------------------------------------------------------------------------
