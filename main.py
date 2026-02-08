import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load variables (needed if you run this locally, Render does this automatically)
load_dotenv()

# Your email configuration
sender_email = "blkalpha616@gmail.com"
sender_password = os.getenv('EMAIL_PASSWORD') # This pulls your 16-digit key from Render
receiver_email = "blkalpha616@gmail.com"

def send_report(report_content):
    """Function to send the AI agents' work to your email."""
    try:
        msg = MIMEText(report_content)
        msg['Subject'] = 'Daily AI Agent Report - Digital Property'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Connecting to Google's secure mail server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print("Success! The report has been sent to your email.")
    except Exception as e:
        print(f"Error sending email: {e}")
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def health_check():
    return "AI Agent is Running", 200

def run_flask():
    # Render gives us a 'PORT' automatically. This finds it.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# This runs the 'Fake Door' in the background so your AI can work
threading.Thread(target=run_flask, daemon=True).start()
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 1. LOAD YOUR PASSWORDS (API KEYS)
load_dotenv()

# 2. INITIALIZE SEARCH TOOL (The Scout's Eyes)
search_tool = SerperDevTool()

# 3. DEFINE THE AGENTS (The Squad)
scout = Agent(
    role='High-Ticket Arbitrage Scout',
    goal='Identify $5k-$20k freelance projects that can be automated with Micro-SaaS.',
    backstory='Expert at finding high-value technical gaps on platforms like Upwork.',
    tools=[search_tool],
    verbose=True
)

architect = Agent(
    role='SaaS Solutions Architect',
    goal='Design a lean Micro-SaaS blueprint (e.g., Supply Chain AI) for the client.',
    backstory='Specializes in creating profitable, scalable software logic.',
    verbose=True
)

developer = Agent(
    role='Senior Python Engineer',
    goal='Write the functional Python code for the Micro-SaaS MVP.',
    backstory='A coding prodigy focused on automation and efficiency.',
    verbose=True
)

# 4. DEFINE THE MISSIONS (The Tasks)
research_task = Task(
    description='Search for high-ticket freelance postings involving "Supply Chain Optimization" or "Freelance Automation Tools". Identify 3 specific client pain points.',
    expected_output='A report on 3 potential high-value arbitrage opportunities.',
    agent=scout,
output_file='research_report.md')

build_task = Task(
    description='Take the best opportunity and write a Python script for a Micro-SaaS that solves it.',
    expected_output='A fully functional Python script ready for deployment.',
    agent=developer,output_file='saas_script.py'
)

# 5. ASSEMBLE THE CREW
squad = Crew(
    agents=[scout, architect, developer],
    tasks=[research_task, build_task],
    process=Process.sequential,
    verbose=True
)

# 6. KICKOFF THE SQUAD
print("### ACTIVATING SUPER AI SQUAD ###")
result = squad.kickoff()
print("\n\n########################")
print("## SQUAD FINAL REPORT ##")
print(result)
