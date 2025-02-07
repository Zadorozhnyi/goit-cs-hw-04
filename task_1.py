import os
import time
import threading
import multiprocessing
from queue import Queue

def search_in_file(file_path, keywords):
    # Шукає ключові слова у файлі.
    results = {word: [] for word in keywords}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for word in keywords:
                if word in content:
                    results[word].append(file_path)
    except Exception as e:
        print(f"Помилка обробки файлу {file_path}: {e}")
    return results

def worker(files, keywords, queue):
    # Процес-обробник для multiprocessing.
    local_results = {word: [] for word in keywords}
    for file in files:
        res = search_in_file(file, keywords)
        for word in keywords:
            local_results[word].extend(res[word])
    queue.put(local_results)

def search_with_threading(file_list, keywords):
    # Багатопотоковий пошук у файлах.
    threads = []
    queue = Queue()
    
    def thread_worker(files):
        local_results = {word: [] for word in keywords}
        for file in files:
            res = search_in_file(file, keywords)
            for word in keywords:
                local_results[word].extend(res[word])
        queue.put(local_results)

    num_threads = min(4, len(file_list))  
    chunk_size = len(file_list) // num_threads
    
    for i in range(num_threads):
        start = i * chunk_size
        end = None if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=thread_worker, args=(file_list[start:end],))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    final_results = {word: [] for word in keywords}
    while not queue.empty():
        local_results = queue.get()
        for word in keywords:
            final_results[word].extend(local_results[word])
    
    return final_results

def search_with_multiprocessing(file_list, keywords):
    # Багатопроцесорний пошук у файлах.
    queue = multiprocessing.Queue()
    
    num_processes = min(4, len(file_list))  
    chunk_size = len(file_list) // num_processes
    processes = []
    
    for i in range(num_processes):
        start = i * chunk_size
        end = None if i == num_processes - 1 else (i + 1) * chunk_size
        process = multiprocessing.Process(target=worker, args=(file_list[start:end], keywords, queue))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    final_results = {word: [] for word in keywords}
    while not queue.empty():
        local_results = queue.get()
        for word in keywords:
            final_results[word].extend(local_results[word])
    
    return final_results

def main():
    # Основна функція.
    keywords = ["Python", "error", "process"]
    directory = "./text_files"
    
    file_list = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")]
    
    print("--- Запуск багатопотокового пошуку ---")
    start_time = time.time()
    thread_results = search_with_threading(file_list, keywords)
    print("Час виконання threading:", time.time() - start_time, "секунд")
    print("Результати:", thread_results)
    
    print("\n--- Запуск багатопроцесорного пошуку ---")
    start_time = time.time()
    process_results = search_with_multiprocessing(file_list, keywords)
    print("Час виконання multiprocessing:", time.time() - start_time, "секунд")
    print("Результати:", process_results)

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Виправлення для macOS
    main()
