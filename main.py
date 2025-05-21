
import json
import os
import time
import random

# File to store vocabulary
VOCAB_FILE = "vocab.json"

# Loads vocabulary, adding repeat_count if missing
def load_vocab():
    if not os.path.exists(VOCAB_FILE):
        return {}
    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
        for unit in vocab.values():
            for entry in unit:
                entry.setdefault("repeat_count", 0)
        return vocab

# Saves vocabulary to file
def save_vocab(vocab):
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=4)

# Cleans input string
def clean_input(text):
    return text.strip().lower()

# Validates input, returns (is_valid, error_message)
def is_valid_word_input(vocab, unit, word, meaning=None, check_duplicates=True, check_unit_exists=True):
    word = clean_input(word)
    if check_unit_exists and unit not in vocab:
        return False, f"שגיאה: היחידה {unit} לא קיימת."
    if not word:
        return False, "שגיאה: המילה לא יכולה להיות ריקה."
    if meaning is not None and not clean_input(meaning):
        return False, "שגיאה: המשמעות לא יכולה להיות ריקה."
    if check_duplicates and unit in vocab and any(entry["word"].lower() == word for entry in vocab[unit]):
        return False, f"שגיאה: המילה '{word}' כבר קיימת ביחידה {unit}."
    return True, ""

# Gets user input for a prompt
def get_user_input(prompt):
    return clean_input(input(prompt))

# Prints an error message
def print_error(message):
    if message:
        print(message)

# Adds a word to a unit
def add_word_to_unit(vocab, unit, word, meaning):
    if unit not in vocab:
        vocab[unit] = []
    vocab[unit].append({"word": word, "meaning": meaning, "repeat_count": 0})
    save_vocab(vocab)

# Handles adding a word
def add_word(unit, word, meaning):
    vocab = load_vocab()
    is_valid, error = is_valid_word_input(vocab, unit, word, meaning, check_unit_exists=False)
    print_error(error)
    if is_valid:
        add_word_to_unit(vocab, unit, word, meaning)
        print(f"המילה '{word}' נוספה ליחידה {unit} עם המשמעות '{meaning}'.")

# Removes a word from a unit
def remove_word_from_unit(vocab, unit, index):
    vocab[unit].pop(index)
    save_vocab(vocab)

# Confirms deletion with user
def confirm_deletion(word, unit):
    return get_user_input(f"האם למחוק את '{word}' מהיחידה {unit}? (כן/לא): ").lower() == 'כן'

# Handles deleting a word
def delete_word(unit, word):
    vocab = load_vocab()
    is_valid, error = is_valid_word_input(vocab, unit, word, check_duplicates=False)
    print_error(error)
    if not is_valid:
        return
    for i, entry in enumerate(vocab[unit]):
        if entry["word"].lower() == word:
            if confirm_deletion(word, unit):
                remove_word_from_unit(vocab, unit, i)
                print(f"המילה '{word}' נמחקה.")
            return
    print(f"שגיאה: המילה '{word}' לא נמצאה ביחידה {unit}.")

# Updates a word in a unit
def update_word_in_unit(vocab, unit, index, new_word, new_meaning):
    vocab[unit][index]["word"] = new_word
    vocab[unit][index]["meaning"] = new_meaning
    save_vocab(vocab)

# Handles updating a word
def update_word(unit, old_word, new_word, new_meaning):
    vocab = load_vocab()
    is_valid, error = is_valid_word_input(vocab, unit, old_word, check_duplicates=False)
    print_error(error)
    if not is_valid:
        return
    is_valid, error = is_valid_word_input(vocab, unit, new_word, new_meaning)
    print_error(error)
    if not is_valid:
        return
    for i, entry in enumerate(vocab[unit]):
        if entry["word"].lower() == old_word:
            update_word_in_unit(vocab, unit, i, new_word, new_meaning)
            print(f"המילה '{old_word}' עודכנה ל-'{new_word}' עם המשמעות '{new_meaning}'.")
            return
    print(f"שגיאה: המילה '{old_word}' לא נמצאה ביחידה {unit}.")

# Displays words in a unit
def list_words(unit):
    vocab = load_vocab()
    if unit not in vocab:
        print(f"שגיאה: היחידה {unit} לא קיימת.")
        return
    if not vocab[unit]:
        print(f"היחידה {unit} ריקה.")
        return
    print(f"\nמילים ביחידה {unit}:")
    for entry in vocab[unit]:
        print(f"מילה: {entry['word']}, משמעות: {entry['meaning']}, חזרות: {entry['repeat_count']}")

# Selects a unit for a mode
def select_unit(vocab, mode_name):
    if not vocab:
        print("אין יחידות זמינות. הוסף מילים במצב עריכה.")
        return None
    print("\nיחידות זמינות:", ", ".join(vocab.keys()))
    unit = get_user_input(f"הזן יחידה ל{mode_name} (או 'יציאה' לחזרה): ")
    if unit == 'יציאה' or unit not in vocab or not vocab[unit]:
        print(f"שגיאה: היחידה {unit} לא קיימת או ריקה." if unit != 'יציאה' else "")
        return None
    return unit

# Selects a range of words or all words
def select_word_range(vocab, unit):
    list_words(unit)
    if get_user_input("להתאמן על כל היחידה או טווח? (מלא/טווח): ") != 'טווח':
        return vocab[unit]
    start_word = get_user_input("הזן מילה התחלתית: ")
    end_word = get_user_input("הזן מילה סופית: ")
    start_index = end_index = -1
    for i, entry in enumerate(vocab[unit]):
        if entry["word"].lower() == start_word:
            start_index = i
        if entry["word"].lower() == end_word:
            end_index = i
    if start_index == -1 or end_index == -1:
        print("שגיאה: אחת המילים או שתיהן לא נמצאו.")
        return None
    if start_index > end_index:
        print("שגיאה: המילה ההתחלתית חייבת להופיע לפני הסופית.")
        return None
    return vocab[unit][start_index:end_index + 1]

# Trains a single word
def train_word(entry):
    print(f"\nמילה: {entry['word']}")
    input("לחץ אנטר לראות משמעות (או המתן 3 שניות)...")
    time.sleep(3)
    print(f"משמעות: {entry['meaning']}")
    entry["repeat_count"] += 1
    input("לחץ אנטר להמשיך...")

# Handles training mode
def training_mode():
    vocab = load_vocab()
    unit = select_unit(vocab, "אימון")
    if not unit:
        return
    words = select_word_range(vocab, unit)
    if not words:
        return
    for _ in range(7):
        random.shuffle(words)
        for entry in words:
            if entry["repeat_count"] < 7:
                train_word(entry)
    save_vocab(vocab)
    print("סיום האימון!")

# Tests a single word
def test_word(entry):
    print(f"\nמילה: {entry['word']}")
    answer = get_user_input("מהי המשמעות? ")
    if answer == entry["meaning"].lower():
        print("נכון!")
        return True, None
    print(f"לא נכון. המשמעות הנכונה היא: {entry['meaning']}")
    return False, (entry["word"], entry["meaning"], answer)

# Handles testing mode
def testing_mode():
    vocab = load_vocab()
    unit = select_unit(vocab, "בחינה")
    if not unit:
        return
    words = vocab[unit]
    random.shuffle(words)
    correct = 0
    incorrect = []
    for entry in words:
        is_correct, error = test_word(entry)
        if is_correct:
            correct += 1
        else:
            incorrect.append(error)
    print(f"\nסיכום הבחינה:")
    print(f"תשובות נכונות: {correct} מתוך {len(words)}")
    print(f"ציון: {(correct / len(words) * 100) if words else 0:.2f}%")
    if incorrect:
        print("\nמילים שגויות:")
        for word, correct_meaning, answer in incorrect:
            print(f"מילה: {word}, תשובתך: {answer}, משמעות נכונה: {correct_meaning}")

# Handles editing mode menu
def editing_mode():
    while True:
        print("\n--- מצב עריכה ---")
        print("1. הוסף מילה\n2. מחק מילה\n3. עדכן מילה\n4. הצג מילים ביחידה\n5. חזור")
        choice = get_user_input("בחר אפשרות (1-5): ")
        if choice == '5':
            return
        if choice in ['1', '2', '3', '4']:
            unit = get_user_input("הזן שם יחידה: ")
            if choice == '1':
                word = get_user_input("הזן מילה באנגלית: ")
                meaning = get_user_input("הזן משמעות בעברית: ")
                add_word(unit, word, meaning)
            elif choice == '2':
                word = get_user_input("הזן מילה למחיקה: ")
                delete_word(unit, word)
            elif choice == '3':
                old_word = get_user_input("הזן את המילה לעדכון: ")
                new_word = get_user_input("הזן מילה חדשה: ")
                new_meaning = get_user_input("הזן משמעות חדשה: ")
                update_word(unit, old_word, new_word, new_meaning)
            else:
                list_words(unit)
        else:
            print("בחירה לא תקינה, נסה שוב.")

# Runs the main menu
def main_menu():
    while True:
        print("\n--- מאמן אוצר מילים ---")
        print("1. מצב עריכה\n2. מצב אימון\n3. מצב בחינה\n4. יציאה")
        choice = get_user_input("בחר אפשרות (1-4): ")
        if choice == '1':
            editing_mode()
        elif choice == '2':
            training_mode()
        elif choice == '3':
            testing_mode()
        elif choice == '4':
            print("תודה שהשתמשת במאמן אוצר המילים!")
            break
        else:
            print("בחירה לא תקינה, נסה שוב.")

# Entry point
if __name__ == "__main__":
    main_menu()
