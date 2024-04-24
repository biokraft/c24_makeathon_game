import random

import streamlit as st
from openai import OpenAI
from prompts import basic_prompt
from SessionStorage import SessionStorage
from validate_input import check_token_limit
import regex as re
from slack import send_message_to_slack

PASSWORD = "HierCheckIchAlles"

session = SessionStorage()

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
	"luffy from one piece",
	"homer simpson",
	"steven hawkings",
	"yung lean",
	"biggie smalls",
	"tupac",
	"spongebob",
	"the users lost brother",
	"a monkey with a typewriter",
	"a cat that can talk",
	"a dog that can talk",
	"Gandalf from Lord of the Rings",
	"Steve Jobs",
	"Elon Musk",
	"a time traveler from the past",
	]

st.title("C24 - Shut up GPT! 🤐")
# Display the disclaimer
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

# Create a placeholder for the high score
high_score_placeholder = st.empty()
high_score_placeholder.markdown(f"🏆 **High Score:** {session['high_score']} ")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
	st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
	st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])

send_message_to_slack(
	"*Shut up GPT is live!* 🚀 High score is reset. Let's see who will claim it! 🏆",
	st.secrets["SLACK_WEBHOOK_URL"]
	)

# Accept user input
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
	search = re.finditer(r"Check24", response, flags=re.IGNORECASE)
	indices = [match.start() for match in search]
	if indices:
		score = 4000 - indices[0]
		if score > session['high_score']:
			session['high_score'] = score
			st.success(f"🎉 New high score: {score} 🎉")
			st.balloons()
			send_message_to_slack(f"🚀 *New high score: {score}* 🏆\n\n"
								  f"Prompt: ```{prompt}```\n\n"
								  f"Response: ```{response}```",
								  st.secrets["SLACK_WEBHOOK_URL"])
		else:
			if score < 0 and session['high_score'] > 0:
				score = 0
				st.error(
					f"That was a pretty bad attempt 😬\n"
					f"High score: {session['high_score']}."
					)
			else:
				st.success(
					f"Score: {score}.\n"
					f"High score: {session['high_score']}."
					)
	else:
		st.error("The model did not mention the company name. Sorry, something went wrong. 😢 Try again!")

	# Update the high score placeholder on any user input
	high_score_placeholder.markdown(f"🏆 **High Score:** {session['high_score']}")
