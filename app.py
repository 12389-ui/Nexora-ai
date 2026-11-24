import gradio as gr
import sqlite3
import pandas as pd
import os

db = sqlite3.connect("nexora.db",check_same_thread=False)

db.execute("CREATE TABLE IF NOT EXISTS plans (name TEXT PRIMARY KEY, monthly_price INTEGER, features TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, plan_name TEXT, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
db.execute("CREATE TABLE IF NOT EXISTS integrations (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, service_name TEXT, status TEXT)")

db.executemany("INSERT OR IGNORE INTO plans VALUES (?,?,?)",[("Free",0,"Basic AI tools"),("Pro",499,"Advanced AI tools and reports"),("Business",1499,"Team workspace and business tools")])
db.commit()

subscribe = lambda u,p: "Enter username first." if not u.strip() else (db.execute("INSERT INTO subscriptions (username,plan_name,status) VALUES (?,?,?)",(u.strip(),p,"Active")),db.commit(),f"Subscription saved for {u}: {p}")[-1]

connect_service = lambda u,s,a: "Enter username first." if not u.strip() else (db.execute("INSERT INTO integrations (username,service_name,status) VALUES (?,?,?)",(u.strip(),s,"Connected" if a=="Connect" else "Disconnected")),db.commit(),f"{s} status saved for {u}.")[-1]

plans_view = lambda: pd.read_sql_query("SELECT * FROM plans",db)
subscriptions_view = lambda: pd.read_sql_query("SELECT * FROM subscriptions ORDER BY id DESC",db)
integrations_view = lambda: pd.read_sql_query("SELECT * FROM integrations ORDER BY id DESC",db)

subscription_tab = gr.Interface(fn=subscribe,inputs=[gr.Textbox(label="Username"),gr.Dropdown(["Free","Pro","Business"],value="Free",label="Choose Plan")],outputs=gr.Textbox(label="Result"),title="Subscriptions")

integration_tab = gr.Interface(fn=connect_service,inputs=[gr.Textbox(label="Username"),gr.Dropdown(["Google Drive","Gmail","Slack","GitHub","Microsoft 365","Notion","OpenRouter"],label="Service"),gr.Radio(["Connect","Disconnect"],value="Connect",label="Action")],outputs=gr.Textbox(label="Result"),title="Integration Hub")

workspace_tab = gr.Interface(fn=lambda: (plans_view(),subscriptions_view(),integrations_view()),inputs=[],outputs=[gr.Dataframe(label="Plans"),gr.Dataframe(label="Subscriptions"),gr.Dataframe(label="Integrations")],title="Central Workspace")

app = gr.TabbedInterface([subscription_tab,integration_tab,workspace_tab],["Subscriptions","Integrations","Workspace"],title="Nexora AI")

app.launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT",7860)))
