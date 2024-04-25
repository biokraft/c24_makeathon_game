import random
import streamlit as st
from openai import OpenAI
from prompts import basic_prompt
from session import SessionStorage
from validate_input import check_token_limit
import regex as re
from slack import send_message_to_slack
from utils import reset_high_score_and_leaderboard, scroll_to_bottom

global_app_session = SessionStorage()

bot_roles = [
    "a quirky time traveler from the future",
    "a retired pirate turned etiquette coach",
    "an alien visiting Earth for the first time",
    "a detective from a noir film with a penchant for melodrama",
    "a mad scientist obsessed with baking",
    "a medieval knight navigating the modern world",
    "a ghost who is more afraid of humans than they are of it",
    "a super villain with very low stakes plots",
    "a superhero with the most useless superpower",
    "a robot who is convinced it is a human",
    "a software develeoper from inda that only knows farsi",
    "a monkey with a typewriter",
    "a cat that can talk",
    "a dog that can talk",
    "a time traveler from the past",
    ]

st.title("C24 - Shut up GPT! 🤐")
def initialize_app():
    update_high_score(global_app_session['high_score'])
    display_disclaimer()

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def display_disclaimer():
    """
    Display the game disclaimer.
    """
    with st.expander("ℹ️ How to play"):
        st.write(
            "This quirky Chatbot seems to really like Check24 and has a multiple personality disorder. "
            "Additionally, it won't shut up about how much it loves the company. 🤫\n\n"
            "The goal of this game is to get the bot to mention the company "
            "name as early as possible.\n\n"
            "Good luck! 🍀\n\n"
        )
        st.markdown(
            '<p style="font-size: 12px;">'
            'Shoutout to Jan Czechowski, who built the '
            '<a href="https://shutupgpt.janczechowski.com/">'
            'original version</a> of this game. 🙌\n',
            unsafe_allow_html=True
        )


def update_high_score(score: int = 0):
    """
    Display the current high score.

    Args:
        score (int): The high score.
    """
    global_app_session['high_score'] = score


def handle_user_input(client: OpenAI):
    """
    Handle user input and generate assistant response.

    Args:
        client (OpenAI): The OpenAI client.
    """
    if prompt := st.chat_input("Give me your best shot.."):
        # Check if user input is within token limit
        if not check_token_limit(prompt):
            st.error("Your message is too long! Please try again with a shorter message.")
            st.stop()

        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            bot_role = random.choice(bot_roles)
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{
                    "role": "user",
                    "content": basic_prompt.format(user_message=prompt, role=bot_role)
                }],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        # Check how long it took the model to mention the company name and display it
        check_high_score(response, prompt)

def update_leaderboard():
    st.sidebar.empty()
    st.sidebar.title("Leaderboard")
    reset_high_score_and_leaderboard()
    if not global_app_session['leaderboard']:
        st.sidebar.write("No high scores yet. Be the first to claim the top spot!")
    else:
        for idx, (player, score) in enumerate(global_app_session['leaderboard'].items()):
            st.sidebar.write(f"{idx + 1}. {player}: {score}")

def add_high_score_to_leaderboard():
    """
    Update the leaderboard with the new high score.
    """
    # Initialize the leaderboard if it doesn't exist
    if not global_app_session['leaderboard']:
        global_app_session['leaderboard'] = {}

    if st.session_state.get('high_score_broken', False) and 'name' in st.session_state:
        name = st.session_state['name']
        score = st.session_state['high_score_broken']

        if score > global_app_session['high_score']:
            update_high_score(score)

        # Add the new high score to the leaderboard
        global_app_session['leaderboard'][name] = score
        # Sort the leaderboard in descending order of scores
        global_app_session['leaderboard'] = dict(sorted(global_app_session['leaderboard'].items(), key=lambda item: item[1], reverse=True))

        update_leaderboard()
        del st.session_state['high_score_broken']  # Clear the high score flag
        del st.session_state['name']  # Clear the stored name
        st.success("High score updated!")
        st.rerun()
        scroll_to_bottom()


def check_high_score(response: str, prompt: str):
    """
    Check if the assistant response contains a new high score.

    Args:
        response (str): The assistant response.
        prompt (str): The user prompt.
    """
    search = re.finditer(r"Check24", response, flags=re.IGNORECASE)
    indices = [match.start() for match in search]
    if indices:
        score = 1000 - indices[0]
        if score > global_app_session['high_score']:
            st.session_state['wait_for_name'] = True
            st.session_state['high_score_broken'] = score

            if "SLACK_WEBHOOK_URL" in st.secrets:
                send_message_to_slack(f"🚀 *New high score: {score}* 🏆\n\n"
                        f"Prompt: ```{prompt}```\n\n"
                        f"Response: ```{response}```",
                        st.secrets["SLACK_WEBHOOK_URL"])
            st.rerun()
        else:
            if score < 0 < global_app_session['high_score']:
                st.error(
                    f"That was a pretty bad attempt 😬\n"
                    f"Try again 🍀"
                )
            else:
                st.success(
                    f"Score: {score}.\n"
                    f"High score: {global_app_session['high_score']}."
                )
    else:
        st.error("The model did not mention the company name. Sorry, something went wrong. 😢 Try again!")


if __name__ == "__main__":
    if not global_app_session['app_running']:
        if "SLACK_WEBHOOK_URL" in st.secrets:
            send_message_to_slack(
                "*Shut up GPT is live!* 🚀 High score is reset. Let's see who will claim it! 🏆",
                st.secrets["SLACK_WEBHOOK_URL"]
                )
        global_app_session['app_running'] = True
    initialize_app()
    update_leaderboard()
    if st.session_state.get('high_score_broken'):
        st.success(f"🎉 New high score: {global_app_session['high_score']} 🎉")
        st.balloons()
        name = st.text_input("You broke the high score! Please enter your name:", key='name')
        if st.button("Submit Name"):
            add_high_score_to_leaderboard()
    else:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        handle_user_input(client)
    scroll_to_bottom()
