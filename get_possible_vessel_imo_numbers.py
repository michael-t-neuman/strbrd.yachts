import requests
import logging
import random
import threading
import queue

def fetch_imo(imo_queue, result_queue):
    while not imo_queue.empty():
        imo_number = imo_queue.get()
        try:
            if requests.get(f"https://www.vesselfinder.com/?imo={imo_number}",headers={'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36'},timeout=2.5).status_code == 200:
                result_queue.put(imo_number)
        except:
            pass
        finally:
            imo_queue.task_done()

def write_to_csv(result_queue,imo_queue):
    with open('imos.csv', 'a+', encoding='utf-8', newline='') as outfile:
        while True:
            imo_number = result_queue.get()
            if imo_number is None:
                break
            outfile.write(str(imo_number) + '\n')
            outfile.flush()
            logging.info(f"NEW IMO DISCOVERED: {imo_number} | {imo_queue.qsize()} LEFT IN QUEUE")
            result_queue.task_done()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    random_range = list(range(9999999))
    random.shuffle(random_range)
    imo_queue = queue.Queue()
    result_queue = queue.Queue()
    for imo in random_range:
        imo_queue.put(imo)
    writer_thread = threading.Thread(target=write_to_csv, args=(result_queue,imo_queue,num_boats_found_so_far))
    writer_thread.start()
    for _ in range(3):
        thread = threading.Thread(target=fetch_imo, args=(imo_queue, result_queue))
        thread.daemon = True
        thread.start()
    imo_queue.join()
    result_queue.put(None)
    writer_thread.join()
    logging.info("Processing complete.")
