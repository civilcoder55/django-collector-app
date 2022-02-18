from lib.CollectorBot.listener import StreamListener


def run():
    print("start")
    stream_listener = StreamListener()
    stream_listener.filter(track=['@_collectorapp_'], stall_warnings=True)
