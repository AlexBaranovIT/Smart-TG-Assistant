import openai
from telebot import TeleBot, types
from fuzzywuzzy import process

TOKEN = 'YOUR TELEGRAM API TOKEN'
openai.api_key = 'YOUR OPENAI API TOKEN'

bot = TeleBot(TOKEN)


# Load questions and answers from the file into a dictionary
def load_data_from_file():
    data = {}
    with open('data.txt', 'r') as file:
        for line in file:
            question, answer = line.strip().split('|')
            data[question.lower()] = answer
    return data

data_dict = load_data_from_file()


def get_answer_from_data(query):
    # Using fuzzy matching to get the closest match and its score
    closest_match, score = process.extractOne(query, data_dict.keys())

    # If the score is above a certain threshold, return the corresponding answer
    if score > 80:
        return data_dict[closest_match]
    return None


def rephrase_answer(answer):
    # Use OpenAI to rephrase the answer to keep just the facts
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Rephrase the following information to provide only the facts: {answer}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

@bot.message_handler(func=lambda m: True)
def send_response(message):
    user_query = message.text
    answer = get_answer_from_data(user_query)

    if answer:
        rephrased_answer = rephrase_answer(answer)
        bot.send_message(message.chat.id, rephrased_answer)
    else:
        # If no answer is found in the database, you can directly query OpenAI or send a default response
        bot.send_message(message.chat.id, "Sorry, I couldn't find an answer to your question.")


# Polling loop
bot.polling(none_stop=True)
