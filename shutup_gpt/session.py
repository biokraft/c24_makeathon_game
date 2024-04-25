import datetime

import streamlit as st
import pytz

@st.cache_resource
class SessionStorage:
    def __init__(self):
        self.high_score = 0
        self.last_reset_time = 0
        self.leaderboard = {}
        self.app_running = False

        germany_tz = pytz.timezone('Europe/Berlin')
        self.last_reset_time = datetime.datetime.now(germany_tz)

    def reset(self):
        self.high_score = 0
        self.leaderboard = {}
        self.last_reset_time = datetime.datetime.now(pytz.timezone('Europe/Berlin'))

    def __getitem__(self, key):
        if key not in self.__dict__:
            setattr(self, key, None)
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
