import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional
import webbrowser
from bs4 import BeautifulSoup  # NEW for parsing YouTube


def _get_edge_path():
    """Find Microsoft Edge executable path"""
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        raise FileNotFoundError("Microsoft Edge not found on this system.")
    return edge_path


@function_tool()
async def open_youtube(
    context: RunContext,  
    query: str = ""
) -> str:
    """
    Open YouTube in Microsoft Edge and auto-play the first video for the given query.
    """
    logging.info(f"Tool called: open_youtube(query='{query}')")
    try:
        edge_path = _get_edge_path()
        webbrowser.register("edge", None, webbrowser.BackgroundBrowser(edge_path))

        if query:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Try to grab the first video link
                for link in soup.find_all("a", href=True):
                    if "/watch?v=" in link["href"]:
                        video_url = f"https://www.youtube.com{link['href']}"
                        webbrowser.get("edge").open(video_url)
                        return f"Opened YouTube and playing '{query}' in Microsoft Edge."
            # fallback: just open search page
            webbrowser.get("edge").open(search_url)
            return f"Opened YouTube search for '{query}' in Microsoft Edge."
        else:
            webbrowser.get("edge").open("https://www.youtube.com")
            return "YouTube homepage opened in Microsoft Edge."
    except Exception as e:
        logging.error(f"Error in open_youtube: {e}")
        return f"Failed to open YouTube in Edge: {e}"


@function_tool()
async def open_instagram(
    context: RunContext  
) -> str:
    """
    Open Instagram in Microsoft Edge.
    """
    logging.info("Tool called: open_instagram()")
    try:
        edge_path = _get_edge_path()
        webbrowser.register("edge", None, webbrowser.BackgroundBrowser(edge_path))
        webbrowser.get("edge").open("https://www.instagram.com")
        return "Instagram opened in Microsoft Edge."
    except Exception as e:
        logging.error(f"Error in open_instagram: {e}")
        return f"Failed to open Instagram: {e}"


# ---------------- Weather Tool ----------------
@function_tool()
async def get_weather(
    context: RunContext,  
    city: str
) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 


# ---------------- Web Search Tool ----------------
@function_tool()
async def search_web(
    context: RunContext,  
    query: str
) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."    


# ---------------- Email Tool ----------------
@function_tool()    
async def send_email(
    context: RunContext,  
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    """
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # App Password only!

        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."
        
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject

        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())
        server.quit()

        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"
