import random
import streamlit as st
from openai import OpenAI
from prompts import basic_prompt
from session import SessionStorage
from validate_input import check_token_limit
import regex as re
from slack import send_message_to_slack
from utils import reset_high_score_and_leaderboard, scroll_to_bottom, set_page_configuration

set_page_configuration()
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
    "a software developer from India that only knows Farsi",
    "a monkey with a typewriter",
    "a cat that can talk",
    "a dog that can talk",
    "a time traveler from the past",
    "an aspiring wizard struggling to learn basic spells",
    "a Viking who accidentally time-traveled to the 21st century",
    "a retired superhero trying to live a normal life",
    "a bard from a fantasy realm trying to make it as a modern musician",
    "a conspiracy theorist trying to uncover alien plots",
    "a renaissance painter reincarnated as a street artist",
    "a Victorian inventor stuck in the digital age",
    "a mystical healer who only uses outdated remedies",
    "an old Western sheriff in a modern city",
    "a space explorer stranded on a deserted alien planet"
]

st.title("CHECK24 - Shut up GPT! 🤐")
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

def get_user_message_count():
    if "messages" not in st.session_state or not st.session_state.messages:
        return 0
    return len([message for message in st.session_state.messages if message["role"] == "user"])

def display_disclaimer():
    """
    Display the game disclaimer.
    """
    with st.expander("ℹ️ How to play"):
        st.write(
            "This quirky chatbot seems to really like Check24 and has a multiple personality disorder. "
            "Additionally, it won't shut up about how much it loves the company. 🤫\n\n"
            "The goal of this game is to get the bot to output 'Check24' as early as possible.\n\n"
            "Hint: This means as close as possible to the start of the response string.\n\n"
            "The leaderboard will be displayed in the sidebar. If you break the high score, you can enter your name. "
            "Before you submit your name, make sure to take a screenshot with the time of you breaking the high score "
            "and the popup displaying that you broke it. 📸 - Each leaderboard reset, the person with the highest score "
            "will be the winner that is eligible to receive a reward from our personnel.\n\n"
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
            if prompt == f"/reset {st.secrets['RESET_KEY']}":
                reset_high_score_and_leaderboard()
                st.success("High score and leaderboard have been reset.")
                st.session_state.messages = []
                session = SessionStorage()
                if "SLACK_WEBHOOK_URL" in st.secrets:
                    send_message_to_slack(
                        f"🚀 *Leaderboard was reset manually!* 🏆\n"
                        f"Next reset at: {session['last_reset_time'].strftime('%Y-%m-%d %H:%M')}",
                        st.secrets["SLACK_WEBHOOK_URL"]
                        )
                session.reset()
                st.rerun()
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
        check_high_score(response)

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
        st.success("High score updated!")
        if "SLACK_WEBHOOK_URL" in st.secrets and "messages" in st.session_state and len(st.session_state["messages"]) >= 2:
            prompt = st.session_state["messages"][-2]["content"]
            response = st.session_state["messages"][-1]["content"]
            send_message_to_slack(
                f"🚀 *{name} unlocked a new high score: {score}* 🏆\n\n"
                f"Prompt: ```{prompt}```\n\n"
                f"Response: ```{response}```",
                st.secrets["SLACK_WEBHOOK_URL"]
                )
        del st.session_state['high_score_broken']  # Clear the high score flag
        del st.session_state['name']  # Clear the stored name
        st.rerun()
        scroll_to_bottom()


def check_high_score(response: str):
    """
    Check if the assistant response contains a new high score.

    Args:
        response (str): The assistant response.
    """
    search = re.finditer(r"Check24", response, flags=re.IGNORECASE)
    indices = [match.start() for match in search]
    if indices:
        score = 1000 - indices[0] - ((get_user_message_count() - 1) * 20)
        if score > global_app_session['high_score'] and global_app_session['high_score'] <= 0:
            st.session_state['wait_for_name'] = True
            st.session_state['high_score_broken'] = score
            st.rerun()
        else:
            if score < 0:
                st.error(
                    f"That was a pretty bad attempt ( ͡° ͜ʖ ͡°)"
                    f" - Try again! 🍀"
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
        st.success(f"🎉 New high score by: {st.session_state['high_score_broken']} 🎉")
        st.balloons()
        name = st.text_input("You broke the high score! Please enter your name:", key='name', max_chars=12)
        if st.button("Submit Name"):
            add_high_score_to_leaderboard()
    else:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        handle_user_input(client)
    scroll_to_bottom()
