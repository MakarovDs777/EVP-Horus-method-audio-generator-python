import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random

# Для работы с аудио
def convert_audio_to_bytes(path):
    with open(path, 'rb') as file:
        return file.read()

def save_bytes_as_audio(byte_data, output_path):
    with open(output_path, 'wb') as f:
        f.write(byte_data)

# Глобальный список выбранных аудио
selected_audios = []

# Создаем интерфейс
root = tk.Tk()
root.title("Конвертер аудио в ЭГФ")
root.geometry("600x500")

# Listbox для отображения выбранных аудио
audio_listbox = tk.Listbox(root, width=60, height=10)
audio_listbox.pack(pady=10)

# Поле для ввода длительности
duration_frame = tk.Frame(root)
duration_frame.pack(pady=5)

tk.Label(duration_frame, text="Длительность ЭГФ (мин):").pack(side=tk.LEFT)
duration_entry = tk.Entry(duration_frame, width=5)
duration_entry.insert(0, "2")  # по умолчанию 2 минуты
duration_entry.pack(side=tk.LEFT)

def select_audio():
    file_path = filedialog.askopenfilename(
        title="Выберите аудио файл",
        filetypes=[("Audio files", "*.mp3;*.wav;*.ogg")]
    )
    if file_path:
        selected_audios.append(file_path)
        audio_listbox.insert(tk.END, file_path)

def create_eghf_from_audios():
    if not selected_audios:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите хотя бы один аудио файл.")
        return
    
    try:
        duration_minutes = float(duration_entry.get())
        if duration_minutes <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректную длительность (>0).")
        return

    target_duration_ms = int(duration_minutes * 60 * 1000)  # переводим в миллисекунды
    header_length = 100
    block_size = 64
    combined_bytes = bytearray()

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

    # Сохраняем объединенный файл
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", "evp_audio.wav")
    save_bytes_as_audio(combined_bytes, output_path)
    messagebox.showinfo("Готово", f"ЭГФ создан: {output_path}")

# Кнопки
tk.Button(root, text="Выбрать аудио", command=select_audio).pack(pady=5)
tk.Button(root, text="Превратить в ЭГФ сразу", command=create_eghf_from_audios).pack(pady=5)

root.mainloop()
