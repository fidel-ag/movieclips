import moviepy.editor as mpe
import sys
import logging
import os
import json
os.environ["PYTHONIOENCODING"] = "UTF-8"
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
imagemagick_path = "convert"  # Set the path to the ImageMagick executable
os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path
import time

def create_watermark (video):
    watermakpath=os.path.join(os.getcwd(),"media", "watermark.png")
    watermark = mpe.ImageClip(watermakpath)
    watermark = watermark.set_duration(video.duration).resize(height=video.h * 0.5).set_pos("center")
    watermaked_video = mpe.CompositeVideoClip([video, watermark])
    return watermaked_video


def setup_audio(audio_background,backgroud_volume,start_audio,duration):
    audio_background=audio_background.set_start(start_audio)
    audio_background=audio_background.subclip(0,duration)
    audio_background = audio_background.volumex(backgroud_volume)
    return audio_background

def add_audio(video_path,audio_paths,backgroud_volumes,start_audios,durations):
    my_clip = mpe.VideoFileClip(video_path)
    for audio_path, backgroud_volume,start_audio,duration in zip(audio_paths,backgroud_volumes,start_audios,durations):
        audio_background = mpe.AudioFileClip(audio_path)
        assert start_audio+duration<my_clip.duration
        audio_background=setup_audio(audio_background,backgroud_volume,start_audio,duration)
        print(audio_background)
        final_audio = mpe.CompositeAudioClip([my_clip.audio, audio_background])
        my_clip = my_clip.set_audio(final_audio)

    logging.info("FINISHED Adding the audio")
    return my_clip


def main():
    logging.info(sys.argv)
    if len(sys.argv)<5:
        print("Usage: python music.py <video_path> <audio_session_path> <outputpath>")
        sys.exit(1)

    video_path=sys.argv[1]
    audio_session_path=sys.argv[2]
    with open(audio_session_path, 'r') as f:
        audio_session=json.loads(f.read())

    video_output_final_name=audio_session["video_output_final_name"]
    backgroud_volume=audio_session["backgroud_volume"]
    start_audio=audio_session["start_audio"]
    duration=audio_session["duration"]
    audio_path=audio_session["audio_paths"]
    working_directory=sys.argv[4]
    with open(os.path.join(working_directory ,"editing.json"),"w") as f:
        f.write(json.dumps({"status":False}))
    outputpath=sys.argv[3]

    try:

        my_finalclip= add_audio(video_path,audio_path,backgroud_volume,start_audio,duration)
        my_finalclip.write_videofile(os.path.join(outputpath,video_output_final_name))
        watermaked_video=create_watermark(my_finalclip)
        watermaked_video.write_videofile(os.path.join(outputpath,"watermarked"+video_output_final_name))
        with open(os.path.join(working_directory ,"editing.json"),"w") as f:
            f.write(json.dumps({"status":True}))
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        sys.exit(1)
if __name__=="__main__":
    main()