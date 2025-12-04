import asyncio
import random
import os
from collections import Counter

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# === ТОКЕН БОТА ===
BOT_TOKEN = "8595067497:AAGWTT6YkL0amt0-MUdimk9wJH-TGm4vzsw"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

games = {}
# Режим одного телефона (singlemode): chat_id -> session
single_sessions = {}


# === ФАЙЛ СО СПИСКОМ КАРТ ===
CARDS_FILE = "cards_ru.txt"

# === СТИКЕРЫ / КАРТИНКИ ===
# Сюда подставь реальный file_id стикера для шпиона (узнаётся через /getfile или логами бота)
SPY_STICKER_ID = "CAACAgIAAxkBAAEUbeRpMfiGTpmX1YsFOAEKvfzXBuxLugACqAIAAi8P8AaI2qBqs3F_0zYE"  # например: "CAACAgIAAxkBA..."

# Здесь можно сопоставить конкретные карты и их стикеры.
# Ключ — название карты (строка, как в списке), значение — file_id стикера.
CARD_STICKERS = {
    "Рыцарь": "CAACAgIAAxkBAAEUbYJpMfUe6NzNqbGURbziV9CqLglUNAACX28AAmm9YUv3XmqcvWqQejYE",
    "Лучницы": "CAACAgIAAxkBAAEUbYRpMfUk1z7UmzFeKGztbAlq6Bgl6gAC3G4AAnpvYUv0ft5AFEBXmTYE",
    "Варвары": "CAACAgIAAxkBAAEUbYhpMfU0BQON65uSXvONP1cAAVyNJe8AAthwAAJMaqBLsDBCbDLTNoM2BA",
    "Миньоны": "CAACAgIAAxkBAAEUbYppMfVQliyO1LTsdP8AAZRSH-QomXcAAj1oAAKOHGFLIYht5hmz8Rg2BA",
    "Орда миньонов": "CAACAgIAAxkBAAEUbYxpMfVVKCM_TE0y9tedQvAmEioL6wACw2sAAlmzoEvxqrbCa8U4YjYE",
    "Скелеты": "CAACAgIAAxkBAAEUbZBpMfVq1iKEtgyMDMzBFyAgQJh89QAC52gAAoWroEuNf7gw5Lpc4zYE",
    "Армия скелетов": "CAACAgIAAxkBAAEUbY5pMfVfPG_0HWrCkQ16LIjNVOIRlAAClm0AAhxQYEvhUwAByx9tJwM2BA",
    "Мушкетёр": "CAACAgIAAxkBAAEUbZRpMfV5FMh1_-Vskw4gfuMomkVDJgACWXEAAhRscEuvbDKX0Xd96zYE",
    "Валькирия": "CAACAgIAAxkBAAEUbZZpMfV-0rr9Tmgn9djc5nQnvdQlHgAC5G0AAkjleUtZtWZAS5gJeDYE",
    "Ведьма": "CAACAgIAAxkBAAEUbZppMfWLki7si1HbqJ4YffKgDmc8DQACW3MAAnBFoUuukzB_rUZ3STYE",
    "П.Е.К.К.А.": "CAACAgIAAxkBAAEUbZxpMfWQkCJT4ekwQl0ebWqLgW3bxgACwm8AAhOCuUuwO1mFX1JkqTYE",
    "Мини-П.Е.К.К.А.": "CAACAgIAAxkBAAEUbaJpMfWdJyPOKZ4Z6K_pm5ZclxNMJwACfmsAAvTpcUtbs6WWq6L8UDYE",
    "Принц": "CAACAgIAAxkBAAEUbaZpMfXSZIGVFA3EXLzu_MhAU39HMAAC6HMAAtbpoUvh8oVRDeQ7uzYE",
    "Тёмный принц": "CAACAgIAAxkBAAEUbappMfX6sgEo3zkDr7vF0Rx4-akGGQAC2msAAuSBkEtaFCA5Eze6tjYE",
    "Мегарыцарь": "CAACAgIAAxkBAAEUba5pMfYJYOyRML9owvAQQZqK2CqkbgACD28AAkuasEu8gpq78veUYjYE",
    "Маг": "CAACAgIAAxkBAAEUbbBpMfYUOyvgzO9ierocfxCAkZxTRgACOnIAApH4oEsT1V-BuK8IcDYE",
    "Ледяной маг": "CAACAgIAAxkBAAEUbbJpMfYgX1ax819UCbyviowC1BatUgACYG8AApwceEsvPXrzS4omwDYE",
    "Электромаг": "CAACAgIAAxkBAAEUbbRpMfYxmpCxldCbO6_zYYFE67ukRgACEmwAAmhciUuITq1ugK8nMDYE",
    "Дракончик": "CAACAgIAAxkBAAEUbbZpMfZEu2YUoKI_g0zQ0tKKGaSWqwACdmsAAjc7kEvwjX74aowZ3zYE",
    "Адская гончая": "CAACAgIAAxkBAAEUbbhpMfZO9mCHuMwc0XlY8S1KQRgvPwACgG0AA7SwS-4pxjlJyP81NgQ",
    "Голем": "CAACAgIAAxkBAAEUbbppMfZWiEV5fseS0b_7y-Pb7pZOqgACZ2gAAhhlsUvFCPVa4FhfizYE",
    "Гигант": "CAACAgIAAxkBAAEUbbxpMfZbCYJWVZpMCGlAwZpo6UFZSwAC8HYAApyxoEuJH9JJ0VhsfTYE",
    "Королевский гигант": "CAACAgIAAxkBAAEUbcBpMfZtNo_EbMCijRLvRGbIECNEIQACzGcAArgGuUtUeGfYpM3cITYE",
    "Шахтёр": "CAACAgIAAxkBAAEUbcBpMfZtNo_EbMCijRLvRGbIECNEIQACzGcAArgGuUtUeGfYpM3cITYE",
    "Бандитка": "CAACAgIAAxkBAAEUbcRpMfbIopld66GGb7gZjpIsWzIg3QACNmcAAt9BeUtPgLjPFlimtTYE",
    "Принцесса": "CAACAgIAAxkBAAEUbcZpMfbMvUZ_bEVHzfr9ucq-fkWh4gACuWoAAg3QcEvHEeNP_uSn7TYE",
    "Королевские рекруты": "CAACAgIAAxkBAAEUbchpMfbrJ4T2Yb3lG_LLPG5xGslgawACVWwAAnL2uEt4VUHabjpRfjYE",
    "Королевские кабаны": "CAACAgIAAxkBAAEUbcppMfb0eSK9N_PfWvOJW_-3VGB6aQAC8HYAAlrooEvagLU8yo_s-jYE",
    "Гоблин-гигант": "CAACAgIAAxkBAAEUbcxpMfb83hDLL14u9gQ6RAABtknNVtMAAjJrAAImsrFLPWb_E5fUjZQ2BA",
    "Электрогигант": "CAACAgIAAxkBAAEUbc5pMfcY0NiiNK6MC7MHo6zi-aZnJQACEWkAAr7GuEuCN0A2PWGpgTYE",
    "Феникс": "CAACAgIAAxkBAAEUbdBpMfcfXLOfDoehejfq47ht4Nc97wACk2cAAkjIkEtuaoFRN0L90DYE",
    "Всадница на баране": "CAACAgIAAxkBAAEUbdJpMfcl6S9DSICdcAjckSUi6ckxCgACuXYAArV1oEukS6UbAS6EiTYE",
    "Бездна": "CAACAgIAAxkBAAEUbdRpMfc9__B2NU4FQB9y2Qvdxe1s9gAC9WkAAvIqcUu29fVRDtI3WDYE",
}



def save_cards(cards):
    cards = sorted(set(c.strip() for c in cards if c.strip()))
    with open(CARDS_FILE, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(c + "\n")


def load_cards():
    # Если файла нет — создаём с базовым набором
    if not os.path.exists(CARDS_FILE):
        default_cards = [
            "Рыцарь",
            "Лучницы",
            "Варвары",
            "Гоблины",
            "Гоблины-копейщики",
            "Миньоны",
            "Орда миньонов",
            "Скелеты",
            "Армия скелетов",
            "Мушкетёр",
            "Валькирия",
            "Ведьма",
            "П.Е.К.К.А.",
            "Мини-П.Е.К.К.А.",
            "Принц",
            "Тёмный принц",
            "Охотник",
            "Мегарыцарь",
            "Маг",
            "Ледяной маг",
            "Электромаг",
            "Дракончик",
            "Адская гончая",
            "Голем",
            "Гигант",
            "Королевский гигант",
            "Шахтёр",
            "Бандитка",
            "Принцесса",
            "Королевские рекруты",
            "Королевские кабаны",
            "Гоблин-гигант",
            "Электрогигант",
            "Феникс",
            "Всадница на баране",
        ]
        save_cards(default_cards)
        return default_cards

    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


CLASH_CARDS = load_cards()

# === Состояния игр (на чат) ===
# chat_id -> game_state
games = {}


def get_game(chat_id: int):
    if chat_id not in games:
        games[chat_id] = {
            "host_id": None,
            "players": {},         # user_id -> {"name": str}
            "state": "idle",       # idle | lobby | in_game
            "spy_ids": [],         # список user_id шпионов
            "spy_count": 1,        # по умолчанию 1 шпион
            "card": None,
            "votes": {},           # voter_id -> target_id
            "voting_active": False,
            "history": [],         # список прошлых раундов
        }
    return games[chat_id]


def normalize_card_name(name: str) -> str:
    # Упрощённое сравнение названий карт
    return "".join(ch.lower() for ch in name if ch.isalnum() or ch.isspace()).strip()


# === /start ===
@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "Привет! Это игра-шпион по Clash Royale 👑\n\n"
        "Основные команды в группе:\n"
        "/newgame — создать лобби\n"
        "/startgame — выдать роли и начать раунд\n"
        "/singlemode — режим для 1 телефона\n"
        "/startvote — начать голосование, кто шпион\n"
        "/guess <карта> — шпион пытается угадать карту\n"
        "/spies <1|2> — задать количество шпионов\n"
        "/history — показать историю раундов\n"
        "/endgame — завершить игру\n\n"
        "Управление картами:\n"
        "/addcard <название> — добавить карту\n"
        "/delcard <название> — удалить карту\n"
        "/cardlist — показать список карт"
    )
    await message.answer(text)


# === /newgame — создание лобби ===
@dp.message(Command("newgame"))
async def cmd_newgame(message: Message):
    if message.chat.type == "private":
        await message.answer("Создавать игру нужно в групповом чате 🙂")
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    game["host_id"] = message.from_user.id
    game["players"] = {}
    game["state"] = "lobby"
    game["spy_ids"] = []
    game["card"] = None
    game["votes"] = {}
    game["voting_active"] = False
    # history не трогаем — можно хранить историю внутри одной сессии

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Участвовать 🙋‍♂️", callback_data="join_game")]
        ]
    )

    await message.answer(
        "Создано новое лобби Clash Spy!\n"
        "Нажмите кнопку, чтобы присоединиться.\n"
        "Ведущий после набора игроков использует /startgame.\n"
        f"Сейчас настроено шпионов: {game['spy_count']}. Можно изменить командой /spies 1 или /spies 2.",
        reply_markup=kb
    )


# === Кнопка «Участвовать» ===
@dp.callback_query(F.data == "join_game")
async def on_join_game(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if game["state"] != "lobby":
        await callback.answer("Сейчас нет активного лобби.", show_alert=True)
        return

    user = callback.from_user
    if user.id in game["players"]:
        await callback.answer("Ты уже в игре!", show_alert=True)
        return

    game["players"][user.id] = {"name": user.full_name}
    await callback.answer("Ты присоединился к игре!")

    await callback.message.edit_text(
        "Лобби Clash Spy\n"
        "Игроки:\n" +
        "\n".join(f"• {p['name']}" for p in game["players"].values()) +
        "\n\nВедущий может запустить игру командой /startgame.",
        reply_markup=callback.message.reply_markup
    )


# === /spies — настройка количества шпионов (1 или 2) ===
@dp.message(Command("spies"))
async def cmd_spies(message: Message):
    if message.chat.type == "private":
        await message.answer("Настраивать количество шпионов нужно в групповой игре.")
        return

    chat_id = message.chat.id
    game = get_game(chat_id)

    if message.from_user.id != game.get("host_id"):
        await message.answer("Только ведущий может менять количество шпионов.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /spies 1 или /spies 2")
        return

    try:
        count = int(parts[1])
    except ValueError:
        await message.answer("Нужно указать число 1 или 2.")
        return

    if count not in (1, 2):
        await message.answer("Поддерживаются только режимы с 1 или 2 шпионами.")
        return

    game["spy_count"] = count
    await message.answer(f"Количество шпионов в игре установлено: {count}.")


# === Запуск раунда (общая функция) ===
async def start_round(chat_id: int, announce_message: Message | None = None):
    game = get_game(chat_id)
    players = list(game["players"].items())

    if len(players) < 3:
        if announce_message:
            await announce_message.answer("Нужно минимум 3 игрока, чтобы начать раунд.")
        return

    if not CLASH_CARDS:
        if announce_message:
            await announce_message.answer("Нет доступных карт. Добавь карты через /addcard.")
        return

    # Защита: если шпионов больше, чем игроков -1, уменьшаем
    spy_count = game.get("spy_count", 1)
    if spy_count >= len(players):
        spy_count = 1
        game["spy_count"] = 1

    # Выбираем карту и шпионов
    card = random.choice(CLASH_CARDS)
    player_ids = [uid for uid, _ in players]
    spy_ids = random.sample(player_ids, k=spy_count)

    game["card"] = card
    game["spy_ids"] = spy_ids
    game["state"] = "in_game"
    game["votes"] = {}
    game["voting_active"] = False

    # Оправляем роли в ЛС + стикеры / картинки
    failed = []
    for user_id, info in players:
        is_spy = user_id in spy_ids
        try:
            if is_spy:
                text = (
                    "Ты 🕵️ ШПИОН!\n"
                    "Ты НЕ знаешь карту.\n"
                    "Слушай других и постарайся угадать, о какой карте идёт речь.\n\n"
                    "В группе ты можешь использовать команду:\n"
                    "/guess <карта> — чтобы попытаться выиграть."
                )
            else:
                text = (
                    "Ты обычный игрок.\n"
                    f"Карта этого раунда: *{card}*\n"
                    "Не называй её прямо, описывай намёками."
                )

            await bot.send_message(user_id, text, parse_mode="Markdown")

            # Попытка отправить стикер / картинку
            try:
                if is_spy and SPY_STICKER_ID:
                    await bot.send_sticker(user_id, SPY_STICKER_ID)
                elif not is_spy:
                    sticker_id = CARD_STICKERS.get(card)
                    if sticker_id:
                        await bot.send_sticker(user_id, sticker_id)
            except Exception:
                # Если стикер не отправился — это не критично
                pass

        except Exception:
            failed.append(info["name"])

    if announce_message:
        msg = (
            f"Новый раунд запущен! Всего игроков: {len(players)}\n"
            f"Шпионов в этом раунде: {spy_count}\n"
            "Всем ролям отправлены личные сообщения.\n\n"
            "Дальше обсуждаете в чате, затем ведущий запускает голосование командой /startvote.\n"
            "Шпион(ы) могут попытаться угадать карту командой /guess <карта>."
        )
        if failed:
            msg += (
                "\n\nНе удалось написать этим игрокам "
                "(пусть сначала напишут боту в ЛС /start):\n"
                + "\n".join(f"• {name}" for name in failed)
            )
        await announce_message.answer(msg)


# === /startgame — старт первого раунда ===
@dp.message(Command("startgame"))
async def cmd_startgame(message: Message):
    chat_id = message.chat.id
    game = get_game(chat_id)

    if game["state"] != "lobby":
        await message.answer("Сначала создай лобби командой /newgame.")
        return

    if message.from_user.id != game["host_id"]:
        await message.answer("Только ведущий может запустить игру.")
        return

    await start_round(chat_id, announce_message=message)


# === /startvote — начать голосование «кто шпион» ===
@dp.message(Command("startvote"))
async def cmd_startvote(message: Message):
    chat_id = message.chat.id
    game = get_game(chat_id)

    if game["state"] != "in_game":
        await message.answer("Сейчас нет активного раунда.")
        return

    if message.from_user.id != game["host_id"]:
        await message.answer("Только ведущий может начать голосование.")
        return

    if game["voting_active"]:
        await message.answer("Голосование уже идёт.")
        return

    if len(game["players"]) < 3:
        await message.answer("Недостаточно игроков для голосования.")
        return

    kb_rows = []
    for user_id, info in game["players"].items():
        kb_rows.append([
            InlineKeyboardButton(
                text=info["name"],
                callback_data=f"vote_{user_id}"
            )
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    game["votes"] = {}
    game["voting_active"] = True

    await message.answer(
        "Голосование: кто шпион? Нажмите на игрока, за которого голосуете.",
        reply_markup=kb
    )


# === Обработка голосов ===
@dp.callback_query(F.data.startswith("vote_"))
async def on_vote(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if not game["voting_active"] or game["state"] != "in_game":
        await callback.answer("Сейчас голосование не активно.", show_alert=True)
        return

    voter_id = callback.from_user.id
    if voter_id not in game["players"]:
        await callback.answer("Ты не участвуешь в этом раунде.", show_alert=True)
        return

    try:
        target_id = int(callback.data.split("_", 1)[1])
    except ValueError:
        await callback.answer("Ошибка голоса.", show_alert=True)
        return

    if target_id not in game["players"]:
        await callback.answer("Игрок уже не в игре.", show_alert=True)
        return

    game["votes"][voter_id] = target_id
    await callback.answer("Голос засчитан.")

    total_players = len(game["players"])
    voted_count = len(game["votes"])

    # Обновляем текст с текущими результатами
    summary_lines = []
    counts = Counter(game["votes"].values())
    for uid, info in game["players"].items():
        summary_lines.append(f"{info['name']}: {counts.get(uid, 0)}")

    text = (
        "Голосование: кто шпион?\n\n"
        "Текущее количество голосов:\n" +
        "\n".join(summary_lines) +
        f"\n\nПроголосовало {voted_count} из {total_players}."
    )
    try:
        await callback.message.edit_text(text, reply_markup=callback.message.reply_markup)
    except Exception:
        pass

    # Все проголосовали — считаем результат
    if voted_count == total_players:
        await finish_voting(callback.message)


# === Подведение итога голосования ===
async def finish_voting(message: Message):
    chat_id = message.chat.id
    game = get_game(chat_id)

    game["voting_active"] = False

    if not game["votes"]:
        result_text = "Никто не проголосовал. Раунд завершён без результата."
        await show_round_result(message, result_text=result_text, winner="none")
        return

    counts = Counter(game["votes"].values())
    most_common = counts.most_common()
    suspect_id, top_votes = most_common[0]

    # Проверяем ничью
    if len(most_common) > 1 and most_common[1][1] == top_votes:
        result_text = (
            "По результатам голосования — ничья между несколькими игроками.\n"
            "Шпионы выигрывают раунд!"
        )
        await show_round_result(message, result_text=result_text, winner="spies")
        return

    spy_ids = game.get("spy_ids", [])
    suspect_name = game["players"][suspect_id]["name"]
    spies_names = [game["players"][sid]["name"] for sid in spy_ids if sid in game["players"]]

    if suspect_id in spy_ids:
        result_text = (
            f"Большинство проголосовало за: {suspect_name}.\n"
            f"Это действительно был один из шпионов! Мирные победили."
        )
        await show_round_result(message, result_text=result_text, winner="civilians")
    else:
        result_text = (
            f"Большинство проголосовало за: {suspect_name}.\n"
            f"Но шпионами были: {', '.join(spies_names) if spies_names else 'неизвестно'}. "
            f"Шпионы выигрывают раунд!"
        )
        await show_round_result(message, result_text=result_text, winner="spies")


# === Показ результата раунда + кнопки «новый раунд / конец игры» ===
async def show_round_result(message: Message, result_text: str, winner: str | None = None):
    chat_id = message.chat.id
    game = get_game(chat_id)

    card = game.get("card") or "неизвестно"
    spy_ids = game.get("spy_ids") or []
    spy_names = [game["players"].get(uid, {"name": "неизвестен"})["name"] for uid in spy_ids]
    if not spy_names:
        spy_names = ["неизвестны"]

    winner_map = {
        "spies": "Победили шпионы.",
        "civilians": "Победили мирные.",
        "none": "Раунд завершился без победителя.",
        None: "",
    }
    winner_line = winner_map.get(winner, "")

    text = (
        "Раунд завершён.\n\n" +
        result_text +
        "\n\n" +
        f"Карта раунда: *{card}*\n"
        f"Шпионы: {', '.join(spy_names)}"
    )
    if winner_line:
        text += "\n" + winner_line

    # Сохраняем в историю
    game["history"].append({
        "card": card,
        "spy_ids": spy_ids[:],
        "winner": winner,
        "result_text": result_text,
    })

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔁 Новый раунд с теми же игроками",
                    callback_data="new_round"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏹ Завершить игру",
                    callback_data="end_game_btn"
                ),
            ],
        ]
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

    # Возвращаемся в состояние «лобби» с теми же игроками
    game["state"] = "lobby"
    game["spy_ids"] = []
    game["card"] = None
    game["votes"] = {}
    game["voting_active"] = False


# === Кнопка «Новый раунд» ===
@dp.callback_query(F.data == "new_round")
async def on_new_round(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    game = get_game(chat_id)

    if callback.from_user.id != game.get("host_id"):
        await callback.answer("Только ведущий может запустить новый раунд.", show_alert=True)
        return

    if len(game["players"]) < 3:
        await callback.answer("Недостаточно игроков для нового раунда.", show_alert=True)
        return

    await callback.answer("Новый раунд!")
    await start_round(chat_id, announce_message=callback.message)


# === Кнопка «Завершить игру» ===
@dp.callback_query(F.data == "end_game_btn")
async def on_end_game_btn(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in games:
        del games[chat_id]
    await callback.answer("Игра завершена.")
    await callback.message.answer(
        "Игра полностью завершена. "
        "Можно создать новое лобби командой /newgame."
    )


# === /guess — шпион пытается угадать карту ===
@dp.message(Command("guess"))
async def cmd_guess(message: Message):
    chat_id = message.chat.id
    game = get_game(chat_id)

    if game["state"] != "in_game":
        await message.answer("Сейчас не идёт раунд.")
        return

    user_id = message.from_user.id
    spy_ids = game.get("spy_ids", [])

    if user_id not in spy_ids:
        await message.answer("Только шпион может использовать /guess.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /guess <название карты>")
        return

    guess = parts[1]
    real_card = game.get("card") or ""

    if normalize_card_name(guess) == normalize_card_name(real_card):
        result_text = (
            f"Шпион угадал карту: *{real_card}!*\n"
            "Шпионы выигрывают раунд."
        )
        await show_round_result(message, result_text=result_text, winner="spies")
    else:
        result_text = (
            f"Шпион ошибся. Его версия: *{guess}*.\n"
            f"Правильная карта: *{real_card}*. Мирные побеждают."
        )
        await show_round_result(message, result_text=result_text, winner="civilians")


# === /addcard — добавить свою карту ===
@dp.message(Command("addcard"))
async def cmd_addcard(message: Message):
    global CLASH_CARDS
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /addcard <название карты>")
        return

    card_name = parts[1].strip()
    if not card_name:
        await message.answer("Название карты не может быть пустым.")
        return

    if card_name in CLASH_CARDS:
        await message.answer("Такая карта уже есть в списке.")
        return

    CLASH_CARDS.append(card_name)
    save_cards(CLASH_CARDS)
    await message.answer(f"Карта «{card_name}» добавлена в список.")


# === /delcard — удалить карту ===
@dp.message(Command("delcard"))
async def cmd_delcard(message: Message):
    global CLASH_CARDS
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /delcard <название карты>")
        return

    card_name = parts[1].strip()
    if card_name not in CLASH_CARDS:
        await message.answer("Такой карты нет в списке.")
        return

    CLASH_CARDS = [c for c in CLASH_CARDS if c != card_name]
    save_cards(CLASH_CARDS)
    await message.answer(f"Карта «{card_name}» удалена из списка.")


# === /cardlist — показать список карт ===
@dp.message(Command("cardlist"))
async def cmd_cardlist(message: Message):
    if not CLASH_CARDS:
        await message.answer("Список карт пуст. Добавь карты через /addcard.")
        return

    max_show = 50
    show_cards = CLASH_CARDS[:max_show]
    text = "Текущий список карт (первые 50):\n\n" + "\n".join(f"• {c}" for c in show_cards)
    if len(CLASH_CARDS) > max_show:
        text += f"\n\nВсего карт: {len(CLASH_CARDS)}. Показаны первые {max_show}."

    await message.answer(text)


# === /history — история раундов ===
@dp.message(Command("history"))
async def cmd_history(message: Message):
    chat_id = message.chat.id
    game = get_game(chat_id)
    history = game.get("history", [])

    if not history:
        await message.answer("История раундов пока пуста.")
        return

    max_show = 10
    to_show = history[-max_show:]
    lines = []
    start_index = max(1, len(history) - len(to_show) + 1)

    for idx, entry in enumerate(to_show, start=start_index):
        card = entry.get("card", "неизвестно")
        spy_ids = entry.get("spy_ids", [])
        winner = entry.get("winner")

        spy_names = [game["players"].get(uid, {"name": "неизвестен"})["name"] for uid in spy_ids]
        if not spy_names:
            spy_names = ["неизвестны"]

        if winner == "spies":
            winner_txt = "шпионы"
        elif winner == "civilians":
            winner_txt = "мирные"
        elif winner == "none":
            winner_txt = "нет победителя"
        else:
            winner_txt = "неизвестно"

        lines.append(
            f"Раунд {idx}: карта — {card}; шпионы — {', '.join(spy_names)}; победитель — {winner_txt}"
        )

    text = "История последних раундов:\n\n" + "\n".join(lines)
    await message.answer(text)


# === /endgame — ручное завершение игры ===
@dp.message(Command("endgame"))
async def cmd_endgame(message: Message):
    chat_id = message.chat.id
    if chat_id in games:
        del games[chat_id]
    await message.answer("Игра завершена. Можно начинать новое лобби командой /newgame.")

@dp.message(Command("singlemode"))
async def cmd_singlemode(message: Message):
    # Режим одного телефона логичен только в ЛС
    if message.chat.type != "private":
        await message.answer("Режим одного телефона работает только в личных сообщениях с ботом.")
        return

    # Клавиатура с выбором количества игроков
    buttons_row1 = [
        InlineKeyboardButton(text=str(n), callback_data=f"single_count_{n}")
        for n in (3, 4, 5, 6)
    ]
    buttons_row2 = [
        InlineKeyboardButton(text=str(n), callback_data=f"single_count_{n}")
        for n in (7, 8, 9, 10)
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=[buttons_row1, buttons_row2])

    await message.answer(
        "Режим одного телефона.\n\n"
        "Выберите количество игроков, которые сейчас находятся рядом:",
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("single_count_"))
async def on_single_count(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    if callback.message.chat.type != "private":
        await callback.answer("Этот режим доступен только в ЛС с ботом.", show_alert=True)
        return

    try:
        total = int(callback.data.split("_")[2])
    except ValueError:
        await callback.answer("Ошибка выбора количества игроков.", show_alert=True)
        return

    if total < 3 or total > 10:
        await callback.answer("Поддерживается от 3 до 10 игроков.", show_alert=True)
        return

    # Выбираем карту и номер шпиона
    if not CLASH_CARDS:
        await callback.message.edit_text("Нет доступных карт. Добавь карты через /addcard.")
        await callback.answer()
        return

    card = random.choice(CLASH_CARDS)
    spy_number = random.randint(1, total)

    single_sessions[chat_id] = {
        "total": total,
        "current": 1,
        "card": card,
        "spy_number": spy_number,
        "active": True,
        "last_sticker_msg_id": None,  # сюда будем запоминать отправленный стикер
    }

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Показать карту игроку 1",
                    callback_data="single_show"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"Режим одного телефона.\n"
        f"Игроков: {total}.\n\n"
        "Сейчас телефон у Игрока 1.\n"
        "Пусть остальные отвернутся.\n"
        "Когда он будет готов, нажмите «Показать карту».",
        reply_markup=kb
    )
    await callback.answer()

@dp.callback_query(F.data == "single_show")
async def on_single_show(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    session = single_sessions.get(chat_id)

    if not session or not session.get("active"):
        await callback.answer("Сессия не найдена. Вызови /singlemode заново.", show_alert=True)
        return

    current = session["current"]
    total = session["total"]
    card = session["card"]
    spy_number = session["spy_number"]

    if current > total:
        await callback.answer("Все игроки уже посмотрели свои роли.", show_alert=True)
        return

    # Текст с ролью
    if current == spy_number:
        text = (
            f"Игрок {current}, смотри только ты!\n\n"
            "Ты 🕵️ ШПИОН.\n"
            "Ты НЕ знаешь карту.\n\n"
            "Запомни свою роль.\n"
            "Нажми «Готово, передать дальше», и отдай телефон следующему игроку."
        )
        is_spy = True
    else:
        text = (
            f"Игрок {current}, смотри только ты!\n\n"
            f"Карта этого раунда: *{card}*\n\n"
            "Запомни карту.\n"
            "Нажми «Готово, передать дальше», и отдай телефон следующему игроку."
        )
        is_spy = False

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Готово, передать дальше",
                    callback_data="single_next"
                )
            ]
        ]
    )

    # Обновляем текст с кнопкой
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

    # Удаляем предыдущий стикер (если по какой-то причине остался)
    last_id = session.get("last_sticker_msg_id")
    if last_id:
        try:
            await bot.delete_message(chat_id, last_id)
        except Exception:
            pass
        session["last_sticker_msg_id"] = None

    # Отправляем новый стикер для текущего игрока
    sticker_id = None
    if is_spy and SPY_STICKER_ID:
        sticker_id = SPY_STICKER_ID
    elif not is_spy:
        sticker_id = CARD_STICKERS.get(card)

    if sticker_id:
        try:
            m = await bot.send_sticker(chat_id, sticker_id)
            session["last_sticker_msg_id"] = m.message_id
        except Exception:
            session["last_sticker_msg_id"] = None

    await callback.answer()


@dp.callback_query(F.data == "single_next")
async def on_single_next(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    session = single_sessions.get(chat_id)

    if not session or not session.get("active"):
        await callback.answer("Сессия не найдена. Вызови /singlemode заново.", show_alert=True)
        return

    # Удаляем стикер текущего игрока
    last_id = session.get("last_sticker_msg_id")
    if last_id:
        try:
            await bot.delete_message(chat_id, last_id)
        except Exception:
            pass
        session["last_sticker_msg_id"] = None

    session["current"] += 1
    current = session["current"]
    total = session["total"]

    # Все посмотрели
    if current > total:
        session["active"] = False
        await callback.message.edit_text(
            "Все игроки посмотрели свои роли.\n\n"
            "Теперь положите телефон и играйте как обычно:\n"
            "один из вас — шпион, который не знает карту.\n"
            "Обсуждайте, задавайте вопросы и пытайтесь его вычислить!"
        )
        await callback.answer()
        return

    # Есть ещё игроки
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Показать карту игроку {current}",
                    callback_data="single_show"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"Теперь дайте телефон Игроку {current}.\n"
        "Пусть остальные отвернутся.\n"
        "Когда он будет готов, нажмите «Показать карту».",
        reply_markup=kb
    )
    await callback.answer()



# === Запуск бота ===
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())