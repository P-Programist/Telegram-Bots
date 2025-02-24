from aiogram.contrib.fsm_storage.redis import RedisStorage2
from .constants import REDIS_PASSWORD

"""
The following RedisStorage instance is responsible for keeping bot states in redis database.
{"telegram_id": <redisState object>}
"""
storage = RedisStorage2(
    host="127.0.0.1",
    db=1,
    port=6379,
    password=REDIS_PASSWORD,
)

"""
The following RedisStorage instance is responsible for keeping state of language that user choose
{"telegram_id": str}
"""
redworker = RedisStorage2(
    host="127.0.0.1",
    db=2,
    port=6379,
    password=REDIS_PASSWORD,
)

"""
Таблица point хранит в себе баллы собранные пользователем
{"telegram_id": int}
"""
point = RedisStorage2(
    host="127.0.0.1",
    db=3,
    port=6379,
    password=REDIS_PASSWORD,
)


"""
Таблица time_question хранит в себе время в которое должен уложиться пользователь во время теста, также на каком вопросе находился пользователь
{"telegram_id": (<datetime object>, int)}
"""
time_question = RedisStorage2(
    host="127.0.0.1",
    db=4,
    port=6379,
    password=REDIS_PASSWORD,
)

"""
The following RedisStorage is responsible for keeping right answer number while a User passing the Quiz.
{"telegram_id": "1"}
"""
check = RedisStorage2(
    host="127.0.0.1",
    db=5,
    port=6379,
    password=REDIS_PASSWORD,
)
'''Таблица check хранит в себе ответы пользователя'''

feedback_data = RedisStorage2(
    host="127.0.0.1",
    db=6,
    port=6379,
    password=REDIS_PASSWORD,
)
'''Таблица feedback_data хранит в себе данные пользователя, при этом созраняются они по этапно'''
