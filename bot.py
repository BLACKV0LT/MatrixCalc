import asyncio
import os
import numpy as np

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

import matrix_core  # твои функции: summa, multi, det, transp, deg

# ------------------ BOT SETUP ------------------
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ------------------ FSM STATES ------------------
class MatrixStates(StatesGroup):
    waiting_first_input = State()   # первая матрица
    waiting_second_input = State()  # вторая матрица или степень

# ------------------ KEYBOARD ------------------
def get_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Сложение", callback_data="add"),
            InlineKeyboardButton(text="✖ Умножение", callback_data="mul")
        ],
        [
            InlineKeyboardButton(text="🔢 Определитель", callback_data="det"),
            InlineKeyboardButton(text="🔁 Транспонирование", callback_data="trans")
        ],
        [
            InlineKeyboardButton(text="^ Возвести в степень", callback_data="power")
        ]
    ])
    return keyboard

# ------------------ PARSING MATRIX ------------------
def parse_matrix(text: str) -> np.ndarray:
    try:
        rows = text.strip().split("\n")
        matrix = [list(map(float, row.strip().split())) for row in rows]
        return np.array(matrix)
    except Exception:
        raise ValueError("Ошибка формата матрицы")

# ------------------ START COMMAND ------------------
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Выбери действие:", reply_markup=get_keyboard())

# ------------------ CALLBACK BUTTON ------------------
@dp.callback_query()
async def process_callback(callback: CallbackQuery, state: FSMContext):
    operation = callback.data
    await state.update_data(operation=operation)

    await callback.message.answer("Введите первую матрицу (через пробелы и перенос строки):")
    await state.set_state(MatrixStates.waiting_first_input)
    await callback.answer()

# ------------------ FIRST INPUT ------------------
@dp.message(MatrixStates.waiting_first_input)
async def first_input(message: Message, state: FSMContext):
    data = await state.get_data()
    operation = data["operation"]

    try:
        matrix = parse_matrix(message.text)
        await state.update_data(first_matrix=matrix)

        # Если det или transpose, считаем сразу
        if operation == "det":
            result = matrix_core.det(matrix)
            await message.answer(f"Результат:\n{np.array2string(result, precision=2)}")
            await state.clear()
        elif operation == "trans":
            result = matrix_core.transp(matrix)
            await message.answer(f"Результат:\n{np.array2string(result, precision=2)}")
            await state.clear()
        else:
            # Для add, mul, power → ждём второй ввод
            if operation in ["add", "mul"]:
                await message.answer("Введите вторую матрицу:")
            elif operation == "power":
                await message.answer("Введите степень (целое число):")
            await state.set_state(MatrixStates.waiting_second_input)

    except ValueError:
        await message.answer("Ошибка формата матрицы. Попробуйте снова.")

# ------------------ SECOND INPUT ------------------
@dp.message(MatrixStates.waiting_second_input)
async def second_input(message: Message, state: FSMContext):
    data = await state.get_data()
    operation = data["operation"]
    matrix1 = data.get("first_matrix")

    try:
        if operation in ["add", "mul"]:
            matrix2 = parse_matrix(message.text)
            if operation == "add":
                result = matrix_core.summa(matrix1, matrix2)
            else:
                result = matrix_core.multi(matrix1, matrix2)
        elif operation == "power":
            n = int(message.text)
            result = matrix_core.deg(matrix1, n)

        await message.answer(f"Результат:\n{np.array2string(result, precision=2)}")
        await state.clear()

    except ValueError:
        await message.answer("Ошибка формата или несовместимые размеры. Попробуйте снова.")
    except Exception:
        await message.answer("Ошибка! Проверьте данные и попробуйте снова.")

# ------------------ RUN BOT ------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
