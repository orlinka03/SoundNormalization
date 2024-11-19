"""Basic sound tests"""
import pytest
from pydub import AudioSegment

from src.file.sound_func import get_file_type, get_sound, apply_compression


@pytest.mark.parametrize("name",
                         [("sounds\\file_example_WAV_2MG.wav"),
                          ])
def test_play_sound(name):

    import os
    os.system(name)

# Тест для определения типа файла
@pytest.mark.parametrize("file_path, expected_type", [
    ("sounds\\file_example_WAV_2MG.wav", "Audio"),
    ("sounds\\perfomance.mp4", "Video"),
    ("sounds\\txt_file.txt", "Unknown"),
])
def test_get_file_type(file_path, expected_type):
    result = get_file_type(file_path)
    assert result == expected_type

#Тест для получения звука из файла
@pytest.mark.parametrize("video_file, expected_type", [
    ("sounds\\file_example_WAV_2MG.wav", AudioSegment),
    ("sounds\\perfomance.mp4", AudioSegment)
])
def test_extract_audio_from_video(video_file, expected_type):
    audio = get_sound(video_file)
    assert isinstance(audio, expected_type)


# Тест для применения компрессии звука
def test_apply_compression():
    file_path = "sounds\\file_example_WAV_2MG.wav"
    audio = get_sound(file_path)
    compressed_audio = apply_compression(audio)
    assert compressed_audio.dBFS < audio.dBFS
