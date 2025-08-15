import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from moviepy.editor import VideoFileClip

# Глобальный список выбранных файлов
selected_files = []

# -------------------------
# Вспомогательные функции
# -------------------------

def convert_video_to_bytes(path):
    """Читает файл и возвращает его байты."""
    with open(path, 'rb') as file:
        return file.read()

def bytes_to_video(byte_data, duration_minutes):
    """Сохраняет байты как mp4 на рабочий стол с именем undefined_{duration_minutes}.mp4"""
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", f"undefined_{duration_minutes}.mp4")
    with open(output_path, 'wb') as file:
        file.write(byte_data)
    return output_path

def extract_audio_from_video(video_path):
    """Извлекает аудио дорожку из видео и возвращает путь к временному mp3 файлу."""
    try:
        clip = VideoFileClip(video_path)
        audio_path = os.path.splitext(video_path)[0] + "_temp_audio.mp3"
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
        clip.close()
        return audio_path
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось извлечь аудио из видео: {e}")
        return None

def convert_audio_to_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def save_bytes_as_audio(byte_data, output_path):
    with open(output_path, 'wb') as f:
        f.write(byte_data)

# -------------------------
# Основные операции
# -------------------------

def select_files():
    """Выбрать несколько файлов и добавить в список."""
    global selected_files
    file_paths = filedialog.askopenfilenames(
        title="Выберите файлы",
        filetypes=[("Аудио и видео файлы", "*.mp3;*.wav;*.ogg;*.mp4;*.avi;*.mov;*.mkv"),
                   ("Все файлы", "*.*")]
    )
    if file_paths:
        for path in file_paths:
            if path not in selected_files:
                selected_files.append(path)
                listbox.insert(tk.END, path)

def remove_selected():
    """Удалить выделенные элементы из списка."""
    global selected_files
    selected_indices = listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Предупреждение", "Выберите файл(ы) для удаления.")
        return
    for index in reversed(selected_indices):
        listbox.delete(index)
        del selected_files[index]

def select_videos_to_bytes_multiple():
    """
    Обрабатывает все файлы из selected_files: для каждого файла
    читаем байты, частично перемешиваем (не трогаем header) и
    добавляем в общий поток байтов. Сохраняем один файл на Desktop.
    """
    if not selected_files:
        messagebox.showwarning("Предупреждение", "Сначала выберите файлы.")
        return

    try:
        combined_bytes = bytearray()
        key_length = 100  # не трогаем первые 100 байт в каждом файле

        for file_path in selected_files:
            # Берём исходные байты файла (видео или аудио — просто читаем файл)
            try:
                byte_data = convert_video_to_bytes(file_path)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось прочитать {file_path}: {e}")
                continue

            byte_list = list(byte_data)
            if len(byte_list) > key_length + 1:
                data_to_shuffle_start = key_length
                data_to_shuffle_end = len(byte_list)
                to_shuffle = byte_list[data_to_shuffle_start:data_to_shuffle_end]

                # Перемешиваем 10% оставшихся байтов (но минимум 1)
                num_bytes_to_shuffle = max(1, len(to_shuffle) // 10)
                indices_to_shuffle = random.sample(range(len(to_shuffle)), num_bytes_to_shuffle)

                shuffled_section = [to_shuffle[i] for i in indices_to_shuffle]
                random.shuffle(shuffled_section)
                for i, index in enumerate(indices_to_shuffle):
                    to_shuffle[index] = shuffled_section[i]

                # Собираем обратно
                byte_list[data_to_shuffle_start:data_to_shuffle_end] = to_shuffle

            # Добавляем обработанный файл в общий буфер
            combined_bytes.extend(byte_list)

        # Сохраняем объединённые байты в один бинарный файл на рабочий стол
        output_path = os.path.join(os.path.expanduser("~"), "Desktop", "combined_video_bytes.bin")
        with open(output_path, 'wb') as out_f:
            out_f.write(bytes(combined_bytes))

        messagebox.showinfo("Готово", f"Байты всех выбранных файлов сохранены в: {output_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при обработке файлов: {e}")

def select_bytes_to_video():
    """Выбрать файл с байтами и сохранить как видео (измените duration_minutes при необходимости)."""
    file_path = filedialog.askopenfilename(title="Выберите файл с байтами", filetypes=[("Все файлы", "*.*")])
    if not file_path:
        return
    try:
        with open(file_path, 'rb') as text_file:
            byte_data = text_file.read()
        duration_minutes = 10  # задайте желаемую длительность
        out_path = bytes_to_video(byte_data, duration_minutes)
        messagebox.showinfo("Готово", f"Видео создано: {out_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при создании видео: {e}")

def convert_video_to_ef_single():
    """Обработка одного видео файла: преобразование в ЭГФ (shuffle) и сохранение."""
    file_path = filedialog.askopenfilename(title="Выберите видео файл для преобразования в ЭГФ")
    if not file_path:
        return
    try:
        byte_data = convert_video_to_bytes(file_path)
        byte_list = list(byte_data)
        key_length = 100
        data_to_shuffle_start = key_length
        data_to_shuffle_end = len(byte_list)
        to_shuffle = byte_list[data_to_shuffle_start:data_to_shuffle_end]
        num_bytes_to_shuffle = max(1, len(to_shuffle) // 10)
        indices_to_shuffle = random.sample(range(len(to_shuffle)), num_bytes_to_shuffle)
        shuffled_section = [to_shuffle[i] for i in indices_to_shuffle]
        random.shuffle(shuffled_section)
        for i, index in enumerate(indices_to_shuffle):
            to_shuffle[index] = shuffled_section[i]
        byte_list[data_to_shuffle_start:data_to_shuffle_end] = to_shuffle
        shuffled_byte_data = bytes(byte_list)
        output_path = os.path.join(os.path.expanduser("~"), "Desktop", "evp_video.mp4")
        with open(output_path, 'wb') as f:
            f.write(shuffled_byte_data)
        messagebox.showinfo("Готово", f"Видео в формате ЭГФ сохранено: {output_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при преобразовании: {e}")

def create_eghf():
    """Комбинированная функция: берёт все выбранные файлы (аудио/видео), извлекает байты,
       перемешивает блоками и создаёт итоговый аудиофайл заданной длины (в секундах)."""
    try:
        duration_sec = int(entry_duration.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для длины.")
        return

    if not selected_files:
        messagebox.showwarning("Предупреждение", "Сначала выберите файлы.")
        return

    combined_bytes = bytearray()
    header_length = 100
    block_size = 64

    for file_path in selected_files:
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in ['.mp4', '.avi', '.mov', '.mkv']:
                # Извлекаем аудио из видео
                audio_path = extract_audio_from_video(file_path)
                if not audio_path:
                    continue
                byte_data = convert_audio_to_bytes(audio_path)
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
            else:
                # Предполагаем, что это аудиофайл
                byte_data = convert_audio_to_bytes(file_path)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось обработать {file_path}: {e}")
            continue

        byte_list = list(byte_data)
        if len(byte_list) > header_length:
            data_to_shuffle = byte_list[header_length:]
            num_blocks = max(1, len(data_to_shuffle) // block_size)
            blocks = [data_to_shuffle[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
            random.shuffle(blocks)
            shuffled_data = [b for block in blocks for b in block]
            byte_list[header_length:header_length+len(shuffled_data)] = shuffled_data
        shuffled_byte_data = bytes(byte_list)
        combined_bytes.extend(shuffled_byte_data)

    sample_rate = 44100
    channels = 2
    bytes_per_sample = 2
    total_bytes = int(duration_sec * sample_rate * channels * bytes_per_sample)
    trimmed_bytes = combined_bytes[:total_bytes]

    output_path = os.path.join(os.path.expanduser("~"), "Desktop", "evp_audio.mp3")
    try:
        save_bytes_as_audio(trimmed_bytes, output_path)
        messagebox.showinfo("Готово", f"ЭГФ сохранен: {output_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

# -------------------------
# GUI
# -------------------------

root = tk.Tk()
root.title("Конвертер ЭГФ Хоруса 8")
root.geometry("900x500")

# Поле для ввода длины в секундах
frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, pady=8)
tk.Label(frame_top, text="Длина ЭГФ (сек):").pack(side=tk.LEFT, padx=8)
entry_duration = tk.Entry(frame_top, width=10)
entry_duration.pack(side=tk.LEFT)
entry_duration.insert(0, "60")  # по умолчанию 60 секунд

# Список выбранных файлов
listbox = tk.Listbox(root, width=110, height=15, selectmode=tk.EXTENDED)
listbox.pack(pady=10, padx=10)

# Кнопки управления файлами
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)

btn_select = tk.Button(frame_buttons, text="Выбрать файлы", command=select_files)
btn_select.grid(row=0, column=0, padx=6)

btn_remove = tk.Button(frame_buttons, text="Удалить выбранное", command=remove_selected)
btn_remove.grid(row=0, column=1, padx=6)

# КНОПКА: теперь обрабатывает все выбранные файлы
btn_videos_to_bytes = tk.Button(frame_buttons, text="Видео -> байты (из всех выбранных)", command=select_videos_to_bytes_multiple)
btn_videos_to_bytes.grid(row=0, column=2, padx=6)

btn_bytes_to_video = tk.Button(frame_buttons, text="Байты -> видео (файл)", command=select_bytes_to_video)
btn_bytes_to_video.grid(row=0, column=3, padx=6)

btn_convert_single_ef = tk.Button(frame_buttons, text="Превратить видео в ЭГФ (один файл)", command=convert_video_to_ef_single)
btn_convert_single_ef.grid(row=0, column=4, padx=6)

btn_create_eghf = tk.Button(root, text="Создать ЭГФ из выбранных файлов", command=create_eghf)
btn_create_eghf.pack(pady=10)

root.mainloop()
