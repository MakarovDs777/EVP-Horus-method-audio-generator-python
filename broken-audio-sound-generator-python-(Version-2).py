import tkinter as tk
from tkinter import filedialog
import os
import random

def convert_video_to_bytes(path):
    with open(path, 'rb') as file:
        return file.read()

def bytes_to_video(byte_data, duration_minutes):
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", f"undefined_{duration_minutes}.mp4")
    with open(output_path, 'wb') as file:
        file.write(byte_data)

def select_video_to_bytes():
    file_path = filedialog.askopenfilename(title="Выберите видео файл")
    if file_path:
        byte_data = convert_video_to_bytes(file_path)
        byte_list = list(byte_data)

        key_length = 100  # Длина ключевой части (например, заголовок)
        data_to_shuffle_start = key_length
        data_to_shuffle_end = len(byte_list)

        # Перемешиваем только 10% от остальной части
        to_shuffle = byte_list[data_to_shuffle_start:data_to_shuffle_end]
        num_bytes_to_shuffle = max(1, len(to_shuffle) // 10)  # Перемешиваем 10%
        
        # Выбираем случайные байты для перемешивания
        indices_to_shuffle = random.sample(range(len(to_shuffle)), num_bytes_to_shuffle)
        shuffled_section = [to_shuffle[i] for i in indices_to_shuffle]
        random.shuffle(shuffled_section)

        for i, index in enumerate(indices_to_shuffle):
            to_shuffle[index] = shuffled_section[i]

        # Объединяем перемешанные и неперемешанные байты
        shuffled_byte_data = byte_list[:data_to_shuffle_start] + to_shuffle
        
        # Преобразование обратно в байты
        shuffled_byte_data = bytes(shuffled_byte_data)
        text_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "video_bytes.txt")
        with open(text_file_path, 'w') as text_file:
            text_file.write(str(shuffled_byte_data))
        print(f"Байты видео сохранены в: {text_file_path}")

def select_bytes_to_video():
    file_path = filedialog.askopenfilename(title="Выберите текстовый файл с байтами")
    if file_path:
        with open(file_path, 'r') as text_file:
            byte_data = eval(text_file.read())  # Преобразование строки в байты
        duration_minutes = 10  # Задайте длительность видео в минутах
        bytes_to_video(byte_data, duration_minutes)
        print(f"Видео создано на рабочем столе с именем: undefined_{duration_minutes}.mp4")

def convert_video_to_ef():
    """Комбинированная функция: видео -> байты -> видео"""
    file_path = filedialog.askopenfilename(title="Выберите видео файл для преобразования в ЭГФ")
    if file_path:
        # Шаг 1: Видео в байты
        byte_data = convert_video_to_bytes(file_path)
        byte_list = list(byte_data)

        key_length = 100
        data_to_shuffle_start = key_length
        data_to_shuffle_end = len(byte_list)

        # Перемешиваем 10% данных
        to_shuffle = byte_list[data_to_shuffle_start:data_to_shuffle_end]
        num_bytes_to_shuffle = max(1, len(to_shuffle) // 10)
        indices_to_shuffle = random.sample(range(len(to_shuffle)), num_bytes_to_shuffle)
        shuffled_section = [to_shuffle[i] for i in indices_to_shuffle]
        random.shuffle(shuffled_section)

        for i, index in enumerate(indices_to_shuffle):
            to_shuffle[index] = shuffled_section[i]

        # Объединяем
        byte_list[:data_to_shuffle_start] = byte_list[:data_to_shuffle_start]
        byte_list[data_to_shuffle_start:data_to_shuffle_end] = to_shuffle
        shuffled_byte_data = bytes(byte_list)

        # Шаг 2: байты обратно в видео
        output_path = os.path.join(os.path.expanduser("~"), "Desktop", "evp_video.mp4")
        with open(output_path, 'wb') as f:
            f.write(shuffled_byte_data)
        print(f"Видео в формате ЭГФ сохранено: {output_path}")

# Создание графического интерфейса
root = tk.Tk()
root.title("Конвертер видео")
root.geometry("320x180")  # Размер окна

video_to_bytes_button = tk.Button(root, text="Видео в текст", command=select_video_to_bytes)
video_to_bytes_button.pack(pady=10)

bytes_to_video_button = tk.Button(root, text="Текст в видео", command=select_bytes_to_video)
bytes_to_video_button.pack(pady=10)

# Новая кнопка для "превращения видео в ЭГФ"
convert_to_ef_button = tk.Button(root, text="Превратить видео в ЭГФ", command=convert_video_to_ef)
convert_to_ef_button.pack(pady=10)

# Запуск интерфейса
root.mainloop()
