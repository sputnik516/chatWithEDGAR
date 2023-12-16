import os
import uuid
import pandas as pd
import streamlit as st

# from langchain.callbacks.tracers import WandbTracer
from langchain.chains import ConversationalRetrievalChain

from langchain_openai import ChatOpenAI

# from langchain_community.callbacks.tracers.wandb import WandbRunArgs
from langchain_community.retrievers import KayAiRetriever

from params import MODEL_NAME#, WANDB_PROJECT_NAME

try:
    from keys import OPEN_AI_KEY, KAYAI_API_KEY, WANDB_API_KEY

    env = 'local'
except ModuleNotFoundError:
    OPEN_AI_KEY, KAYAI_API_KEY, WANDB_API_KEY = st.secrets["OPEN_AI_KEY"], st.secrets["KAYAI_API_KEY"], st.secrets[
        "WANDB_API_KEY"]
    env = 'remote'

os.environ["KAY_API_KEY"] = KAYAI_API_KEY
os.environ["WANDB_API_KEY"] = WANDB_API_KEY


class Chat(object):
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.chat_history = []
        # self.tracer = WandbTracer(
        #     run_args=WandbRunArgs(project=WANDB_PROJECT_NAME, save_code=False,
        #                           config={'model_name': MODEL_NAME, 'env': env},
        #                           id=self.id, resume='allow', tags=[env])
        # )

        model = ChatOpenAI(model_name=MODEL_NAME, openai_api_key=OPEN_AI_KEY, temperature=0.0)
        self.qa = ConversationalRetrievalChain.from_llm(model,
                                                        retriever=self.get_retriever,
                                                        return_source_documents=True,
                                                        # callbacks=[self.tracer]
                                                        )

    # def __del__(self):
    #     self.tracer.finish()
    #     del self

    @property
    def get_retriever(self):
        retrievers = [
            KayAiRetriever.create(
                dataset_id="company",
                data_types=st.session_state.data_scope,  # which filings should be in-scope for generating response?
                num_contexts=6  # 6 is max
            )
        ]
        return retrievers[0]

    def generate_response(self, question, retries=1):
        self.qa.retriever = self.get_retriever
        try:
            result = self.qa({"question": question, "chat_history": self.chat_history})
            self.chat_history.append((question, result["answer"], result['source_documents']))
        except Exception as e:
            st.error(f':warning: An error occurred: {str(e)}. Re-trying {retries} more time(s)')
            retries -= 1
            if retries > 0:
                self.generate_response(question, retries=retries)
            else:
                st.error(f':warning: An error occurred: {str(e)}. Not retrying again :( - '
                         f'attempts exhausted, please refresh the page. If that doesn\'t work, please contact the '
                         f'developer')


def add_linebreak_to_text(text, max_chars_per_line=50):
    split = text.split(" ")
    nchars = 0
    out_text = ""
    for word in split:
        if nchars >= max_chars_per_line:
            out_text += "\n"
            nchars = 0
        out_text += word + " "
        nchars += len(word) + 1
    return out_text


def show_history():
    # Display chat messages from history on app rerun
    if 'chat' not in st.session_state:
        return

    for question, result, source_documents in st.session_state.chat.chat_history:
        # Question
        with st.chat_message("user"):
            st.code(add_linebreak_to_text(question), language=None)
        # Response
        with st.chat_message("assistant"):
            st.code(add_linebreak_to_text(result), language=None)
        # Source documents
        with st.expander(":newspaper: Show sources", expanded=False) as expander:
            tabs = st.tabs([f":newspaper: {i + 1}" for i in range(len(source_documents))])
            for i, tab in enumerate(tabs):
                doc = source_documents[i]
                tab.subheader(doc.metadata['title'])
                pub_date_str = pd.to_datetime(doc.metadata['data_source_publish_date']).strftime(format='%b %-d, %Y')
                tab.text(add_linebreak_to_text(doc.page_content),
                         help=f'SEC published date: {pub_date_str}')
                tab.write("Click to open [SEC filing]({})".format(doc.metadata['data_source_link']))
                tab.divider()


def question_form():
    with st.form('my_form'):
        # User selects which datasets should be in scope. Currently, Kay.ai is limited to these document types:
        available_data = ["10-K", "10-Q", "8-K", "PressRelease"]
        st.multiselect("Filings to use", options=available_data, default=available_data, key="data_scope")

        if 'chat' not in st.session_state:
            st.session_state.chat = Chat()

        # Question entry box
        text = st.text_area('Ask a question:', 'What was Microsoft\'s revenue in fiscal year 2022?')
        submitted = st.form_submit_button('Submit')
        if not OPEN_AI_KEY.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        if submitted and OPEN_AI_KEY.startswith('sk-'):
            with st.status("Thinking...") as status:
                st.session_state.chat.generate_response(text)
                status.update(label="Done", state="complete", expanded=False)


if __name__ == "__main__":
    st.image('logo.png', width=300)
    history_row = st.container()
    question_form_row = st.container()

    with question_form_row:
        question_form()
    with history_row:
        show_history()



