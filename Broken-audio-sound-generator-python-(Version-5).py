import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from pydub import AudioSegment

# Глобальный список выбранных аудио
selected_audios = []

def convert_audio_to_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def save_bytes_as_audio(byte_data, output_path):
    with open(output_path, 'wb') as f:
        f.write(byte_data)

def create_eghf():
    # Получаем длину в секундах из поля ввода
    duration_sec = int(entry_duration.get())
    combined_bytes = bytearray()
    header_length = 100
    block_size = 64

    for audio_path in selected_audios:
        byte_data = convert_audio_to_bytes(audio_path)
        byte_list = list(byte_data)
        data_to_shuffle = byte_list[header_length:]
        num_blocks = len(data_to_shuffle) // block_size
        blocks = [data_to_shuffle[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
        random.shuffle(blocks)
        shuffled_data = [byte for block in blocks for byte in block]
        byte_list[header_length:] = shuffled_data
        shuffled_byte_data = bytes(byte_list)
        combined_bytes.extend(shuffled_byte_data)

    # Обрезаем итоговый байтовый поток до нужной длины
    sample_rate = 44100
    channels = 2
    bytes_per_sample = 2
    total_bytes = int((duration_sec * sample_rate * channels * bytes_per_sample))
    trimmed_bytes = combined_bytes[:total_bytes]

    # Создаем аудио из байтов
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", "evp_audio.mp4")
    save_bytes_as_audio(trimmed_bytes, output_path)
    messagebox.showinfo("Готово", f"ЭГФ сохранен: {output_path}")

# Создаем интерфейс
root = tk.Tk()
root.title("Создание ЭГФ из аудио")
root.geometry("500x400")

# Поле для ввода длины
tk.Label(root, text="Длина ЭГФ (сек):").pack(pady=5)
entry_duration = tk.Entry(root)
entry_duration.pack(pady=5)
entry_duration.insert(0, "60")  # по умолчанию 60 секунд

# Область для списка выбранных файлов
listbox = tk.Listbox(root, width=60)
listbox.pack(pady=10)

# Кнопка выбора файла
def select_audio():
    global selected_audios
    file_path = filedialog.askopenfilename(
        title="Выберите аудио файл",
        filetypes=[("Audio files", ".mp3;.wav;*.ogg")]
    )
    if file_path:
        selected_audios.append(file_path)
        listbox.insert(tk.END, file_path)

tk.Button(root, text="Выбрать аудио", command=select_audio).pack(pady=5)

# --- Кнопка "Удалить выбранное" ---
def remove_selected():
    global selected_audios
    selected_indices = listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Предупреждение", "Выберите файл для удаления.")
        return
    for index in reversed(selected_indices):
        listbox.delete(index)
        del selected_audios[index]

tk.Button(root, text="Удалить выбранное", command=remove_selected).pack(pady=5)

# --- Кнопка "Создать ЭГФ" ---
tk.Button(root, text="Создать ЭГФ", command=create_eghf).pack(pady=5)

root.mainloop()
