"""Basic sound tests"""
import pytest

@pytest.mark.parametrize("name",
                         [("sounds\\file_example_WAV_2MG.wav"),
                          ])
def test_play_sound(name):

    import os
    os.system(name)

