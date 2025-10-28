import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk
import math

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
# Преобразования байт <-> битовая строка
# -------------------------
def bytes_chunk_to_binary_string(byte_chunk):
    """Преобразует блок байтов в строку '0'/'1' (каждый байт -> 8 символов)."""
    return ''.join(format(b, '08b') for b in byte_chunk)

def binary_string_to_bytes(binary_string):
    """Преобразует строку из 0 и 1 обратно в байты."""
    byte_list = []
    trimmed_len = (len(binary_string) // 8) * 8
    for i in range(0, trimmed_len, 8):
        byte_string = binary_string[i:i+8]
        byte = int(byte_string, 2)
        byte_list.append(byte)
    return bytes(byte_list)

# -------------------------
# Основные операции (GUI-колбэки)
# -------------------------
def select_files():
    """Выбрать несколько файлов и добавить в список."""
    global selected_files
    file_paths = filedialog.askopenfilenames(
        title="Выберите файлы",
        filetypes=[("Аудио и видео файлы", "*.mp3;*.wav;*.ogg;*.mp4;*.avi;*.mov;*.mkv"), ("Все файлы", "*.*")]
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
    """Обрабатывает все файлы из selected_files: частичное перемешивание и сохранение combined .bin"""
    if not selected_files:
        messagebox.showwarning("Предупреждение", "Сначала выберите файлы.")
        return
    try:
        combined_bytes = bytearray()
        key_length = 100  # не трогаем первые 100 байт
        for file_path in selected_files:
            try:
                byte_data = convert_video_to_bytes(file_path)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось прочитать {file_path}: {e}")
                continue
            byte_list = list(byte_data)
            if len(byte_list) > key_length + 1:
                data_to_shuffle_start = key_length
                to_shuffle = byte_list[data_to_shuffle_start:]
                num_bytes_to_shuffle = max(1, len(to_shuffle) // 10)  # перемешиваем 10%
                indices_to_shuffle = random.sample(range(len(to_shuffle)), num_bytes_to_shuffle)
                shuffled_section = [to_shuffle[i] for i in indices_to_shuffle]
                random.shuffle(shuffled_section)
                for i, idx in enumerate(indices_to_shuffle):
                    to_shuffle[idx] = shuffled_section[i]
                byte_list[data_to_shuffle_start:] = to_shuffle
            combined_bytes.extend(byte_list)
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
        with open(file_path, 'rb') as f:
            byte_data = f.read()
        duration_minutes = 10  # задайте длительность при необходимости
        out_path = bytes_to_video(byte_data, duration_minutes)
        messagebox.showinfo("Готово", f"Видео создано: {out_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при создании видео: {e}")

def convert_video_to_ef_single():
    """Обработка одного видео файл��: преобразование в ЭГФ (shuffle) и сохранение."""
    file_path = filedialog.askopenfilename(title="Выберите видео файл для преобразования в ЭГФ")
    if not file_path:
        return
    try:
        byte_data = convert_video_to_bytes(file_path)
        byte_list = list(byte_data)
        key_length = 100
        if len(byte_list) > key_length + 1:
            to_shuffle = byte_list[key_length:]
            num_bytes_to_shuffle = max(1, len(to_shuffle) // 10)
            indices_to_shuffle = random.sample(range(len(to_shuffle)), num_bytes_to_shuffle)
            shuffled_section = [to_shuffle[i] for i in indices_to_shuffle]
            random.shuffle(shuffled_section)
            for i, index in enumerate(indices_to_shuffle):
                to_shuffle[index] = shuffled_section[i]
            byte_list[key_length:] = to_shuffle
        shuffled_byte_data = bytes(byte_list)
        output_path = os.path.join(os.path.expanduser("~"), "Desktop", "evp_video.mp4")
        with open(output_path, 'wb') as f:
            f.write(shuffled_byte_data)
        messagebox.showinfo("Готово", f"Видео в формате ЭГФ сохранено: {output_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при преобразовании: {e}")

def create_eghf():
    """Комбинированная функция: берёт все выбранные файлы, извлекает байты, перемешивает блоками и создаёт итоговый аудиофайл."""
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
                audio_path = extract_audio_from_video(file_path)
                if not audio_path:
                    continue
                byte_data = convert_audio_to_bytes(audio_path)
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
            else:
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
# Новая функция: байты -> картинки
# -------------------------
def convert_videos_bytes_to_images():
    """Создаёт N картинок из байтов каждого выбранного видео.

    Логика:
      - Берём сырой файл (видео или аудио) и читаем байты.
      - Делим байты на N приблизительно равных частей.
      - Для каждой части вычисляем минимальную квадратную размерность (side x side),
        дополняем нулями и создаём grayscale PNG.
    """
    if not selected_files:
        messagebox.showwarning("Предупреждение", "Сначала выберите файлы.")
        return
    try:
        n_images = int(entry_images_count.get())
        if n_images < 1:
            raise ValueError
    except Exception:
        messagebox.showerror("Ошибка", "Введите корректное натуральное число картинок.")
        return

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    saved_files = []
    try:
        for file_path in selected_files:
            try:
                byte_data = convert_video_to_bytes(file_path)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось прочитать {file_path}: {e}")
                continue
            total_len = len(byte_data)
            if total_len == 0:
                messagebox.showwarning("Предупреждение", f"Файл {os.path.basename(file_path)} пуст.")
                continue

            # Разбиваем на n_images частей (приблизительно равных)
            base = total_len // n_images
            remainder = total_len % n_images
            start = 0
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            for i in range(n_images):
                add = 1 if i < remainder else 0
                end = start + base + add
                chunk = byte_data[start:end]
                start = end

                if len(chunk) == 0:
                    # если часть пустая — создаём 1x1 чёрный пиксель
                    side = 1
                    padded = b"\x00"
                else:
                    side = math.ceil(math.sqrt(len(chunk)))
                    needed = side*side - len(chunk)
                    if needed:
                        padded = chunk + (b"\x00" * needed)
                    else:
                        padded = chunk

                # Создаём изображение в режиме L (grayscale)
                try:
                    img = Image.frombytes('L', (side, side), padded)
                except Exception as e:
                    # На случай проблем с frombytes — конвертируем через list
                    pixels = list(padded)
                    img = Image.new('L', (side, side))
                    img.putdata(pixels)

                out_name = f"{base_name}_bytes_img_{i+1}.png"
                out_path = os.path.join(desktop, out_name)
                img.save(out_path)
                saved_files.append(out_path)

        if saved_files:
            # Показываем только число и папку, чтобы не перегружать сообщение
            messagebox.showinfo("Готово", f"Создано {len(saved_files)} изображений на рабочем столе.")
        else:
            messagebox.showwarning("Результат", "Не удалось создать ни одной картинки.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при создании изображений: {e}")

# -------------------------
# Новая функция: живой стрим изображений (на лету, без сохранения)
# -------------------------
def stream_bytes_images_live():
    """Открывает окно с бесконечным потоком изображений, создаваемых из байтов выбранных файлов.

    Поведение:
      - Читает байты каждого файла и делит на N частей (entry_images_count).
      - По очереди отображает части как grayscale-изображения в окне в режиме бесконечного цикла.
      - Есть кнопка "Остановить" или закрытие окна для завершения.
    """
    if not selected_files:
        messagebox.showwarning("Предупреждение", "Сначала выберите файлы.")
        return
    try:
        fps = int(entry_fps.get())
        if fps < 1:
            raise ValueError
    except Exception:
        messagebox.showerror("Ошибка", "Введите корректное натуральное число для FPS.")
        return
    try:
        n_images = int(entry_images_count.get())
        if n_images < 1:
            raise ValueError
    except Exception:
        messagebox.showerror("Ошибка", "Введите корректное натуральное число картинок.")
        return

    win = tk.Toplevel(root)
    win.title("Живой просмотр байтовых изображений")

    lbl = tk.Label(win)
    lbl.pack()
    btn_stop = tk.Button(win, text="Остановить", width=12)
    btn_stop.pack(pady=6)

    stop_flag = {'stop': False}

    def stop_stream():
        stop_flag['stop'] = True
        try:
            win.destroy()
        except Exception:
            pass

    btn_stop.config(command=stop_stream)

    # Генератор изображений — создаёт ImageTk.PhotoImage по одному кадру
    def image_generator():
        while not stop_flag['stop']:
            for file_path in selected_files:
                if stop_flag['stop']:
                    return
                try:
                    byte_data = convert_video_to_bytes(file_path)
                except Exception:
                    continue
                total_len = len(byte_data)
                if total_len == 0:
                    continue
                base = total_len // n_images
                remainder = total_len % n_images
                start = 0
                for i in range(n_images):
                    if stop_flag['stop']:
                        return
                    add = 1 if i < remainder else 0
                    end = start + base + add
                    chunk = byte_data[start:end]
                    start = end

                    if len(chunk) == 0:
                        side = 1
                        padded = b"\x00"
                    else:
                        side = math.ceil(math.sqrt(len(chunk)))
                        needed = side * side - len(chunk)
                        if needed:
                            padded = chunk + (b"\x00" * needed)
                        else:
                            padded = chunk

                    try:
                        img = Image.frombytes('L', (side, side), padded)
                    except Exception:
                        pixels = list(padded)
                        img = Image.new('L', (side, side))
                        img.putdata(pixels)

                    # Ограничим размеры для удобства просмотра
                    max_dim = 512
                    if max(img.size) > max_dim:
                        scale = max_dim / max(img.size)
                        new_size = (max(1, int(img.size[0] * scale)), max(1, int(img.size[1] * scale)))
                        img = img.resize(new_size, Image.NEAREST)

                    try:
                        photo = ImageTk.PhotoImage(img)
                        yield photo
                    except Exception:
                        # В редких случаях создание PhotoImage может упасть — пропускаем кадр
                        continue
            # после прохода по всем файлам — цикл повторяется
        return

    gen = image_generator()
    delay = int(1000 / max(1, fps))
    current_ref = {'img': None}

    def update_frame():
        if stop_flag['stop']:
            return
        try:
            photo = next(gen)
        except StopIteration:
            return
        except Exception:
            win.after(delay, update_frame)
            return
        # Обновляем метку — сохраняем ссылку, чтобы объект не собрался GC
        lbl.config(image=photo)
        current_ref['img'] = photo
        win.after(delay, update_frame)

    # Обрабатываем закрытие окна
    win.protocol("WM_DELETE_WINDOW", stop_stream)

    # Запуск обновления
    update_frame()

# -------------------------
# Новые функции: байты -> 0/1 для множества файлов
# -------------------------
def convert_selected_bytes_to_binary_files(combine_into_one=True, output_name="combined_binary.txt", chunk_size=65536):
    """
    Преобразует байты выбранных файлов в текст '0' и '1'.
    Параметры:
      - combine_into_one: если True, все файлы объединяются в один выходной файл.
                          если False, для каждого входного файла создаётся свой файл с суффиксом _binary.txt
      - output_name: имя итогового объединённого файла (в ~/Desktop)
      - chunk_size: размер чтения блока байтов (стриминг)
    """
    if not selected_files:
        messagebox.showwarning("Предупреждение", "Сначала выберите файлы.")
        return
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if combine_into_one:
            out_path = os.path.join(desktop, output_name)
            with open(out_path, 'w') as out_f:
                for file_path in selected_files:
                    out_f.write(f"---FILE:{os.path.basename(file_path)}---\n")
                    with open(file_path, 'rb') as in_f:
                        while True:
                            chunk = in_f.read(chunk_size)
                            if not chunk:
                                break
                            out_f.write(bytes_chunk_to_binary_string(chunk))
                    out_f.write("\n")
            messagebox.showinfo("Готово", f"Битовая строка всех файлов сохранена в: {out_path}")
        else:
            for file_path in selected_files:
                base = os.path.splitext(os.path.basename(file_path))[0]
                out_path = os.path.join(desktop, f"{base}_binary.txt")
                with open(out_path, 'w') as out_f:
                    with open(file_path, 'rb') as in_f:
                        while True:
                            chunk = in_f.read(chunk_size)
                            if not chunk:
                                break
                            out_f.write(bytes_chunk_to_binary_string(chunk))
            messagebox.showinfo("Готово", "Битовые файлы созданы на рабочем столе.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при преобразовании в двоичный код: {e}")

def convert_binary_file_to_bytes_single():
    """Преобразует один файл с 0/1 обратно в байты и сохраняет."""
    file_path = filedialog.askopenfilename(title="Выберите текстовый файл с двоичным кодом")
    if not file_path:
        return
    try:
        with open(file_path, 'r') as binary_file:
            binary_string = binary_file.read().strip()
        byte_data = binary_string_to_bytes(binary_string)
        output_path = os.path.join(os.path.expanduser("~"), "Desktop", "restored_bytes.bin")
        with open(output_path, 'wb') as byte_file:
            byte_file.write(byte_data)
        messagebox.showinfo("Готово", f"Байты восстановлены и сохранены в: {output_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при восстановлении байтов: {e}")

# -------------------------
# GUI
# -------------------------
root = tk.Tk()
root.title("Конвертер ЭГФ Хоруса 8 — с бинарным выводом и живым стримом")
root.geometry("1060x640")

# Верх: длина ЭГФ, количество картинок и FPS
frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, pady=8)

# Длина ЭГФ
tk.Label(frame_top, text="Длина ЭГФ (сек):").pack(side=tk.LEFT, padx=8)
entry_duration = tk.Entry(frame_top, width=10)
entry_duration.pack(side=tk.LEFT)
entry_duration.insert(0, "60")

# Количество картинок
tk.Label(frame_top, text="Количество картинок на файл:").pack(side=tk.LEFT, padx=8)
entry_images_count = tk.Entry(frame_top, width=6)
entry_images_count.pack(side=tk.LEFT)
entry_images_count.insert(0, "3")

# FPS для живого стрима
tk.Label(frame_top, text="FPS:").pack(side=tk.LEFT, padx=8)
entry_fps = tk.Entry(frame_top, width=6)
entry_fps.pack(side=tk.LEFT)
entry_fps.insert(0, "6")

# Список выбранных файлов
listbox = tk.Listbox(root, width=140, height=18, selectmode=tk.EXTENDED)
listbox.pack(pady=10, padx=10)

# Кнопки управления файлами
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)
btn_select = tk.Button(frame_buttons, text="Выбрать файлы", command=select_files)
btn_select.grid(row=0, column=0, padx=6)
btn_remove = tk.Button(frame_buttons, text="Удалить выбранное", command=remove_selected)
btn_remove.grid(row=0, column=1, padx=6)
btn_videos_to_bytes = tk.Button(frame_buttons, text="Видео -> байты (из всех выбранных)", command=select_videos_to_bytes_multiple)
btn_videos_to_bytes.grid(row=0, column=2, padx=6)
btn_bytes_to_video = tk.Button(frame_buttons, text="Байты -> видео (файл)", command=select_bytes_to_video)
btn_bytes_to_video.grid(row=0, column=3, padx=6)
btn_convert_single_ef = tk.Button(frame_buttons, text="Превратить видео в ЭГФ (один файл)", command=convert_video_to_ef_single)
btn_convert_single_ef.grid(row=0, column=4, padx=6)

# Кнопка создания ЭГФ
btn_create_eghf = tk.Button(root, text="Создать ЭГФ из выбранных файлов", command=create_eghf)
btn_create_eghf.pack(pady=10)

# Новые кнопки для двоичного вывода, создания изображений и живого стрима
frame_binary = tk.Frame(root)
frame_binary.pack(pady=6)

btn_bytes_to_binary_all = tk.Button(frame_binary, text="Текст байтов -> 0 и 1 (все в один файл)", command=lambda: convert_selected_bytes_to_binary_files(combine_into_one=True))
btn_bytes_to_binary_all.grid(row=0, column=0, padx=6)

btn_bytes_to_binary_each = tk.Button(frame_binary, text="Текст байтов -> 0 и 1 (по файлу)", command=lambda: convert_selected_bytes_to_binary_files(combine_into_one=False))
btn_bytes_to_binary_each.grid(row=0, column=1, padx=6)

btn_binary_to_bytes = tk.Button(frame_binary, text="Текст 0 и 1 -> байты (один файл)", command=convert_binary_file_to_bytes_single)
btn_binary_to_bytes.grid(row=0, column=2, padx=6)

# Кнопка: Создать картинки из байтов выбранных файлов
btn_bytes_to_images = tk.Button(frame_binary, text="Создать картинки из байтов (по файлу)", command=convert_videos_bytes_to_images)
btn_bytes_to_images.grid(row=0, column=3, padx=6)

# Кнопка: Живой стрим изображений
btn_stream = tk.Button(frame_binary, text="Живой просмотр (стрим)", command=stream_bytes_images_live)
btn_stream.grid(row=0, column=4, padx=6)

# Запуск интерфейса
root.mainloop()
