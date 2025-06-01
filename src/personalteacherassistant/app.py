import gradio as gr
import os
from personalteacherassistant.auth import AuthManager
from personalteacherassistant.model import GPT      



# UI Gradio
class CustomChatbot:
    def __init__(self):
        
        self.auth = AuthManager()
        # GPT instance will be created after login
        self.model = None  


    def run(self):
        session = self.auth.get_session()

        with gr.Blocks() as demo:
            gr.Markdown("# 🔐 Secure LLM with Authentication")

            # Login page
            with gr.Group(visible=not session["authenticated"]) as login_page:
                username = gr.Textbox(label="Username", placeholder="Enter your username")
                password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                login_btn = gr.Button("Login")
                create_account_btn = gr.Button("Create Account")
                login_msg = gr.Textbox(interactive=False, show_label=False)

            # Account creation page
            with gr.Group(visible=False) as create_account_page:
                new_username = gr.Textbox(label="New Username", placeholder="Choose a username")
                new_password = gr.Textbox(label="New Password", placeholder="Choose a password", type="password")
                create_btn = gr.Button("Create")
                cancel_btn = gr.Button("Cancel")
                create_msg = gr.Textbox(interactive=False, show_label=False)

            # Chat page
            with gr.Group(visible=session["authenticated"]) as chat_page:
                user_info = gr.Markdown(lambda: f"✅ Logged in as: **{session['username']}**")
                chatbot = gr.Chatbot()
                msg = gr.Textbox(label="Message")
                send = gr.Button("Send")
                clear = gr.Button("Clear")
                logout_btn = gr.Button("Logout")

            # Callbacks
            def try_login(u, p):
                success, msg = self.auth.login(u, p)
                if success:
                    self.model = GPT(u)
                return (gr.update(visible=not success),
                        gr.update(visible=success),
                        msg)

            def try_logout():
                self.auth.logout()
                return gr.update(visible=True), gr.update(visible=False)

            def handle_send(message, history):
                if self.model:
                    response = self.model.sendMessage(prompt=message)
                    history.append((message, response))
                    return "", history
                return "", history

            def show_create_account():
                return gr.update(visible=False), gr.update(visible=True)

            def cancel_create_account():
                return gr.update(visible=True), gr.update(visible=False)

            def try_create_account(new_user, new_pass):
                try:
                    self.auth.add_user(new_user, new_pass)
                    return "✅ Account created successfully. You can now log in."
                except ValueError as e:
                    return f"❌ {str(e)}"

            # Event bindings
            login_btn.click(try_login, inputs=[username, password], outputs=[login_page, chat_page, login_msg])
            send.click(handle_send, inputs=[msg, chatbot], outputs=[msg, chatbot])
            clear.click(lambda: [], None, chatbot)
            logout_btn.click(try_logout, outputs=[login_page, chat_page])

            create_account_btn.click(show_create_account, outputs=[login_page, create_account_page])
            cancel_btn.click(cancel_create_account, outputs=[login_page, create_account_page])
            create_btn.click(try_create_account, inputs=[new_username, new_password], outputs=[create_msg])

        demo.launch()

def main():
    app = CustomChatbot()
    app.run()

if __name__ == "__main__":
    main()

