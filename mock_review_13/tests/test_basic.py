import asyncio
def test_event_loop():
    assert asyncio.run(asyncio.sleep(0, result=1)) == 1
