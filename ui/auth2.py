import os
import tempfile

from pydub import AudioSegment

from ..src.file.router import upload_file
from ..src.file.sound_func import cut_from_file, save_file, apply_compression, load_audio, get_file_type, save_or_replace_audio, get_file_extension, save_result
import requests
import flet as ft

from src.dbmodels import File
from util.repositories.db_repos import SQLAlchemyPostgresqlDataclassRepository

LOGIN_URL = "http://127.0.0.1:8000/auth/jwt/login"
PROTECTED_ROUTE_URL = "http://127.0.0.1:8000//protected-route"
REGISTER_ROUTER = "http://127.0.0.1:8000/auth/register"
API_URL = "http://127.0.0.1:8000"
logged_data = []


def main(page: ft.Page):

    page.title = "Sound Processing Platform"
    page.scroll = "auto"

    # Градиентный фон
    page.bgcolor = ft.LinearGradient(
        begin=ft.alignment.top_center,
        end=ft.alignment.bottom_center,
        colors=["#4A90E2", "#007AFF"]
    )

    # Заголовок страницы
    header = ft.Text(
        "Добро пожаловать в Sound Processing Platform",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE,
        text_align=ft.TextAlign.CENTER
    )

    # Подзаголовок
    subtitle = ft.Text(
        "Загружайте, обрабатывайте и храните аудио и видео файлы легко и удобно.",
        size=20,
        color=ft.colors.GREY_300,
        text_align=ft.TextAlign.CENTER
    )

    # Секции с функциями
    features = [
        {
            "icon": ft.icons.FILE_UPLOAD,
            "title": "Добавление файлов",
            "description": "Загружайте аудио и видео файлы для дальнейшей обработки."
        },
        {
            "icon": ft.icons.CLOUD,
            "title": "Хранение в облаке",
            "description": "Сохраняйте файлы в облачном хранилище Selectel для удобного доступа."
        },
        {
            "icon": ft.icons.COMPRESS,
            "title": "Компрессия звука",
            "description": "Нормализуйте громкость для комфортного звучания."
        },
        {
            "icon": ft.icons.CONTENT_CUT,
            "title": "Обрезка файлов",
            "description": "Обрезайте аудио и видео файлы по нужной длине."
        }
    ]

    # Карточки функций
    feature_cards = []
    for feature in features:
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(feature["icon"], size=60, color=ft.colors.WHITE),
                        ft.Text(feature["title"], size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(feature["description"], size=16, color=ft.colors.GREY_300, text_align=ft.TextAlign.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=20,
                alignment=ft.alignment.center,
                bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                border_radius=15,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                    offset=ft.Offset(0, 5)
                )
            ),
            elevation=0
        )
        feature_cards.append(ft.Container(content=card, width=280, height=240, padding=10))

    # Функции для перехода на страницы логина и регистрации
    def go_to_login(e):
        page.clean()
        login_page(page)
        page.update()

    def go_to_register(e):
        page.clean()
        registration_page(page)
        page.update()

    # Кнопки для перехода
    login_button = ft.ElevatedButton(
        text="Войти",
        icon=ft.icons.LOGIN,
        style=ft.ButtonStyle(
            bgcolor={"": "#4CAF50"},
            color={"": ft.colors.WHITE},
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=5
        ),
        on_click=go_to_login
    )

    register_button = ft.ElevatedButton(
        text="Зарегистрироваться",
        icon=ft.icons.PERSON_ADD,
        style=ft.ButtonStyle(
            bgcolor={"": "#FF9800"},
            color={"": ft.colors.WHITE},
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=5
        ),
        on_click=go_to_register
    )

    # Размещение кнопок
    button_row = ft.Row([login_button, register_button], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    # Главный макет страницы
    page.add(
        ft.Column(
            [
                ft.Container(header, alignment=ft.alignment.center, padding=20),
                ft.Container(subtitle, alignment=ft.alignment.center, padding=10, width=600),
                ft.Row(
                    feature_cards,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Container(button_row, alignment=ft.alignment.center, padding=40)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )



def login_page(page: ft.Page):
    page.title = "Login Page"
    page.bgcolor = ft.colors.BLACK  # Темный фон страницы
    page.padding = 40  # Отступы по краям страницы

    # Поля ввода для логина и пароля
    username_input = ft.TextField(
        label="Email",
        autofocus=True,
        border_color=ft.colors.GREY_700,
        border_radius=10,
        width=300,
        prefix_icon=ft.icons.EMAIL,
        color=ft.colors.WHITE,  # Цвет текста
        label_style=ft.TextStyle(color=ft.colors.GREY_500),  # Цвет подсказки
        cursor_color=ft.colors.WHITE
    )

    password_input = ft.TextField(
        label="Password",
        password=True,
        border_color=ft.colors.GREY_700,
        border_radius=10,
        width=300,
        prefix_icon=ft.icons.LOCK,
        color=ft.colors.WHITE,  # Цвет текста
        label_style=ft.TextStyle(color=ft.colors.GREY_500),  # Цвет подсказки
        cursor_color=ft.colors.WHITE
    )

    # Текст для отображения статуса логина
    status_text = ft.Text(size=16, color=ft.colors.RED_400, weight=ft.FontWeight.BOLD)


    def go_to_files(e):
        page.clean()
        files_page(page, logged_data[0])
        page.update()

    def login_clicked(e):
        response = requests.post(
            LOGIN_URL,
            data={
                "username": username_input.value,
                "password": password_input.value
            }
        )
        my_cookies = requests.utils.dict_from_cookiejar(response.cookies)
        logged_data.append(my_cookies)

        if response.status_code == 200 or response.status_code == 204:
            status_text.value = "Авторизация успешна"
            print(type(logged_data[0]))
            status_text.color = ft.colors.GREEN_400
            go_to_files(e)

        else:
            status_text.value = "Неверный логин или пароль"
            status_text.color = ft.colors.RED_400

        page.update()

    # Кнопка для входа
    login_button = ft.ElevatedButton(
        text="Войти",
        on_click=login_clicked,
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        width=300,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=5,
        )
    )

    # Заголовок страницы
    title_text = ft.Text(
        "Welcome! Please Log In",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE,
    )

    # Создание контейнера для формы логина
    login_container = ft.Container(
        content=ft.Column(
            [
                title_text,
                username_input,
                password_input,
                login_button,
                status_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        padding=30,
        width=400,
        bgcolor=ft.colors.GREY_900,  # Темный фон для контейнера
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.GREY_700),
    )

    # Размещаем контейнер по центру страницы
    page.add(
        ft.Row(
            [login_container],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
    )




def registration_page(page: ft.Page):
    page.title = "Registration Page"
    page.bgcolor = ft.colors.BLACK  # Темная тема для страницы
    page.padding = 40

    # Поля ввода для регистрации
    email_input = ft.TextField(
        label="Email",
        border_color=ft.colors.GREY_700,
        border_radius=10,
        width=300,
        color=ft.colors.WHITE,
        label_style=ft.TextStyle(color=ft.colors.GREY_500),
        cursor_color=ft.colors.WHITE,
        prefix_icon=ft.icons.EMAIL
    )

    password_input = ft.TextField(
        label="Password",
        password=True,
        border_color=ft.colors.GREY_700,
        border_radius=10,
        width=300,
        color=ft.colors.WHITE,
        label_style=ft.TextStyle(color=ft.colors.GREY_500),
        cursor_color=ft.colors.WHITE,
        prefix_icon=ft.icons.LOCK
    )

    name_input = ft.TextField(
        label="Name",
        border_color=ft.colors.GREY_700,
        border_radius=10,
        width=300,
        color=ft.colors.WHITE,
        label_style=ft.TextStyle(color=ft.colors.GREY_500),
        cursor_color=ft.colors.WHITE,
        prefix_icon=ft.icons.PERSON
    )

    # Текст для отображения статуса регистрации
    status_text = ft.Text(size=16, color=ft.colors.RED_400, weight=ft.FontWeight.BOLD)

    def go_to_login(e):
        page.clean()
        login_page(page)
        page.update()

    def register_clicked(e):
        response = requests.post(
            REGISTER_ROUTER,
            json={
                "email": email_input.value,
                "password": password_input.value,
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "name": name_input.value,
                "role_id": 2
            }
        )

        if response.status_code == 201:
            status_text.value = "Регистрация успешна!"
            status_text.color = ft.colors.GREEN_400
            go_to_login(e)
        else:
            status_text.value = f"Ошибка регистрации: {response.text}"
            status_text.color = ft.colors.RED_400

        page.update()

    # Кнопка для регистрации
    register_button = ft.ElevatedButton(
        text="Зарегистрироваться",
        on_click=register_clicked,
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        width=300,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=5,
        )
    )

    # Заголовок страницы
    title_text = ft.Text(
        "Create a New Account",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE,
    )

    alreeady_authorized = ft.TextButton(
        "Already registered?",
        on_click=go_to_login
    )

    # Контейнер для формы регистрации
    register_container = ft.Container(
        content=ft.Column(
            [
                title_text,
                email_input,
                password_input,
                name_input,
                register_button,
                status_text,
                alreeady_authorized

            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        padding=30,
        width=400,
        bgcolor=ft.colors.GREY_900,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.GREY_700),
    )

    # Центрирование формы на странице
    page.add(
        ft.Row(
            [register_container],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
    )

file_repo = SQLAlchemyPostgresqlDataclassRepository(File)

def load_files_from_repo(status):
    try:
        if status == "all":
            files = file_repo.list_name()
        else:
            files = file_repo.list_files_by_status(status)
            # Извлекаем только имена файлов из результата запроса
            files = [file['name'] for file in files]
        return files
    except Exception as ex:
        print(f"Error fetching files: {str(ex)}")
        return []

def files_page(page: ft.Page, cookies: dict):
    page.title = "File Management"
    page.bgcolor = "linear-gradient(to bottom, #1c1c1c, #3b3b3b)"
    page.padding = 40

    # Текст для отображения статуса операций
    status_text = ft.Text(size=16, color=ft.colors.RED_400, weight=ft.FontWeight.BOLD)
    selected_status = 1

    # Анимация загрузки файла
    loading_gif = ft.Image(src="https://i.gifer.com/ZZ5H.gif", width=50, height=50)
    loading_text = ft.Text("\ud83d\udee0\ufe0f File is uploading...", color=ft.colors.YELLOW_400)
    loading_container = ft.Row([loading_gif, loading_text], visible=False, alignment=ft.MainAxisAlignment.CENTER)

    # Список файлов
    files_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def go_to_proc(e, f_name):
        page.clean()
        sound_proc(page, f_name)
        page.update()

    # Функция для загрузки списка файлов из репозитория по статусу
    def load_files(status="all"):
        files_list_view.controls.clear()
        try:
            files = load_files_from_repo(status)
            if not files:
                files_list_view.controls.append(
                    ft.Text("\ud83d\udeab No files found", color=ft.colors.GREY_400)
                )
            else:
                for file_name in files:
                    files_list_view.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Text(file_name, color=ft.colors.WHITE, size=14),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE_OUTLINE,
                                            tooltip="Delete file",
                                            on_click=lambda e, fname=file_name: delete_file(fname),
                                            icon_color=ft.colors.RED_400
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN

                                ),
                                on_click=lambda e, fname=file_name: go_to_proc(e, fname),
                                padding=10,
                                bgcolor=ft.colors.GREY_900,
                                border_radius=10
                            )
                        )
                    )

        except Exception as ex:
            status_text.value = f"\ud83d\udeab Error: {str(ex)}"
            status_text.color = ft.colors.RED_400
        page.update()

    status_dialog = None

    def show_status_dialog():
        global status_dialog
        status_dialog = ft.AlertDialog(
            title=ft.Text("Select file status"),
            content=ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value='1', label="Added"),  # Передаем id 1
                    ft.Radio(value='2', label="Modified"),  # Передаем id 2
                    ft.Radio(value='3', label="Completed"),  # Передаем id 3
                ]),
                value='1',  # Устанавливаем по умолчанию выбранный статус как "Added" (id = 1)
                on_change=status_func_changed
            ),
            actions=[ft.TextButton("Confirm", on_click=confirm_status)]
        )
        page.add(status_dialog)
        status_dialog.open = True
        page.update()

    # Обработчик выбора статуса
    def status_func_changed(e):
        global selected_status
        selected_status = int(e.control.value)  # Сохраняем id статуса
        print(f"Selected status id: {selected_status}")

    # Подтверждение выбора статуса и загрузка файла
    def confirm_status(e):
        global status_dialog

        status_dialog.open = False  # Закрыть диалоговое окно
        page.update()
        if selected_file:
            handle_file_pick(selected_status)
            print(selected_status)
        else:
            status_text.value = "\ud83d\udeab No file selected."
            status_text.color = ft.colors.RED_400
            page.update()

    # Функция загрузки файла на сервер с передачей статуса
    def handle_file_pick(status):
        global selected_file  # Используем глобальную переменную с выбранным файлом
        file = selected_file  # Получаем выбранный файл
        file_name = file.name

        try:
            # Показать анимацию загрузки
            loading_container.visible = True
            page.update()

            print("stat:", status)
            # Загрузить файл на сервер с передачей статуса через query параметр
            files = {'file': open(file.path, 'rb')}
            response = requests.post(f"{API_URL}/files/uploadfile?path={file.path}&status={status}", files=files,
                                     cookies=cookies)

            # Обработка ответа
            if response.status_code == 200:
                status_text.value = f"\ud83c\udf1f File '{file_name}' uploaded successfully!"
                status_text.color = ft.colors.GREEN_400
            else:
                status_text.value = f"\ud83d\udeab Error: {response.text}"
                status_text.color = ft.colors.RED_400

            loading_container.visible = False

        except Exception as ex:
            loading_container.visible = False
            status_text.value = f"\ud83d\udeab Error: {str(ex)}"
            status_text.color = ft.colors.RED_400

        load_files()  # Перезагружаем список файлов
        page.update()

    # Функция для выбора файла
    def handle_file_pick_2(e):
        global selected_file
        file_picker.pick_files(dialog_title="Select file", allowed_extensions=["mp3", "wav", "mp4"])  # Показываем диалог для выбора файла

    # Функция для обработки результата выбора файла
    def on_file_picker_result(e: ft.FilePickerResultEvent):
        global selected_file
        if e.files:
            selected_file = e.files[0]  # Сохраняем выбранный файл
            show_status_dialog()  # Показываем диалог для выбора статуса
        else:
            status_text.value = "\ud83d\udeab No file selected."
            status_text.color = ft.colors.RED_400
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picker_result)

    # Функция для удаления файла
    def delete_file(filename):
        response = requests.delete(f"{API_URL}/files/files/{filename}", cookies=cookies)
        if response.status_code == 200:
            status_text.value = f"\ud83d\udc4d File '{filename}' deleted successfully!"
            status_text.color = ft.colors.GREEN_400
        else:
            status_text.value = f"\ud83d\udeab Error: {response.text}"
            status_text.color = ft.colors.RED_400
        load_files()
        page.update()

    # Кнопка для загрузки нового файла
    upload_button = ft.ElevatedButton(
        text="Upload File",
        icon=ft.icons.UPLOAD_FILE,
        on_click=handle_file_pick_2,
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # Выпадающий список для выбора статуса
    status_dropdown = ft.Dropdown(
        label="Select file status",
        options=[
            ft.dropdown.Option("all"),
            ft.dropdown.Option("added"),
            ft.dropdown.Option("modified"),
            ft.dropdown.Option("completed")
        ],
        value="all",
        on_change=lambda e: load_files(e.control.value)
    )

    # Добавляем элементы на страницу
    page.add(
        ft.Column(
            [
                ft.Text("\ud83d\udcc2 File Management", size=24, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                ft.Row([upload_button, status_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                loading_container,
                files_list_view,
                status_text,
                file_picker
            ],
            spacing=20,
            expand=True
        )
    )

    # Загрузка списка файлов при инициализации страницы
    load_files()

def sound_proc(page: ft.Page, filename):
    page.title = "Audio/Video Editor"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.colors.GREY_700
    page.padding = 20
    processing_indicator = ft.ProgressRing(visible=False, width=50, height=50)
    processing_gif = ft.Image(
        src="D:\GraduationProject\SoundNormalization1\dance.gif",
        width=50,
        height=50,
        visible=False  # Изначально скрыт
    )

    selected_file = None
    original_file = None
    video = None

    def go_to_files(e):
        page.clean()
        files_page(page, logged_data[0])
        page.update()

    def back_to_original(e):
        nonlocal selected_file
        selected_file = original_file
        row1.content = update_video_player(selected_file)
        sound_funcs.value = None
        row2.content = ft.Text("Выберите функцию для обработки")
        page.update()

    def update_cut_slider(file_path):
        cut_slider.max = round(len(AudioSegment.from_file(file_path)) / 1000, 1)
        cut_slider.divisions = len(AudioSegment.from_file(file_path)) // 100

    def update_video_player(file_path):
        nonlocal video
        try:
            video = ft.Video(
                expand=True,
                playlist=[ft.VideoMedia(file_path)],
                playlist_mode=ft.PlaylistMode.LOOP,
                fill_color=ft.colors.GREY_800,  # Replaced with gray color
                aspect_ratio=16 / 9,
                volume=100,
                autoplay=True,
            )
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
                        ),
                        ft.IconButton(
                            icon=ft.icons.FILE_COPY,
                            tooltip="Go to Files",
                            on_click=go_to_files
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(
                    "Sound Normalization App",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE38,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor="linear-gradient(to right, #333333, #111111)",  # Soft gray gradient
        padding=10,
        height=60,
        border=ft.border.all(0, ft.colors.TRANSPARENT),
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=2, color="#444444"),
        border_radius=ft.border_radius.all(8),  # Rounded corners
    )

    row1 = ft.Container(
        content=ft.Text("Выберите файл"),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.GREY_600,
        border_radius=15,
        padding=15,
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=3, color=ft.colors.GREY_600),
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
        if e.path:
            try:
                if selected_file:
                    save_result(selected_file, e.path)
                    print(f"File saved to {e.path}")
                else:
                    print("No file selected")
            except Exception as ex:
                print(f"Error saving file: {ex}")
        else:
            print("Save canceled")

    def compress_file_sound(e):
        nonlocal selected_file
        import requests

        # Показать GIF-анимацию
        processing_gif.visible = True
        row2.content.controls[0] = ft.Text("Processing...")
        page.update()

        try:
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
        except Exception as ex:
            print(f"Error during compression: {ex}")
            row2.content = ft.Text("Error during processing")
        finally:
            # Скрыть GIF после завершения обработки
            processing_gif.visible = False
            page.update()

    def sound_func_changed(e):
        update_cut_slider(selected_file)
        if e.control.value == "compress":
            row2.content = ft.Column([
                ft.Text("Adjust compression settings", size=18, color=ft.colors.WHITE38),
                ft.Row([threshold_slider, ratio_slider], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([ft.ElevatedButton("Apply compression", on_click=compress_file_sound)], alignment=ft.MainAxisAlignment.CENTER),
            ])
        else:
            row2.content = ft.Column([
                ft.Text("Select range to cut", size=18, color=ft.colors.WHITE38),
                cut_slider,
                ft.ElevatedButton("Cut file", on_click=cut_file, icon=ft.icons.CUT),
            ])
        page.update()

    threshold_slider = ft.Slider(min=0, max=100, divisions=100, value=30, label="{value}", expand=True)
    ratio_slider = ft.Slider(min=1.0, max=10.0, divisions=18, value=4, label="{value}", expand=True)
    cut_slider = ft.RangeSlider(min=0, start_value=10, end_value=20, label="{value} sec", expand=True)

    sound_funcs = ft.RadioGroup(
        content=ft.Column([ft.Radio(value="compress", label="Compression"), ft.Radio(value="cut", label="Crop file")]),
        on_change=sound_func_changed,
    )

    def cut_file(e):
        nonlocal selected_file
        start, end = cut_slider.start_value, cut_slider.end_value
        processing_gif.visible = True
        row2.content.controls[0] = ft.Text("Processing...")
        page.update()  # Немедленно обновляем страницу для отображения сообщения об обработке

        try:
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
            row2.content.controls[0] = ft.Text("Processing complete!")

            print(f"Video player updated with {temp_file.name}")
        except Exception as ex:
            print(f"Error during cutting: {ex}")
            row2.content.controls[0] = ft.Text("Error during processing")
        finally:
            # Скрыть GIF после завершения обработки
            processing_gif.visible = False
            page.update()

    row2 = ft.Container(
        content=ft.Column([
            ft.Text("Выберите функцию для обработки"),
            processing_gif
        ], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.GREY_700,
        border_radius=10,
        padding=10,
        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=ft.colors.GREY_600),
    )

    column_1 = ft.Column(
        controls=[row1, row2],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
    )

    column_2 = ft.Container(
        content=ft.Text("Select file first"),
        alignment=ft.alignment.center,
        bgcolor=ft.colors.GREY_700,  # Replaced with gray color
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=ft.colors.GREY_600),
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

    page.add(
        ft.Column(
            controls=[top_bar, layout],
            expand=True,
        )
    )

    file_path = file_repo.get_path(filename)
    selected_file = file_path
    original_file = file_path
    row1.content = update_video_player(file_path)
    column_2.content = sound_funcs
    page.update()




# Запуск приложения
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

