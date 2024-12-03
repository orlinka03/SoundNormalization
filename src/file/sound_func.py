import enum
import os
import shutil
from pathlib import Path

from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
from pymediainfo import MediaInfo

SIZE_THRESHOLD = 50 * 1024 * 1024  # Пример порога для большого файла (50MB)

class FileType(enum.Enum):
    Video = "Video",
    Audio = "Audio"

def get_file_type(file):
    """
    Определяет тип файла: видео, аудио или неизвестный.
    """
    media_info = MediaInfo.parse(file)
    has_video = False
    has_audio = False
    for track in media_info.tracks:
        if track.track_type == FileType.Video.name:
            has_video = True
        elif track.track_type == FileType.Audio.name:
            has_audio = True

    if has_video:
        return FileType.Video.name
    elif has_audio:
        return FileType.Audio.name
    return "Unknown"


def get_sound(file):
    """
    Загружает звуковой файл (или извлекает аудио из видеофайла).
    Если файл большой, извлекает аудио во временный файл.
    """
    file_type = get_file_type(file)

    # Получаем размер файла
    file_size = os.path.getsize(file)

    # Проверка типа файла
    if file_type == "Unknown":
        raise ValueError(f"Unsupported file type: '{file}'. Please upload a valid audio or video file.")

    if file_type == FileType.Audio.name:
        print(f"Loading audio from audio file ...")
        return load_audio(file, file_type)

    if file_size > SIZE_THRESHOLD:
        print(f"File is large ({file_size / (1024 * 1024):.2f} MB), using temporary file...")
        return extract_audio_to_temp_file(file, file_type)
    else:
        print(f"File is small ({file_size / (1024 * 1024):.2f} MB), using memory processing...")
        return load_audio(file, file_type)


def load_audio(file, file_type):
    """
    Загружает аудио из файла, независимо от его типа (видео или аудио).
    Если видео, извлекает аудио.
    """
    if file_type == FileType.Video.name:
        print("Extracting audio from video file...")
        video = VideoFileClip(file)
        audio = video.audio
        temp_audio_path = "temp_audio.wav"
        audio.write_audiofile(temp_audio_path, codec='pcm_s16le', fps=44100)
        sound = AudioSegment.from_file(temp_audio_path)
        os.remove(temp_audio_path)  # Удаляем временный файл
    elif file_type == FileType.Audio.name:
        print("Loading audio from audio file...")
        sound = AudioSegment.from_file(file)
    else:
        raise ValueError("Unsupported file type")

    return sound


def extract_audio_to_temp_file(file, file_type):
    """
    Извлекает аудио и сохраняет его во временный файл для больших файлов.
    """
    sound = load_audio(file, file_type)
    temp_audio_path = "temp_audio.wav"
    sound.export(temp_audio_path, format="wav")  # Экспортируем в WAV
    sound_from_file = AudioSegment.from_file(temp_audio_path)
    os.remove(temp_audio_path)  # Удаляем временный файл
    return sound_from_file


def apply_compression(audio, threshold=-30, ratio=4.0):
    # Применение компрессии с настройкой порога и соотношения
    compressed_audio = compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
    return compressed_audio


def compress_dynamic_range(audio, threshold, ratio):
    """
    Применяет компрессию для уменьшения динамического диапазона.
    """
    audio = audio.set_channels(1)  # Для упрощения работы, ставим моно
    compressed = audio.compress_dynamic_range(threshold=threshold, ratio=ratio)
    return compressed


def save_or_replace_audio(file, audio, file_type, res_file="compressed file"):
    """
    Сохраняет или заменяет аудио в зависимости от типа файла, удаляя временные файлы.
    """
    # Сохраняем обработанное аудио во временный файл
    temp_audio_path = "temp_compressed_audio.wav"
    audio.export(temp_audio_path, format="wav")

    try:
        if file_type == FileType.Video.name:
            print("Replacing audio in video file...")
            video = VideoFileClip(file)
            audio_clip = AudioFileClip(temp_audio_path)
            video = video.set_audio(audio_clip)
            output_video_path = res_file
            video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
            return output_video_path

        elif file_type == FileType.Audio.name:
            output_audio_path = res_file
            audio.export(output_audio_path, format="wav")
            return output_audio_path

        else:
            raise ValueError("Unsupported file type")

    finally:
        # Удаляем временный файл
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Temporary file {temp_audio_path} deleted.")

def cut_from_file(file, start, end):
    if get_file_type(file) == FileType.Video.name:
        print("VIDEO")
        clip = VideoFileClip(file)
        clip = clip.subclip(start, end)
        return clip
    elif get_file_type(file) == FileType.Audio.name:
        print("AUDIO")
        audio = AudioSegment.from_file(file)
        trimmed_audio = audio[start * 1000:end * 1000]
        return trimmed_audio

def save_file(fragment, name="output"):
    if isinstance(fragment, AudioSegment):
        if not name.endswith(".mp3") and not name.endswith(".wav"):
            name += ".mp3"
        fragment.export(name, "mp3")
    elif isinstance(fragment, VideoFileClip):
        if not name.endswith(".mp4"):
            name += ".mp4"
        fragment.write_videofile(name)

def save_result(file, path):
    if path.endswith not in (".mp3", '.mp4'):
        if get_file_type(file) == FileType.Audio.name:
            path += ".mp3"
        elif get_file_type(file) == FileType.Video.name:
            path += ".mp4"
    shutil.copy(file, path)



def get_file_extension(file):
    return Path(file).suffix