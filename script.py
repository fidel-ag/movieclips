
import logging
from pathlib import Path
from typing import List, Dict
import sys
import os
import re
import pysrt
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
    TextClip,
    VideoFileClip,
    ImageClip,  # Add this line
)

from moviepy.video.fx.crop import crop
from moviepy.video.fx.loop import loop
from moviepy.config import change_settings
import openai
import requests
import shutil
from moviepy.video.fx.speedx import speedx
from elevenlabs import Voice, VoiceSettings, play, save
from elevenlabs.client import ElevenLabs
import subprocess
import json
import os
os.environ["PYTHONIOENCODING"] = "UTF-8"
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
imagemagick_path = "convert"  # Set the path to the ImageMagick executable
os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path


# You can also set the MoviePy config
change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})


# Base URL for Pexels API


def save_audio(audio_data, filename="output_of_lead_kyrona.mp3"):
    with open(filename, "wb") as f:
        f.write(audio_data)
        print(f"Audio saved to: {filename}")


# Function to search for videos
def search_videos(query, per_page=15, page=1):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "page": page}
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to search videos: {response.status_code}")
        return None

def create_watermark (video):
    watermakpath=os.path.join(os.getcwd(),"media", "watermark.png")
    watermark = ImageClip(watermakpath)
    watermark = watermark.set_duration(video.duration).resize(height=video.h * 0.5).set_pos("center")
    watermaked_video = CompositeVideoClip([video, watermark])
    return watermaked_video


# Function to find the HD video file with the highest number of likes and correct dimensions
def get_best_hd_file(videos):
    best_video = None
    best_file = None
    highest_likes = -1

    for video in videos:
        for file in video["video_files"]:
            if (
                file["width"] >= 1280
                and file["height"] >= 720
                and file["width"] / file["height"] >= 0.8
            ):
                likes = video.get("likes", 0)
                if likes > highest_likes:
                    highest_likes = likes
                    best_video = video
                    best_file = file

    return best_video, best_file


def load_subtitles_from_txt_file(srt_file: Path) -> pysrt.SubRipFile:
    # if not srt_file.exists():
    #     raise FileNotFoundError(f"SRT File not found: {srt_file}")
    return pysrt.open(srt_file)


def get_segments_using_srt_file(srt_file: Path) -> int:
    subtitles = load_subtitles_from_txt_file(srt_file)
    return len(subtitles)


def get_video_duration_from_srt(srt_file):
    with open(srt_file, "r") as file:
        content = file.read()
    timestamps = re.findall(r"\d{2}:\d{2}:\d{2},\d{3}", content)
    end_times = timestamps[1::2]  # Get all end times
    last_end_time = end_times[-1] if end_times else "00:00:00,000"
    h, m, s_ms = last_end_time.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def generate_blank_video_with_audio(audio_file, srt_file, output_video):
    # Get the duration from the SRT file
    srt_duration = get_video_duration_from_srt(srt_file)

    # Get the duration of the audio file
    audio_clip = AudioFileClip(audio_file)
    audio_duration = audio_clip.duration

    # Determine the maximum duration between the SRT and audio file
    duration = max(srt_duration, audio_duration)

    # Create a blank (black) clip with 4:5 aspect ratio
    width, height = 800, 1000  # 4:5 aspect ratio
    blank_clip = ColorClip(size=(width, height), color=(0, 0, 0)).set_duration(duration)

    # Combine the audio with the blank video
    final_video = CompositeVideoClip([blank_clip]).set_audio(audio_clip)

    # Write the final video to a file
    final_video.write_videofile(output_video, fps=24)


def load_video_from_file(file: Path) -> VideoFileClip:
    print(f"Attempting to load video from file: {file}")  # Debug statement
    # Check if file exists
    if not file.exists():
        print(f"File not found: {file}")  # Debug statement if file does not exist
    return VideoFileClip(os.path.normpath(file))


def crop_to_aspect_ratio(video: VideoFileClip, desired_aspect_ratio: float) -> VideoFileClip:
    video_aspect_ratio = video.w / video.h
    if video_aspect_ratio > desired_aspect_ratio:
        new_width = int(desired_aspect_ratio * video.h)
        new_height = video.h
        x1 = (video.w - new_width) // 2
        y1 = 0
    else:
        new_width = video.w
        new_height = int(video.w / desired_aspect_ratio)
        x1 = 0
        y1 = (video.h - new_height) // 2
    x2 = x1 + new_width
    y2 = y1 + new_height
    return crop(video, x1=x1, y1=y1, x2=x2, y2=y2)


def load_subtitles_from_file(srt_file: Path) -> pysrt.SubRipFile:
    # if not srt_file.exists():
    #     raise FileNotFoundError(f"SRT File not found: {srt_file}")
    return pysrt.open(srt_file)


def adjust_segment_duration(segment: VideoFileClip, duration: float) -> VideoFileClip:
    current_duration = segment.duration
    if current_duration < duration:
        return loop(segment, duration=duration)
    elif current_duration > duration:
        return segment.subclip(0, duration)
    return segment


def adjust_segment_properties(
    segment: VideoFileClip, original: VideoFileClip
) -> VideoFileClip:
    segment = segment.set_fps(original.fps)
    segment = segment.set_duration(segment.duration)
    segment = segment.resize(newsize=(original.w, original.h))
    return segment


def subriptime_to_seconds(srt_time: pysrt.SubRipTime) -> float:
    return (
        srt_time.hours * 3600
        + srt_time.minutes * 60
        + srt_time.seconds
        + srt_time.milliseconds / 1000.0
    )


def get_segments_using_srt(
    video: VideoFileClip, subtitles: pysrt.SubRipFile
) -> (List[VideoFileClip], List[pysrt.SubRipItem]):
    subtitle_segments = []
    video_segments = []
    video_duration = video.duration

    for subtitle in subtitles:
        start = subriptime_to_seconds(subtitle.start)
        end = subriptime_to_seconds(subtitle.end)

        if start >= video_duration:
            logging.warning(
                f"Subtitle start time ({start}) is beyond video duration ({video_duration}). Skipping this subtitle."
            )
            continue

        if end > video_duration:
            logging.warning(
                f"Subtitle end time ({end}) exceeds video duration ({video_duration}). Clamping to video duration."
            )
            end = video_duration

        if end <= start:
            logging.warning(
                f"Invalid subtitle duration: start ({start}) >= end ({end}). Skipping this subtitle."
            )
            continue

        video_segment = video.subclip(start, end)
        if video_segment.duration == 0:
            logging.warning(
                f"Video segment duration is zero for subtitle ({subtitle.text}). Skipping this segment."
            )
            continue

        subtitle_segments.append(subtitle)
        video_segments.append(video_segment)

    return video_segments, subtitle_segments


def add_subtitles_to_clip(clip: VideoFileClip,subtitle: pysrt.SubRipItem,base_font_size: int = 42,color: str = "white",bg_color: str ="black",margin: int = 20,font_path : str ="Montserrat-SemiBold.ttf") -> VideoFileClip:
    logging.info(f"Adding subtitle: {subtitle.text}")
    # font_path = os.path.join(os.getcwd(), "data", "Montserrat-SemiBold.ttf")
    # Calculate the scaling factor based on the resolution of the clip
    scaling_factor = clip.h / 1080
    font_size = int(base_font_size * scaling_factor)

    def split_text(text: str, max_line_width: int) -> str:
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) <= max_line_width:
                current_line.append(word)
                current_length += len(word) + 1  # +1 for the space
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word) + 1

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    # Function to ensure the subtitle text does not exceed two lines
    def ensure_two_lines(
        text: str, initial_max_line_width: int, initial_font_size: int
    ) -> (str, int):
        max_line_width = initial_max_line_width
        font_size = initial_font_size
        wrapped_text = split_text(text, max_line_width)

        # Adjust until the text fits in two lines
        while wrapped_text.count("\n") > 1:
            max_line_width += 1
            font_size -= 1
            wrapped_text = split_text(text, max_line_width)

            # Stop adjusting if font size becomes too small
            if font_size < 20:
                break

        return wrapped_text, font_size

    max_line_width = 35  # Initial value, can be adjusted

    if len(subtitle.text) > 60:
        wrapped_text, adjusted_font_size = ensure_two_lines(
            subtitle.text, max_line_width, font_size
        )
    else:
        wrapped_text, adjusted_font_size = (
            split_text(subtitle.text, max_line_width),
            font_size,
        )

    # Create a temporary TextClip to measure the width of the longest line
    temp_subtitle_clip = TextClip(
        wrapped_text, fontsize=adjusted_font_size, font=font_path
    )
    longest_line_width, text_height = temp_subtitle_clip.size

    subtitle_clip = TextClip(
        wrapped_text,
        fontsize=adjusted_font_size,
        color=color,
        font=font_path,
        method="caption",
        align="center",
        size=(longest_line_width, None),  # Use the measured width for the longest line
    ).set_duration(clip.duration)

    text_width, text_height = subtitle_clip.size
    small_margin = 8  # Small margin for box width
    box_width = (
        text_width + small_margin
    )  # Adjust the box width to be slightly larger than the text width
    box_height = text_height + margin
    box_clip = (
        ColorClip(size=(box_width, box_height), color=bg_color)
        .set_opacity(0.5)
        .set_duration(subtitle_clip.duration)
    )

    # Adjust box position to be slightly higher in the video
    box_position = ("center", clip.h - box_height - 2 * margin)
    subtitle_position = (
        "center",
        clip.h - box_height - 2 * margin + (box_height - text_height) / 2,
    )

    box_clip = box_clip.set_position(box_position)
    subtitle_clip = subtitle_clip.set_position(subtitle_position)

    return CompositeVideoClip([clip, box_clip, subtitle_clip])


def replace_video_segments(original_segments: List[VideoFileClip],replacement_videos: Dict[int, VideoFileClip],
    subtitles: pysrt.SubRipFile,
    original_video: VideoFileClip,
) -> List[VideoFileClip]:
    combined_segments = original_segments.copy()
    for replace_index, replacement_video in replacement_videos.items():
        if 0 <= replace_index < len(combined_segments):
            target_duration = combined_segments[replace_index].duration
            start = subriptime_to_seconds(subtitles[replace_index].start)
            end = subriptime_to_seconds(subtitles[replace_index].end)

            # Adjust replacement video duration to match target duration
            if replacement_video.duration < target_duration:
                replacement_segment = loop(replacement_video, duration=target_duration)
            else:
                replacement_segment = replacement_video.subclip(0, target_duration)

            adjusted_segment = adjust_segment_properties(
                replacement_segment, original_video
            )
            adjusted_segment_with_subtitles = add_subtitles_to_clip(
                adjusted_segment, subtitles[replace_index],
            )
            combined_segments[replace_index] = adjusted_segment_with_subtitles

    return combined_segments


def parse_srt(subtitle_file_path):
    with open(subtitle_file_path, "r") as file:
        srt_content = file.read()

    pattern = re.compile(
        r"\d+\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})"
    )
    matches = pattern.findall(srt_content)

    timestamps = []
    for start, end in matches:
        start = start.replace(",", ".")
        end = end.replace(",", ".")
        timestamps.append((start, end))

    return timestamps


def time_to_seconds(time_str):
    h, m, s = time_str.split(":")
    s, ms = s.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000



def reencode_video(
    input_path, output_path, codec="libx264", resolution="1080x1350", fps=30
):
    command = [
        "ffmpeg",
        "-i",
        input_path,
        "-vf",
        f"scale={resolution}",
        "-r",
        str(fps),
        "-c:v",
        codec,
        "-preset",
        "fast",
        "-y",
        output_path,
    ]
    subprocess.run(command, check=True)




def resize_to_aspect_ratio(input_path, output_path, aspect_ratio=4 / 5):
    command = [
        "ffmpeg",
        "-i",
        input_path,
        "-vf",
        f"scale=iw*{aspect_ratio}:ih",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-y",
        output_path,
    ]
    subprocess.run(command, check=True)


def convert_video_to_mp3(video_path, mp3_output_path):
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-q:a",
        "0",
        "-map",
        "a",
        "-y",
        mp3_output_path,
    ]
    subprocess.run(command, check=True)


def main():
    if len(sys.argv) < 5:
        print("Usage: python script.py <manual_script_file> <voice_id> <video_file> <userId>")
        sys.exit(1)

    # Script arguments
    manual_script_file = sys.argv[1]
    voice_id = sys.argv[2]
    userid=sys.argv[5]
    original_video_file = os.path.join(os.getcwd(), "tmp",userid, sys.argv[3])
    elevenlabs = sys.argv[4]
    
    print(f"Attempting to load video from: {original_video_file}")

    print(f"Original video file path set to: {original_video_file}")
    print("Listing directory contents:")
    print(userid)
    print(f"Current working directory: {os.getcwd()}")
    # print(f"Environment variables related to path/file handling: {os.getenv('PATH')}")
    client = ElevenLabs(api_key=elevenlabs)  # Replace with your actual API key

    # Paths
    tmp_folder = os.path.join(os.getcwd(), "tmp",userid)
    print(tmp_folder)
    session_data_file = os.path.join(tmp_folder, "session_data.json")
    mp3_file_of_same_video = os.path.join(os.getcwd(), "tmp",userid, "audio_from_video.mp3")
    with open(os.path.join(os.getcwd(), "tmp",userid, "editing.json"),"w") as f:
        f.write(json.dumps({"status":False}))

    # Ensure tmp folder and session file exist
    if not os.path.exists(session_data_file):
        print(f"Session data file not found: {session_data_file}")
        sys.exit(1)

    with open(session_data_file, "r") as f:
        session_data = json.load(f)

    # Extract paths from session data
    updated_original_script_path = session_data["updated_original_script_path"]
    manual_script_path = session_data["manual_script_path"]
    slide_images_paths = session_data["slide_images_paths"]
    voice_id = session_data["voice_id"]
    original_transcription_path = session_data["original_transcription_path"]
    Text_coloring=session_data["textColor"]
    background_Coloring=session_data["bgColor"]
    fontSize=int(session_data["fontSize"])
    font_path=session_data["font_path"]
    # Generate audio for new slides
    audio_file_path = os.path.join(tmp_folder, "generated_audio.mp3")

    try:
        with open(manual_script_file, "r") as f:
            manual_text = f.read()

        # Generate new voiceover using Eleven Labs API
        audio_data = client.generate(
            text=manual_text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5),
            ),
        )
        save(audio_data, audio_file_path)
        logging.info(f"Generated audio for new rows and saved to {audio_file_path}")

    except Exception as e:
        logging.error(f"Error generating audio: {e}")
        sys.exit(1)

    # Process the video based on the updated original script
    try:
        # original_video = VideoFileClip(original_video_file)
        # resized_video1_path = os.path.join(tmp_folder, "resized_video1.mp4")
        # resized_video1 = VideoFileClip(resized_video1_path)

        # Load the updated original script (for trimming the original video)
        print(updated_original_script_path,original_video_file,mp3_file_of_same_video)
        with open(updated_original_script_path, "r") as f:
            updated_script_lines = f.readlines()

        # Open manual script for new slides
        logging.info(manual_script_path)
        with open(manual_script_path, "r") as f:
            new_script_lines = f.readlines()
        convert_video_to_mp3(original_video_file, mp3_file_of_same_video)
        # Generate SRT file for the updated script (optional)
        srt_file_path = generate_srt(
            mp3_file_of_same_video, original_transcription_path
        )
        num_slides = len(
            slide_images_paths
        )  # Number of slides (and corresponding audio segments)
        audio_segments = generate_audio_segments(audio_file_path, num_slides)
        original_videoo_size=VideoFileClip(original_video_file).size
        video1_clips = []
        for idx, (line, image_path, audio_clip) in enumerate(
            zip(manual_text.splitlines(), slide_images_paths, audio_segments)
        ):
            text = line.strip()
            # audio_clip = AudioFileClip(audio_file_path)
            duration = audio_clip.duration

            if image_path and os.path.exists(image_path):

                if image_path.endswith(".png"):
                    image_clip = ImageClip(image_path).set_duration(duration)
                elif image_path.endswith(".mp4"):
                    image_clip = VideoFileClip(image_path).subclip(0, duration)
                else:
                    continue

                image_clip = image_clip.resize(width=original_videoo_size[0])
                image_clip = image_clip.resize(height=min(original_videoo_size[1],image_clip.size[1]))
                image_clip = image_clip.on_color(size=original_videoo_size, color=(0, 0, 0), col_opacity=1)
                video_clip = add_styled_subtitles_to_clip(image_clip, text,color=Text_coloring,bg_color=background_Coloring,base_font_size=fontSize,font_path=font_path)
            else:
                # Create a blank video clip with just text
                blank_clip = ColorClip(size=(800, 1000), color=(0, 0, 0)).set_duration(
                    duration
                )

                # Apply styled subtitles to the blank clip
                video_clip = add_styled_subtitles_to_clip(blank_clip, text,color=Text_coloring,bg_color=background_Coloring,base_font_size=fontSize,font_path=font_path)

            # Set the audio for the clip (AI-generated voice)
            video_clip = video_clip.set_audio(audio_clip)
            video1_clips.append(video_clip)

        # Concatenate all Video 1 clips together
        video1 = concatenate_videoclips(video1_clips, method="compose")
        # video1 = crop_to_aspect_ratio(video1, 4 / 5)

        # Step 2: Save the resized Video 1
        video1_resized_path = os.path.join(tmp_folder, "video1_resized.mp4")
        video1.write_videofile(
            video1_resized_path, fps=24, codec="libx264", audio_codec="aac"
        )
        resized_video1 = VideoFileClip(video1_resized_path)
        print("------------------------------------------------------------------------"
              )
        # Process video to remove parts corresponding to deleted slides
        trimmed_video_path = os.path.join(tmp_folder, "trimmed_video.mp4")
        trimmed_video = trim_video(
            original_video_file,
            original_transcription_path,
            srt_file_path,
            updated_original_script_path,
            trimmed_video_path,
        )
        print(trimmed_video)
        print(VideoFileClip(trimmed_video))
        if not trimmed_video:
            logging.error("Error trimming video based on updated script.")
            sys.exit(1)
        # Step 4: Combine Video 1 and Video 2
        final_video_clips = [
            resized_video1,
            VideoFileClip(trimmed_video),
        ]  # Video 1 first, then Video 2

        # Concatenate all video clips into one final video
        final_video = concatenate_videoclips(final_video_clips, method="compose")
        output_video_path = os.path.join(
            os.getcwd(), "static", "finalbeforeMusic", session_data["video_output_final_name"]
        )
        final_video.write_videofile(
            output_video_path, fps=24, codec="libx264", audio_codec="aac"
        )
        output_video_path_watermarket = os.path.join(
            os.getcwd(), "static", "finalbeforeMusic", "watermarked"+session_data["video_output_final_name"]
        )
        logging.info(f"Final video saved to: {output_video_path}")
        watermaked_video=create_watermark(final_video)
        watermaked_video.write_videofile(
            output_video_path_watermarket, fps=24, codec="libx264", audio_codec="aac"
        )
        with open(os.path.join(os.getcwd(), "tmp",userid, "editing.json"),"w") as f:
            f.write(json.dumps({"status":True}))
        logging.info(f"Final watermarked video saved to: {output_video_path}")

    except Exception as e:
        logging.error(f"Error processing video: {e}")
        sys.exit(1)


def add_styled_subtitles_to_clip(clip: VideoFileClip,subtitle_text: str,base_font_size: int = 42,color: str = "white",bg_color="white",margin: int = 20,font_path : str ="Montserrat-SemiBold.ttf") -> VideoFileClip:
    """Applies styled subtitles to a video clip, ensuring subtitles do not exceed two lines."""
    logging.info(f"Adding styled subtitle: {subtitle_text}")

    # Path to the font file
    # font_path = os.path.join(os.getcwd(), "data", "Montserrat-SemiBold.ttf")

    # Calculate the scaling factor based on the resolution of the clip
    scaling_factor = clip.h / 1080
    font_size = int(base_font_size * scaling_factor)
    max_line_width = 35  # Initial max line width, can be adjusted

    def split_text(text: str, max_line_width: int) -> str:
        """Split text based on line width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_line_width:  # +1 for the space
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word) + 1

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    def ensure_two_lines(text: str, initial_max_line_width: int, initial_font_size: int) -> (str, int):
        """Ensure the text does not exceed two lines, adjusting font size and line width."""
        max_line_width = initial_max_line_width
        font_size = initial_font_size
        wrapped_text = split_text(text, max_line_width)

        while wrapped_text.count("\n") > 1:
            max_line_width += 1
            font_size -= 1
            wrapped_text = split_text(text, max_line_width)
            if font_size < 20:  # Minimum font size check
                break

        return wrapped_text, font_size

    # Apply wrapping and ensure two lines
    if len(subtitle_text) > 60:
        wrapped_text, adjusted_font_size = ensure_two_lines(subtitle_text, max_line_width, font_size )
    else:
        wrapped_text, adjusted_font_size = (split_text(subtitle_text, max_line_width),font_size,)
    temp_subtitle_clip = TextClip(wrapped_text, fontsize=adjusted_font_size, font=font_path)
    longest_line_width, text_height = temp_subtitle_clip.size

    # Create a TextClip for the styled subtitle
    subtitle_clip = TextClip(
        wrapped_text,
        fontsize=adjusted_font_size,
        color=color,
        font=font_path,
        method="caption",
        align="center",
        size=(longest_line_width, None),
    ).set_duration(clip.duration)

    # Measure the width for the box
    text_width, text_height = subtitle_clip.size
    box_width = text_width + 8  # Small margin
    box_height = text_height + margin

    # Create a semi-transparent background box
    print("lmao--------------------------------")
    print(bg_color)
    print([i for i in bytes.fromhex(bg_color[1:])])
    box_clip = ColorClip(
        size=(box_width, box_height), color=[i for i in bytes.fromhex(bg_color[1:])], duration=subtitle_clip.duration
    ).set_opacity(0.5)

    # Position the subtitle and box
    box_position = ("center", clip.h - box_height - 2 * margin)
    subtitle_position = (
        "center",
        clip.h - box_height - 2 * margin + (box_height - text_height) / 2,
    )

    box_clip = box_clip.set_position(box_position)
    subtitle_clip = subtitle_clip.set_position(subtitle_position)

    # Composite the clip with subtitles
    return CompositeVideoClip([clip, box_clip, subtitle_clip])


def generate_srt(audio_file, text_file):
    """Generates an SRT file using Aeneas for synchronization."""
    srt_file = text_file.replace(".txt", "_with_timestamps.srt")
    try:
        # Use Aeneas to align text and audio
        command = f'python3.10 -m aeneas.tools.execute_task "{audio_file}" "{text_file}" "task_language=eng|is_text_type=plain|os_task_file_format=srt" "{srt_file}"'
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            logging.error(f"Aeneas failed: {result.stderr.decode('utf-8')}")
            return None

        logging.info(f"SRT file generated successfully at {srt_file}")
        return srt_file

    except Exception as e:
        logging.error(f"Error generating SRT file: {e}")
        return None


def trim_video(original_video_path, original_path, srt_file_path, updated_script_path, output_path):
    """
    Trims the video based on the number of slides to be removed.
    We calculate the number of slides to remove by subtracting the length of
    updated script from the original script and remove that many segments from the video.
    """

    # Parse the timestamps from the SRT file
    timestamps = parse_srt(srt_file_path)
    print(f"Number of scenes available: {len(timestamps)}")  # Debug statement

    # Load the original and updated script lines
    with open(original_path, "r") as f:
        original_script_lines = [line.strip() for line in f.readlines() if line.strip()]

    with open(updated_script_path, "r") as f:
        updated_script_lines = [line.strip() for line in f.readlines() if line.strip()]

    # Calculate the number of slides (segments) to delete
    num_scenes_to_delete = len(original_script_lines) - len(updated_script_lines)
    print(f"Number of scenes to delete: {num_scenes_to_delete}")  # Debug statement

    if num_scenes_to_delete <= 0:
        logging.info("No scenes to delete, the video will remain untrimmed.")
        return original_video_path

    # Trim the video by removing the specified number of scenes from the start
    return trim_video_moviepy(
        original_video_path, srt_file_path, num_scenes_to_delete, output_path
    )


def trim_video_ffmpeg(input_video, srt_file_path, num_scenes_to_delete, output_video):
    """
    Uses FFmpeg to trim the video based on the number of scenes to delete,
    removing the specified number of segments from the start of the video.
    """

    # Parse timestamps
    timestamps = parse_srt(srt_file_path)

    if num_scenes_to_delete >= len(timestamps):
        logging.error("Number of scenes to delete exceeds available scenes.")
        return None

    # Get the start time for the first scene to keep (after removing the first `num_scenes_to_delete` scenes)
    trim_start_time = timestamps[num_scenes_to_delete][0]
    print(f"Trimming video from start time: {trim_start_time}")  # Debug statement

    # Use FFmpeg to trim the video from the specified start time
    command = [
        "ffmpeg",
        "-i",
        input_video,
        "-ss",
        trim_start_time,
        "-c",
        "copy",
        "-r 24 ",
        "-y",  # Overwrite the output file without asking
        output_video,
    ]
    print(f"Running FFmpeg command: {' '.join(command)}")  # Debug statement
    result = subprocess.run(command, check=True)
    print(f"FFmpeg command execution result: {result.returncode}")  # Debug result

    return output_video

def trim_video_moviepy(input_video, srt_file_path, num_scenes_to_delete, output_video):
    """
    Uses MoviePy to trim the video based on the number of scenes to delete,
    removing the specified number of segments from the start of the video.
    """

    # Parse timestamps
    timestamps = parse_srt(srt_file_path)

    if num_scenes_to_delete >= len(timestamps):
        logging.error("Number of scenes to delete exceeds available scenes.")
        return None

    # Get the start time for the first scene to keep (after removing the first `num_scenes_to_delete` scenes)
    trim_start_time = timestamps[num_scenes_to_delete][0]
    print(f"Trimming video from start time: {trim_start_time}")  # Debug statement

    # Load the video
    video = VideoFileClip(input_video)

    # Trim the video from the specified start time to the end of the video
    trimmed_video = video.subclip(trim_start_time)

    # Write the trimmed video to the output file
    trimmed_video.write_videofile(output_video, codec="libx264", fps=24)

    print(f"Video successfully trimmed and saved as {output_video}")

    return output_video


def generate_audio_segments(audio_file_path, num_segments):
    """
    Split the full audio file into segments, each corresponding to a slide.
    """
    full_audio_clip = AudioFileClip(audio_file_path)
    total_duration = full_audio_clip.duration
    segment_duration = total_duration / num_segments

    audio_segments = []
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = start_time + segment_duration
        segment_clip = full_audio_clip.subclip(start_time, end_time)
        audio_segments.append(segment_clip)

    return audio_segments


def concatenate_videos(video1_path, video2_path, output_path, fade_duration=1):
    # Re-encode both videos to ensure compatibility
    reencoded_video1 = os.path.join(os.getcwd(), "tmp", "reencoded_video1.mp4")
    reencoded_video2 = os.path.join(os.getcwd(), "tmp", "reencoded_video2.mp4")

    reencode_video(video1_path, reencoded_video1)
    reencode_video(video2_path, reencoded_video2)

    video1 = VideoFileClip(reencoded_video1)
    video2 = VideoFileClip(reencoded_video2)

    # Apply audio fade-out to the end of the first video
    video1 = video1.audio_fadeout(fade_duration)

    final_video = concatenate_videoclips([video1, video2],method="compose")
    final_video.write_videofile(output_path, codec="libx264")

    return output_path


if __name__ == "__main__":
    main()