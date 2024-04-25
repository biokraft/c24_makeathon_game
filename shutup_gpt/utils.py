import streamlit as st
import datetime
import streamlit.components.v1 as components
from session import SessionStorage

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
    current_time = datetime.datetime.now()

    # Check if the reset timestamp exists in the session state
    if 'last_reset_time' not in st.session_state:
        st.session_state['last_reset_time'] = current_time

    # Calculate the time difference
    time_difference = current_time - st.session_state['last_reset_time']

    # Reset the high score and leaderboard if an hour has passed
    if time_difference.total_seconds() >= 3600:
        session = SessionStorage()
        session['high_score'] = 0
        session['leaderboard'] = {}
        st.session_state['last_reset_time'] = current_time
        st.experimental_rerun()

    # Display the time of the next scheduled reset
    next_reset_time = st.session_state['last_reset_time'] + datetime.timedelta(hours=1)
    st.sidebar.write(f"Next reset at: {next_reset_time.strftime('%Y-%m-%d %H:%M')}")

