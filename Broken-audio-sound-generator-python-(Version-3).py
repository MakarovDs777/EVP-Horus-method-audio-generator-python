import tkinter as tk
import pyaudio
import threading
import numpy as np
from collections import deque

# Константы для настройки аудио
CHUNK = 1024  # Количество фреймов за раз
FORMAT = pyaudio.paInt16  # Формат звука
CHANNELS = 1  # Количество каналов
RATE = 44100  # Частота дискретизации

is_recording = False
audio_buffer = deque(maxlen=44100)  # Буфер для аудио (например, 1 секунда звука)

def process_audio(input_device_index):
    global is_recording
    audio = pyaudio.PyAudio()
    
    stream_input = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=input_device_index
    )

    print("Запись аудио... Чтобы остановить запись, нажмите 'Стоп'.")
    is_recording = True

    try:
        while is_recording:
            data = stream_input.read(CHUNK)
            audio_buffer.append(data)  # Запись аудио в буфер

    except Exception as e:
        print(f"Ошибка записи: {e}")

    finally:
        stream_input.stop_stream()
        stream_input.close()
        audio.terminate()

def start_recording():
    global is_recording
    input_device_index = int(input_device_entry.get().strip())
    
    is_recording = True
    
    # Запускаем запись в отдельном потоке
    recording_thread = threading.Thread(target=process_audio, args=(input_device_index,), daemon=True)
    recording_thread.start()

def stop_recording():
    global is_recording
    is_recording = False

def apply_chorus_effect(data):
    """Применение эффекта хорус."""
    audio_data = list(data)  # Преобразуем данные в список байтов

    # Длина заголовка (может варьироваться в зависимости от формата аудио)
    header_length = 100  
    data_to_shuffle = audio_data[header_length:]

    # Перемешивание случайных блоков
    block_size = 64  # Размер блока для перемешивания
    num_blocks = len(data_to_shuffle) // block_size

    # Создание блоков
    blocks = [data_to_shuffle[i * block_size:(i + 1) * block_size] for i in range(num_blocks)]
    
    # Перемешивание блоков
    np.random.shuffle(blocks)

    # Объединение блоков обратно
    shuffled_data = [byte for block in blocks for byte in block]
    
    # Объединяем заголовок и перемешанные данные
    shuffled_byte_data = audio_data[:header_length] + shuffled_data
    
    # Преобразование обратно в байты
    return bytes(shuffled_byte_data)

def play_recorded_audio():
    global audio_buffer
    if len(audio_buffer) == 0:
        print("Нет записанного аудио для воспроизведения.")
        return

    audio = pyaudio.PyAudio()
    stream_output = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True
    )

    # Воспроизведение записанных данных из буфера с эффектом хорус
    for data in audio_buffer:
        chorus_data = apply_chorus_effect(data)  # Применение эффекта хорус
        stream_output.write(chorus_data)

    stream_output.stop_stream()
    stream_output.close()
    audio.terminate()

def list_audio_devices():
    audio = pyaudio.PyAudio()
    device_list = []
    
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        device_list.append(f"{i}: {device_info['name']}")
        
    audio.terminate()
    return device_list

# Создание графического интерфейса
root = tk.Tk()
root.title("Конвертер аудио")
root.geometry("320x220")  # Измененный размер окна

# Поля для ввода индексов устройств
tk.Label(root, text="Индекс записи устройства:").pack()
input_device_entry = tk.Entry(root)
input_device_entry.insert(0, "0")  # Установка значения по умолчанию на 0
input_device_entry.pack()

start_button = tk.Button(root, text="Запись аудио", command=start_recording)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Стоп", command=stop_recording)
stop_button.pack(pady=10)

play_button = tk.Button(root, text="Воспроизвести записанное", command=play_recorded_audio)
play_button.pack(pady=10)

# Заполнение индексов устройств
audio_devices = list_audio_devices()
for device in audio_devices:
    print(device)
    if 'Microphone' in device:  # Проверка на наличие слова 'Microphone'
        input_device_entry.insert(0, device.split(":")[0])  # Устанавливаем значение по умолчанию для микрофона

# Запустить основной цикл интерфейса
root.mainloop()
