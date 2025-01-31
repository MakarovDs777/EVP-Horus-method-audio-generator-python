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
        
        # Преобразуем байты в список
        byte_list = list(byte_data)

        # Длина заголовка (может варьироваться в зависимости от формата видео)
        header_length = 100  
        
        # Идентифицируем часть данных, которую можно перемешать
        data_to_shuffle = byte_list[header_length:]

        # Перемешиваем случайные блоки
        block_size = 64  # Размер блока для перемешивания
        num_blocks = len(data_to_shuffle) // block_size

        # Создание блоков
        blocks = [data_to_shuffle[i * block_size:(i + 1) * block_size] for i in range(num_blocks)]
        
        # Перемешивание блоков
        random.shuffle(blocks)

        # Объединение блоков обратно
        shuffled_data = [byte for block in blocks for byte in block]
        
        # Объединяем заголовок и перемешанные данные
        shuffled_byte_data = byte_list[:header_length] + shuffled_data
        
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

# Создание графического интерфейса
root = tk.Tk()
root.title("Конвертер видео")
root.geometry("320x120")  # Установка размера окна

video_to_bytes_button = tk.Button(root, text="Видео в текст", command=select_video_to_bytes)
video_to_bytes_button.pack(pady=10)

bytes_to_video_button = tk.Button(root, text="Текст в видео", command=select_bytes_to_video)
bytes_to_video_button.pack(pady=10)

# Запустить основной цикл интерфейса
root.mainloop()
