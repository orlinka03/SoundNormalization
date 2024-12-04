import shutil
import tempfile

import flet as ft
from pydub import AudioSegment
from src.file.sound_func import cut_from_file, save_file, apply_compression, load_audio, get_file_type, \
    save_or_replace_audio, get_file_extension, save_result


def main(page: ft.Page):
    page.title = "Audio/Video Editor"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    selected_file = None
    original_file = None
    video = None

    def back_to_original(e):
        nonlocal selected_file
        selected_file = original_file
        print("Orig")
        row1.content = update_video_player(selected_file)
        sound_funcs.value = None
        row2.content = ft.Text("Выберите функцию для обработки")
        page.update()

    def update_cut_slider(file_path):
        cut_slider.max = round(len(AudioSegment.from_file(file_path)) / 1000, 1)
        cut_slider.divisions = len(AudioSegment.from_file(file_path)) // 100

    def update_video_player(file_path):
        nonlocal video

        # Выводим путь файла для отладки
        print(f"File path: {file_path}")

        # Если видео еще не создано, создаем его

        try:
            video = ft.Video(
                expand=True,
                playlist=[ft.VideoMedia(file_path)],
                playlist_mode=ft.PlaylistMode.LOOP,
                fill_color=ft.colors.BLUE_400,
                aspect_ratio=16 / 9,
                volume=100,
                autoplay=True,
            )
            print("Video created successfully.")
        except Exception as e:
            print(f"Error creating video: {e}")

        return video

    top_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.FOLDER_OPEN,
                            tooltip="Open file",
                            on_click=lambda e: file_picker.pick_files(
                                allowed_extensions=["mp3", "wav", "mp4"],
                                dialog_title="Select a file for processing"
                            ),
                        ),
                        ft.IconButton(
                            icon=ft.icons.SAVE,
                            tooltip="Save file",
                            on_click=lambda e: save_picker.save_file(
                                dialog_title="Save processed file",
                                file_name="processed file",
                                initial_directory="D:/"
                            ),
                        ),
                        ft.IconButton(
                            icon=ft.icons.BACKUP,
                            tooltip="Back to original",
                            on_click=back_to_original
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(
                    "Sound Normalization App",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLACK87,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor="linear-gradient(to right, #f0f0f0, #e0e0e0)",  # Soft gray gradient
        padding=10,
        height=60,
        border=ft.border.all(0, ft.colors.TRANSPARENT),
        shadow=ft.BoxShadow(
            blur_radius=8,
            spread_radius=1,
            color="#d0d0d0",
        ),
        border_radius=ft.border_radius.all(8),  # Rounded corners
    )

    # Окно для выбора файла
    row1 = ft.Container(
        content=ft.Text("Выберите файл"),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.BLUE_100,
        border_radius=15,
        padding=10,
        shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, color=ft.colors.BLUE_GREY_100),
        expand=True,
    )


    def pick_files_result(e: ft.FilePickerResultEvent):
        nonlocal selected_file, original_file
        if e.files and len(e.files) > 0:
            selected_file = e.files[0].path
            original_file = selected_file
            row1.content = update_video_player(selected_file)
            column_2.content = sound_funcs
            update_cut_slider(selected_file)
        else:
            row1.content = ft.Text("Файл не выбран")
        page.update()

    def save(e):
        print("saving file")
        if e.path:
            try:
                if selected_file:
                    save_result(selected_file, e.path)
                    print(f"Selected file save to {e.path}")
                else:
                    print("No selected file")
            except Exception as ex:
                print(f"Error saving file {ex}")
        else:
            print("Save canceled")






    # Функции обработки
    # def compress_file_sound(e):
    #     nonlocal selected_file
    #     thresh, ratio = -threshold_slider.value, float(ratio_slider.value)
    #     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"{get_file_extension(selected_file)}")
    #     temp_file.close()
    #     result = apply_compression(load_audio(selected_file, get_file_type(selected_file)), thresh, ratio)
    #     save_or_replace_audio(
    #         selected_file,
    #         result,
    #         get_file_type(selected_file),
    #         temp_file.name
    #     )
    #     print("file saved")
    #     selected_file = temp_file.name
    #     row1.content = update_video_player(selected_file)
    #     sound_funcs.value = None
    #     row2.content = ft.Text("Выберите функцию для обработки")
    #     page.update()

    def compress_file_sound(e):
        nonlocal selected_file
        import requests
        url = "http://127.0.0.1:8000/file/compress"
        files = {'file': open(selected_file, 'rb')}
        data = {'thresh': -threshold_slider.value, 'ratio': ratio_slider.value}

        # Скачиваем обработанное видео
        with requests.post(url, stream=True, files=files, data=data) as r:
            r.raise_for_status()
            with open("downloaded.mp4", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print("All is downloaded!")
        selected_file = "downloaded.mp4"
        row1.content = update_video_player(selected_file)
        sound_funcs.value = None
        row2.content = ft.Text("Выберите функцию для обработки")
        page.update()


    def cut_file(e):
        nonlocal selected_file
        start, end = cut_slider.start_value, cut_slider.end_value

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"{get_file_extension(selected_file)}")
        temp_file.close()

        print(f"Cutting file: {selected_file}, start={start}, end={end}")

        # Сохраняем обработанный файл в новый временный файл
        result = cut_from_file(selected_file, start, end)
        save_file(result, temp_file.name)

        print(f"File saved as {temp_file.name}")
        selected_file = temp_file.name

        # Обновляем видеоплеер
        row1.content = update_video_player(temp_file.name)
        sound_funcs.value = None
        row2.content = ft.Text("Выберите функцию для обработки")

        print(f"Video player updated with {temp_file.name}")


        page.update()
        print("File processing complete.")

    def sound_func_changed(e):
        update_cut_slider(selected_file)
        if e.control.value == "compress":
            row2.content = ft.Column([
                ft.Text("Adjust compression settings", size=18, color=ft.colors.BLACK87),
                ft.Row([threshold_slider, ratio_slider], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([ft.ElevatedButton("Apply compression", on_click=compress_file_sound)], alignment=ft.MainAxisAlignment.CENTER),
            ])
        else:
            row2.content = ft.Column([
                ft.Text("Select range to cut", size=18, color=ft.colors.BLACK87),
                cut_slider,
                ft.ElevatedButton("Cut file", on_click=cut_file, icon=ft.icons.CUT),
            ])
        page.update()

    # Элементы управления
    threshold_slider = ft.Slider(min=0, max=100, divisions=100, value=30, label="{value}", expand=True)
    ratio_slider = ft.Slider(min=1.0, max=10.0, divisions=18, value=4, label="{value}", expand=True)
    cut_slider = ft.RangeSlider(
        min=0,
        start_value=10,
        end_value=20,
        label="{value} sec",
        expand=True
    )

    sound_funcs = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="compress", label="Compression"),
            ft.Radio(value="cut", label="Crop file"),
        ]),
        on_change=sound_func_changed,
    )

    row2 = ft.Container(
        content=ft.Text("Выберите функцию для обработки"),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.LIME_100,
        border_radius=10,
        padding=10,
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=ft.colors.LIME_300),
    )

    column_1 = ft.Column(
        controls=[row1, row2],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
    )

    column_2 = ft.Container(
        content=ft.Text("Select file first"),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.ORANGE_100,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=ft.colors.ORANGE_300),
        expand=True,
    )

    layout = ft.Row(
        controls=[column_1, column_2],
        expand=True,
    )

    column_1.expand = 5
    column_2.expand = 1

    file_picker = ft.FilePicker(on_result=pick_files_result)
    save_picker = ft.FilePicker(on_result=save)
    page.overlay.append(file_picker)
    page.overlay.append(save_picker)

    # Добавляем содержимое на страницу
    page.add(
        ft.Column(
            controls=[top_bar, layout],
            expand=True,
        )
    )

ft.app(target=main)