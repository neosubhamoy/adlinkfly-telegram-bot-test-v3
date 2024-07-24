from webserver import keep_alive
from dotenv import load_dotenv
from urllib.parse import quote
import json
import os
import re
import requests
import telebot

load_dotenv()   #load environment variables from .env file

API_KEY = os.environ.get('BOT_TOKEN') or os.getenv('BOT_TOKEN')
PROURL_KEY = os.environ.get('PROURL_TOKEN') or os.getenv('PROURL_TOKEN')
bot = telebot.TeleBot(API_KEY)

user_data = {}
WAITING_FOR_FILE_LINK = 1
WAITING_FOR_TITLE = 2


#function for Direct Link shortening API call
def shorten_link(link):
  try:
    r = requests.get(f'https://prourl.eu.org/api?api={PROURL_KEY}&url={link}&type=0')

    if r.status_code == 200:
      response = json.loads(r.text)
      return response['shortenedUrl']
    elif r.status_code == 520:
      return "Failed to process your request...!! Due to high server load. If you are facing this issue multiple times then please consider using our web interface insted, Sorry, for the inconvenience...!!"
    else:
      print(f'Request failed with status code: {r.status_code}')
      print(f'Response content: {r.text}')
      return None

  except Exception as e:
    print(f'An error occurred: {str(e)}')
    return None


#function for No URL Metadata shortening API call
def shorten_link_nometa(link):
  try:
    r = requests.get(f'https://prourl.eu.org/api?api={PROURL_KEY}&url={link}')

    if r.status_code == 200:
      response = json.loads(r.text)
      return response['shortenedUrl']
    elif r.status_code == 520:
      return "Failed to process your request...!! Due to high server load. If you are facing this issue multiple times then please consider using our web interface insted, Sorry, for the inconvenience...!!"
    else:
      print(f'Request failed with status code: {r.status_code}')
      print(f'Response content: {r.text}')
      return None

  except Exception as e:
    print(f'An error occurred: {str(e)}')
    return None


#function to Create StreamLinks Page via API call
def create_streamlinks_page(url, title):
  try:
    r = requests.post(f'https://stream.prourl.eu.org/api/create.php', json={"title": title, "url": url}, headers={'Content-Type': 'application/json'})

    if r.status_code == 201:
      response = json.loads(r.text)
      return response['link']
    else:
      print(f'Request failed with status code: {r.status_code}')
      print(f'Response content: {r.text}')
      return None
    
  except Exception as e:
    print(f'An error occurred: {str(e)}')
    return None


#function to check if the (UserInput) Link is Valid
def is_valid_url(link):
  url_regex = re.compile(
      r'^(?:http|ftp)s?://'
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
      r'localhost|'
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
      r'(?::\d+)?'
      r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  return url_regex.match(link)


#function to check if the (UserInput) Link is Valid with Video File extention
def is_valid_url_with_video_extension(url):
  valid_extensions = [
      '3g2', '3gp', 'asf', 'avi', 'divx', 'dv', 'f4v', 'flv', 'm1v', 'm2v', 'm2ts', 'm4v', 'mkv', 'mov', 
      'mp2', 'mp2v', 'mp4', 'mp4v', 'mpe', 'mpeg', 'mpeg1', 'mpeg2', 'mpeg4', 'mpg', 'mpg4', 'mts', 'mxf', 
      'ogg', 'ogm', 'ogv', 'qt', 'rm', 'rmvb', 'ts', 'vob', 'webm', 'wmv', 'iso'
  ]
  pattern = re.compile(
        r'^(https?|ftp)://'
        r'([a-zA-Z0-9.-]+)'
        r'(/[a-zA-Z0-9._~:/?#@!$&\'()*+,;=%-]+)+'
        r'\.(' + '|'.join(valid_extensions) + r')'
        r'$', re.IGNORECASE)
  return re.match(pattern, url) is not None


@bot.message_handler(commands=['start'])
def start(message):
  bot.reply_to(
      message,
      "🌟 Welcome to ProURL Link Shortener Bot...🙏 \n🌟 Shortening Links are now more Simpler! \n🌟 You\'re now all set to go...! Just send the links to shorten! too simple right...? \n🌟 To get more info use the command /help \n\n😇 For more Advanced Controls with Web Admin Panel please visit Our Website! and Sign-Up for your new account. Try it now...It\'s totally Free! you\'ll surely love it...!! \n\n\n🌐 Our Website: https://prourl.eu.org \n\n❤️ Powered by RoundWeb",
      parse_mode='Markdown',
      disable_web_page_preview=True)
  bot.send_message(
      message.chat.id,
      "Yay! I\'m too exited to see you..!!\nJust send me a link to see the magic..."
  )


@bot.message_handler(commands=['help'])
def help(message):
  bot.reply_to(
      message,
      "🌟 ProURL Bot Help and Support!\n\n💡 Commands:\n\n/start - Start the first conversation with bot and initialize the link shortening process\n\n/nometa - Used to shorten links without metadata. This feature also creates a separate Short Link Web Page!\n(Keep in Mind: Short link page may contain some Adult 18+ Ads, Use only if you are OK with that! Ads by Adsterra, ExoClick)\n\n/help - Used to view help and support info\n\n*By default the Link shortening method is set to Direct Shortening (with metadata). If you want to shorten links without metadata you need to use the /nometa command everytime you want to use this method!\n\n*Now main shortening url is changed to prourl.eu.org from myurl.ml (Signup on Prourl website now to use exclusive custom shorturls!)\n\nThat\'s it...!! You\'r all caught up...!!\n\n\n📧 Contact Us(Email): support@prourl.eu.org"
  )


@bot.message_handler(commands=['nometa'])
def handle_nometa_command(message):
  bot.send_message(
      chat_id=message.chat.id,
      text="Please send the link to shorten without URL metadata!")
  bot.register_next_step_handler(message, handle_link)

def handle_link(message):
  if is_valid_url(message.text):
    bot.send_message(message.chat.id, "Shortening! Please wait...")
    link = quote(message.text)    #urlencode the link
    shortened_link = shorten_link_nometa(link)    #shorten the link (No Metadata)
    if shortened_link:
      bot.reply_to(message,
                   "Link Metadata Removed!\n" + shortened_link,
                   parse_mode='Markdown',
                   disable_web_page_preview=True)
    else:
      bot.reply_to(message, 'Failed to shorten the link! Please try again...')
  else:
    bot.send_message(
        message.chat.id,
        "Invalid URL!\nPlease reuse the command /nometa to try again with a valid link..."
    )


@bot.message_handler(commands=['stream'])
def stream_command(message):
  chat_id = message.chat.id
  user_data[chat_id] = {'state': WAITING_FOR_FILE_LINK}
  bot.send_message(chat_id, "Please send the video file link to create a streamlinks page!")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]['state'] == WAITING_FOR_FILE_LINK)
def handle_file_link(message):
  chat_id = message.chat.id
  user_data[chat_id]['file_link'] = message.text
  user_data[chat_id]['state'] = WAITING_FOR_TITLE
  bot.reply_to(message, "Got the link! Now, please send the video title to display on the streamlinks page!")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]['state'] == WAITING_FOR_TITLE)
def handle_title(message):
  chat_id = message.chat.id
  file_link = user_data[chat_id].get('file_link')
  title = message.text

  del user_data[chat_id]
  handle_stream(message, file_link, title)

def handle_stream(message, file_link, title):
  if is_valid_url_with_video_extension(file_link):
    if len(title) > 100:
      bot.send_message(message.chat.id, "Title is too long! Max: 100 charecters!\nPlease reuse the command /stream to try again with a smaller title...")
    else:
      bot.send_message(message.chat.id, "Creating! Please wait...")
      streamlink = create_streamlinks_page(file_link, title)    #Create streamlinks page
      if streamlink:
        bot.send_message(message.chat.id,
                        "StreamLinks Page Created!\n" + streamlink,
                        parse_mode='Markdown',
                        disable_web_page_preview=True)
      else:
        bot.send_message(message.chat.id, 'Failed to create streamlinks page! Please try again...')
  else:
    bot.send_message(
        message.chat.id,
        "Invalid Video File URL!\nPlease reuse the command /stream to try again with a valid link..."
    )


@bot.message_handler(content_types=['text'])
def handle_text(message):
  if is_valid_url(message.text):
    bot.send_message(message.chat.id, "Shortening! Please wait...")
    link = quote(message.text)    #urlencode the link
    shortened_link = shorten_link(link)    #shorten the link (Direct Shortening)
    if shortened_link:
      bot.reply_to(message,
                   shortened_link,
                   parse_mode='Markdown',
                   disable_web_page_preview=True)
    else:
      bot.reply_to(message, 'Failed to shorten the link! Please try again...')
  else:
    bot.send_message(message.chat.id,
                     "Invalid URL!\nPlease send a valid link...!")


keep_alive()
bot.polling()
