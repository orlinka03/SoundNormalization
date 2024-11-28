import flet as ft
from pydub import AudioSegment

from src.file.sound_func import cut_from_file, save_file, apply_compression, load_audio, get_file_type


def main(page: ft.Page):
    selected_file = None
    row1 = ft.Container(  # Инициализация `row1`
        content=ft.Text("Выберите файл"),
        alignment=ft.alignment.center,
        bgcolor="lightblue",
        expand=True,
    )

    def pick_files_result(e: ft.FilePickerResultEvent):
        nonlocal selected_file
        if e.files and len(e.files) > 0:
            selected_file = e.files[0].path
            # Обновляем содержимое `row1` на видеопроигрыватель
            row1.content = ft.Video(
                expand=True,
                playlist=[ft.VideoMedia(selected_file)],
                playlist_mode=ft.PlaylistMode.LOOP,
                fill_color=ft.colors.BLUE_400,
                aspect_ratio=16 / 9,
                volume=100,
                autoplay=True,  # Автоматически запускает воспроизведение
                filter_quality=ft.FilterQuality.HIGH)
            column_2.content = sound_funcs
            cut_slider.max = round(len(AudioSegment.from_file(selected_file))/1000, 1)
            cut_slider.divisions = len(AudioSegment.from_file(selected_file))//100
        else:
            row1.content = ft.Text("Файл не выбран")

        page.update()

    # Создаём FilePicker
    file_picker = ft.FilePicker(on_result=pick_files_result)

    # Меню-бар
    menubar = ft.MenuBar(
        controls=[
            ft.SubmenuButton(
                content=ft.Text("File"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("Open"),
                        on_click=lambda e: file_picker.pick_files(
                            allowed_extensions=["mp3", "wav", "mp4"],
                            dialog_title="Выберите файл для обработки"
                        ),
                    ),
                ],
            ),
        ],
    )

    threshold_slider = ft.Slider(
        min=0,
        max=100,
        divisions=100,
        value=30,
        label="{value}",
        expand=True
    )

    ratio_slider = ft.Slider(
        min=1.0,  # Минимальное значение (например, коэффициент 1 - без сжатия)
        max=10.0,  # Максимальное значение (например, коэффициент сжатия до 10)
        divisions=18,
        round=1,
        value=1,  # Начальное значение
        label="{value}",
        expand=True
    )

    cut_slider = ft.RangeSlider(
        min=0,
        start_value=10,
        end_value=20,
        inactive_color=ft.colors.GREEN_300,
        active_color=ft.colors.GREEN_700,
        overlay_color=ft.colors.GREEN_100,
        label="{value} sec",
        expand=True
    )

    def compress_file_sound(e):
        thresh, ratio = -threshold_slider.value, float(ratio_slider.value)
        print(thresh, ratio)
        print(get_file_type(selected_file))
        save_file(apply_compression(load_audio(selected_file, get_file_type(selected_file)), thresh, ratio))
        print("file saved")

    def cut_file(e):
        start, end = cut_slider.start_value, cut_slider.end_value
        print(start, end)
        save_file(cut_from_file(selected_file, start, end))
        print("Файл сохранен")


    def sound_func_changed(e):
        if e.control.value == "compress":
            row2.content = ft.Column([ft.Row([ft.Text("Choose thresh and ratio for compression", size=16, color=ft.colors.BLACK87)]),
                            ft.Row([threshold_slider, ratio_slider], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            ft.Row([ft.ElevatedButton("Apply compression", on_click=compress_file_sound)], alignment=ft.MainAxisAlignment.CENTER)])
        else:
            row2.content = ft.Column([ft.Row([ft.Text("Choose time for cutting file", size=16, color=ft.colors.BLACK87)]),
                            ft.Row([cut_slider], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([ft.ElevatedButton("Cut file", on_click=cut_file)], alignment=ft.MainAxisAlignment.CENTER)])
            print(cut_slider.max)
        page.update()

    sound_funcs = ft.RadioGroup(content=ft.Column([
        ft.Radio(value='compress', label='Компрессия'),
        ft.Radio(value='cut', label='Обрезание')
    ]), on_change=sound_func_changed)

    # Вторая строка в первой колонке
    row2 = ft.Container(
        content=ft.Text("Выберите функцию для обработки"),
        alignment=ft.alignment.center,
        bgcolor="lightgreen",
    )

    # Первая колонка (содержит две строки)
    column_1 = ft.Column(
        controls=[row1, row2],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
    )

    row1.expand = 3
    row2.expand = 1

    # Вторая колонка
    column_2 = ft.Container(
        content=ft.Text("Select file first"),
        alignment=ft.alignment.center,
        bgcolor="lightcoral",
        expand=True
    )

    # Главный ряд (два столбца)
    layout = ft.Row(
        controls=[column_1, column_2],
        expand=True
    )

    column_1.expand = 5
    column_2.expand = 1

    page.overlay.append(file_picker)

    # Установка макета страницы
    page.add(
        ft.Column(
            controls=[
                menubar,  # Меню-бар сверху
                layout,  # Основной контент
            ],
            expand=True,
        )
    )



ft.app(target=main)
