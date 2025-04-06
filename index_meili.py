import meilisearch
import json
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python index_meili.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    client = meilisearch.Client('http://localhost:7700', 'rmuds5OuiWit9ccjQdTnjOUG3zvKi-ayIwunj3R0ums')

    with open(input_file, encoding='utf-8') as data:
        chunks = json.load(data)
    
    taskinfo = client.index('Buddhism').add_documents(chunks)
    uid = taskinfo.task_uid

    while True:
        task = client.get_task(uid)
        print(task)
        if task.status != 'enqueued' and task.status != 'processing':
            break

if __name__ == "__main__":
    main()