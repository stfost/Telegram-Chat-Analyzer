import pandas as pd
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetCommonChatsRequest
from telethon.tl.types import User  
import asyncio

api_id = ''
api_hash = ''
phone_number = ''

chat_id = 

MESSAGE_SEARCH_LIMIT = 500000

session_name = 'telegram_session'

members_data = []
processed_users = set()

async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("Клиент успешно запущен...")

        try:
            chat_entity = await client.get_entity(chat_id)
            print(f"Анализируем чат: '{chat_entity.title}'")
            print(f"Начинаем анализ последних {MESSAGE_SEARCH_LIMIT} сообщений для сбора участников...")

            processed_messages = 0
            async for message in client.iter_messages(chat_entity, limit=MESSAGE_SEARCH_LIMIT):
                processed_messages += 1
                if processed_messages % 200 == 0:
                    print(f"Обработано {processed_messages}/{MESSAGE_SEARCH_LIMIT} сообщений...")
                
                if message.sender and isinstance(message.sender, User) and not message.sender.bot:
                    user = message.sender
                    
                    if user.id not in processed_users:
                        common_chats_count = 0
                        try:
                            common_chats_result = await client(GetCommonChatsRequest(user_id=user.id, max_id=0, limit=100))
                            common_chats_count = len(common_chats_result.chats)
                        except Exception as e:
                            print(f"Не удалось получить общие чаты для {user.username or user.id}: {e}")

                        members_data.append({
                            'имя': user.first_name,
                            'юзернейм': user.username,
                            'ид': user.id,
                            'количество общих групп': common_chats_count
                        })
                        
                        processed_users.add(user.id)
                        print(f"Найден новый участник: {user.first_name} ({user.username}), общих групп: {common_chats_count}. Всего найдено: {len(processed_users)}")

        except ValueError:
            print(f"Ошибка: Неверный ID чата ({chat_id}). Убедитесь, что вы состоите в этом чате и ID указан верно.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    if members_data:
        df = pd.DataFrame(members_data)
        df_sorted = df.sort_values(by='количество общих групп', ascending=False)

        print("\n--- Итоговая таблица ---")
        print(df_sorted.to_string(index=False))

        try:
            df_sorted.to_csv('telegram_common_chats_active.csv', index=False, encoding='utf-8-sig')
            print("\nРезультаты также сохранены в файл 'telegram_common_chats_active.csv'")
        except Exception as e:
            print(f"Не удалось сохранить файл: {e}")
    else:
        print("\nНе удалось собрать данные об участниках из истории сообщений.")


if __name__ == "__main__":
    asyncio.run(main())