import speech_recognition as sr
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('voice', 'en')  # English voice identifier
engine.runAndWait()
import time
import subprocess
import wikipediaapi
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import webbrowser

class VoiceAssistant:
    def __init__(self):
        # Text-to-speech settings
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("volume", 3)
        self.recognizer = sr.Recognizer()
        # Setting up Wikipedia with user_agent
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='VoiceAssistantApp (https://example.com) Contact: reza776m@gmail.com'
        )

    def speak(self, text):
        """Converts text to speech"""
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listens to user input"""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        
        try:
            # Speech recognition in English
            query = self.recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("I didn't understand. Please repeat.")
            return ""
        except sr.RequestError:
            print("Error connecting to the speech recognition service.")
            return ""

    def get_time(self):
        """Fetches and announces the current time"""
        now = datetime.now().strftime("%H %M")
        self.speak(f"The current time is {now}.")
    
    def get_date(self):
        """Fetches and announces the current date and day of the week"""
        now = datetime.now()
        day_of_week = now.strftime("%A")
        date_today = now.strftime("%B %d, %Y")
        self.speak(f"Today is {day_of_week}, {date_today}.")

    def get_weather(self, city):
        """Fetches the weather"""
        api_key = "Api_Key_From_Website"
        if not api_key:
            self.speak("Weather service API key is missing. Please configure it.")
            return
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Checks for HTTP errors
            data = response.json()
            if "main" in data:
                temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]
                self.speak(f"The temperature in {city} is currently {temp} degrees Celsius, with weather conditions being {weather}.")
            else:
                self.speak("Sorry, I couldn't retrieve weather details.")
        except requests.exceptions.HTTPError as http_err:
            self.speak("There was an error fetching the weather data.")
            print(f"HTTP error: {http_err}")
        except requests.exceptions.RequestException as req_err:
            self.speak("There was an error connecting to the weather service.")
            print(f"Request error: {req_err}")

    def search_wikipedia(self, query):

        """Searches Wikipedia"""
        page = self.wiki.page(query)
        if page.exists():
            summary = page.summary[:200]
            self.speak(summary)
        else:
            self.speak("No results were found on Wikipedia.")

    def play_on_youtube(self, song):
        """Searches and plays a song on YouTube"""
        query = song.replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={query}"
        self.speak(f"Playing {song} on YouTube.")
        webbrowser.open(url)

    def note(self):
        """Prompts user to speak a note and saves it to a file"""
        self.speak("What would you like to note down?")
        note_content = self.listen()  # Capture the note
        if note_content:
            with open("notes.txt", "a") as file:
                file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {note_content}\n")
            self.speak("Your note has been saved.")
        else:
            self.speak("I didn't catch that. Please try again.")

    def open_application(self, app_name):
        """Opens specified application if available on Ubuntu"""
        try:
            if "calculator" in app_name:  # Gnome calculator
                subprocess.Popen(["gnome-calculator"])
                self.speak("Opening Calculator.")
            elif "telegram" in app_name:  # Telegram
                subprocess.Popen(["/snap/bin/telegram-desktop"])
                self.speak("Opening Telegram.")
            elif "chrome" in app_name or "google chrome" in app_name:  # Google Chrome
                subprocess.Popen(["google-chrome"])
                self.speak("Opening Google Chrome.")
            elif "firefox" in app_name:  # Firefox
                subprocess.Popen(["firefox"])
                self.speak("Opening Firefox.")
            else:
                self.speak("Sorry, I cannot open that application.")
        except FileNotFoundError:
            self.speak("Application not found on this system.")
        except Exception as e:
            self.speak(f"An error occurred: {str(e)}")
    
    def search_digikala_product(self, product_name):
        """Searches for a product on Digikala and saves the link of the first result to a file."""
        base_url = "https://www.digikala.com/search/?q="
        search_url = base_url + product_name.replace(" ", "%20")
        
        try:
            response = requests.get(search_url, verify=False)
            response.raise_for_status()  # Check if the request was successful
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            product_tag = soup.find("a", {"class": "product-box-link"})
            if product_tag and 'href' in product_tag.attrs:
                product_link = "https://www.digikala.com" + product_tag["href"]
                
                # Save the link to a file
                with open("product_links.txt", "a") as file:
                    file.write(f"{product_name}: {product_link}\n")
                
                self.speak(f"The link to {product_name} has been saved.")
            else:
                self.speak("Sorry, I couldn't find the product on Digikala.")
        
        except requests.RequestException as e:
            self.speak("There was an error connecting to Digikala.")
            print(f"Error: {e}")
    
    def process_command(self, command):
        """Processes user input commands"""
        if "time" in command:
            self.get_time()
        elif "date" in command:
            self.get_date()
        elif "weather" in command:
            city = command.split("weather")[-1].strip()
            self.get_weather(city)
        elif "wikipedia" in command:
            query = command.split("wikipedia ")[-1].strip()
            self.search_wikipedia(query)
        elif "play" in command:
            song = command.split("play ")[-1].strip()
            self.play_on_youtube(song)
        elif "note" in command:
            self.note()
        elif "open" in command:
            app_name = command.split("open")[-1].strip()
            self.open_application(app_name)
        elif "search" in command:
            product_name = command.split("search for")[-1].strip()
            self.search_digikala_product(product_name)
        elif "goodbye" in command:
            self.speak("Goodbye! Have a nice day.")
            return False
        else:
            self.speak("I didn't understand, please say it again.")
        return True

    def start(self):
        """Main function for the voice assistant"""
        self.speak("Hello! How can I assist you?")
        while True:
            command = self.listen()
            if not self.process_command(command):
                break

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start()
