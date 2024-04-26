import streamlit as st
import datetime
import streamlit.components.v1 as components
import pytz
from session import SessionStorage
from slack import send_message_to_slack

def set_page_configuration():
    st.set_page_config(
        page_title="Check24 Shut Up GPT!",
        page_icon="🤐",
        layout="wide",
    )


def scroll_to_bottom():
    components.html("""
    <script>
    setTimeout(() => {
        document.querySelectorAll('*').forEach(el => {
            if (el.scrollHeight > el.clientHeight) {
                el.scrollTop = el.scrollHeight;
            }
        });
    }, 1000); // Small delay to ensure the DOM has loaded
    </script>
    """, height=0)


def reset_high_score_and_leaderboard():
    """
    Reset the high score and leaderboard if an hour has passed since the last reset.
    """
    germany_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.datetime.now(germany_tz)

    # Check if the reset timestamp exists in the session state
    session = SessionStorage()
    if not session['last_reset_time']:
        session['last_reset_time'] = current_time

    # Calculate the time difference
    time_difference = current_time - session['last_reset_time']

    next_reset_time = session['last_reset_time'] + datetime.timedelta(hours=1)
    # Reset the high score and leaderboard if an hour has passed
    if time_difference.total_seconds() >= 3600:
        session.reset()
        if "SLACK_WEBHOOK_URL" in st.secrets:
            send_message_to_slack(
                f"🚀 *Leaderboard was reset!* 🏆\n"
                f"Next reset in an hour. 🕒",
                st.secrets["SLACK_WEBHOOK_URL"]
                )

    # Display the time of the next scheduled reset
    st.sidebar.write(f"Next reset at: {next_reset_time.strftime('%Y-%m-%d %H:%M')}")

