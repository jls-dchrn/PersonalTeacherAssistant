import gradio as gr
import os
import json
from personalteacherassistant.auth import AuthManager
from personalteacherassistant.model import GPT      



# UI Gradio
class CustomChatbot:
    def __init__(self):
        
        self.auth = AuthManager()

        # Need login name to create those attributes
        self.model = None

    
    def run(self):
        session = self.auth.get_session()

        with gr.Blocks(theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🔐 Secure LLM with Authentication")

            """
            -------------------------------------------------------------------------------------------------
            First page, choose between login and creating an account.
            -------------------------------------------------------------------------------------------------
            """
            with gr.Group(visible=not session["authenticated"]) as first_page:
                first_page_label = gr.Markdown("# Identify yourself to connect to the Personal Teacher Assistant")
                first_page_login_btn = gr.Button("Login")
                first_page_create_account_btn = gr.Button("Create Account")

            """
            -------------------------------------------------------------------------------------------------
            Page to creating an account. Once done, access the chat page for the newly created account.
            Have a button to go to login if missclicked
            -------------------------------------------------------------------------------------------------
            """
            
            with gr.Group(visible=False) as create_account_page:
                new_username = gr.Textbox(label="New Username", placeholder="Choose a username")
                new_password = gr.Textbox(label="New Password", placeholder="Choose a password", type="password")
                create_btn = gr.Button("Create")
                login_instead = gr.Button("Login")
                create_msg = gr.Textbox(interactive=False, show_label=False)
            """
            -------------------------------------------------------------------------------------------------
            Page to login. Once done, access the chat page if password and username are correct.
            Have a button to go to create account page if missclicked
            --------    -----------------------------------------------------------------------------------------
            """
            with gr.Group(visible=False) as login_page:
                username = gr.Textbox(label="Username", placeholder="Enter your username")
                password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                login_btn = gr.Button("Login")
                create_account_instead = gr.Button("Create New Account")
                login_msg = gr.Textbox(interactive=False, show_label=False)
            
            """
            -------------------------------------------------------------------------------------------------
            Chat page, have access to your usual teacher assistant adapting to your pace rate.
            -------------------------------------------------------------------------------------------------
            """
            # Chat page
            with gr.Group(visible=session["authenticated"]) as chat_page:
                with gr.Row():
                    with gr.Column(scale=1):
                        history_label = gr.Markdown("### 💬 History")
                        history_selector = gr.Dropdown(label="Previous Sessions", choices=[], interactive=True)
                        load_history_btn = gr.Button("Load Selected")

                    with gr.Column(scale=4):
                        user_info = gr.Markdown(value="✅ Logged in as: ")
                        chatbot = gr.Chatbot()
                        msg = gr.Textbox(label="Message")
                        image_input = gr.File(label="Upload Images", file_types=[".jpg", ".jpeg", ".png"], file_count="multiple")
                        send = gr.Button("Send")
                        clear = gr.Button("Clear")
                        logout_btn = gr.Button("Logout")
                        save_session_title = gr.Textbox(label="Save Session As", placeholder="E.g. Fractions Lesson")
                        save_btn = gr.Button("Save Session")

            """
            -------------------------------------------------------------------------------------------------
                                                    Button functions
            -------------------------------------------------------------------------------------------------
            """
            def try_login(user, pwd):
                success, msg = self.auth.login(user, pwd)
                if success:
                    self.model = GPT(user)
                   
                return (gr.update(visible=not success),
                        gr.update(visible=success),
                        msg,
                        gr.update(value=f"✅ Logged in as: **{user}**"))

            def try_logout():   
                self.auth.logout()
                return gr.update(visible=True), gr.update(visible=False)


            def handle_send(message, history, images):
                if self.model:
                    img_paths = [img.name for img in images] if images else []
                    prompt, _ = self.model.process_prompt(prompt=message, image_paths=img_paths)
                    response = self.model.sendMessage(prompt=prompt, history=history)
                    history.append((message, response))
                    return "", None, history
                return "", None, history


            def false_true():
                return gr.update(visible=False), gr.update(visible=True)

            def true_false():
                return gr.update(visible=True), gr.update(visible=False)

            def try_create_account(new_user, new_pass):
                try:
                    self.auth.add_user(new_user, new_pass)
                    return "✅ Account created successfully. You can now log in."
                except ValueError as e:
                    return f"❌ {str(e)}"
                
            def save_session(title, history):
                if self.model and title and history:
                    self.model.save_chat_history(session["username"], title, history)
                    updated_titles = self.model.load_chat_titles(session["username"])
                    #return f"💾 Session saved as: {title}", gr.update(choices=updated_titles), []
                    return f"💾 Session saved as: {title}", gr.update(choices=updated_titles), [], gr.update(value="")

                return "⚠️ Please enter a title.", gr.update(), history

            def load_session(title):
                if self.model:
                    return self.model.load_chat_history(session["username"], title)
                return []

            def refresh_titles():
                if self.model:
                    return gr.update(choices=self.model.load_chat_titles(session["username"]))
                return gr.update(choices=[])

            def get_available_histories():
                if self.model:
                    return gr.update(choices=self.model.list_sessions())
                return gr.update(choices=[])



            """
            -------------------------------------------------------------------------------------------------
                                                    Event Biding
            -------------------------------------------------------------------------------------------------
            """
            
            # first page 
            first_page_login_btn.click(true_false, outputs=[login_page, first_page])
            first_page_create_account_btn.click(true_false, outputs=[login_page, first_page])
            
            # create_account page
            create_btn.click(try_create_account, inputs=[new_username, new_password], outputs=[create_msg])
            login_instead.click(true_false, outputs=[login_page, create_account_page])
           
            # login page
            login_btn.click(try_login, inputs=[username, password], outputs=[login_page, chat_page, login_msg, user_info])
            create_account_instead.click(false_true, outputs=[login_page, create_account_page])
                
            # chat page
            send.click(handle_send, inputs=[msg, chatbot, image_input], outputs=[msg, image_input, chatbot])
            clear.click(lambda: [], None, chatbot)
            logout_btn.click(try_logout, outputs=[login_page, chat_page])

            #save_btn.click(save_session, inputs=[save_session_title, chatbot], outputs=[login_msg, history_selector, chatbot])
            save_btn.click(save_session, inputs=[save_session_title, chatbot], outputs=[login_msg, history_selector, chatbot, save_session_title])

            load_history_btn.click(load_session, inputs=[history_selector], outputs=[chatbot])


        demo.launch()

def main():
    app = CustomChatbot()
    app.run()

if __name__ == "__main__":
    main()

