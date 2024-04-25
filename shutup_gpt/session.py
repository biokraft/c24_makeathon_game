import streamlit as st

@st.cache_resource
class SessionStorage:
    def __init__(self):
        self.high_score = 0
        self.last_reset_time = 0

    def __getitem__(self, key):
        if key not in self.__dict__:
            setattr(self, key, None)
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
