import requests

is_queue_empty = True

while is_queue_empty:
    for queue in requests.get("http://guest:guest@mq_75:15672/api/queues/%2F").json():
        if queue.get("name")=="local_persist_vulnz_queue":
            messages = queue.get("messages")
            unacked_messages = queue.get("messages_unacknowledged")
            print (f"local_persist_vulnz_queue has {messages} messages and {unacked_messages} unacked messages")
            if messages == 0 and unacked_messages == 0:
                is_queue_empty = False
                break