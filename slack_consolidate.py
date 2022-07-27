import time
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from supabase import create_client, Client
logger = logging.getLogger(__name__)
from datetime import datetime
from dotenv import dotenv_values
config = dotenv_values(".env")
bot_client = WebClient(token=config['SLACK_BOT_TOKEN'])
client = WebClient(token=config['SLACK_TOKEN'])
SUPABASE_URL=config['SUPABASE_URL']
SUPABASE_KEY=config['SUPABASE_KEY']
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
SLACK_ORG = config['SLACK_ORG']
SLACK_ORG_LINK = f"https://{SLACK_ORG}.slack.com/archives/"
############
# Config: 
############
# 1.4 seconds should be the minimum to avoid passing Slack API limits.
# https://api.slack.com/docs/rate-limits#tier_t3
POOLING_DELAY = 1.4  
# Check if new channels were added each hour.
SCAN_CHANNELS_DELAY = 3600.0

class SlackChannel:
  def __init__(self, id, name, p_level, dest_channel_id, dest_channel, private):
    """_summary_

      Args:
          id (str): Slack channel ID from the source channel
          name (str): Name of the source channel (used in logging)
          p_level (str): (Optional message) added when posting
          dest_channel_id (str): Slack channel ID for the destination channel
          dest_channel (str): Name of the destination channel (used in logging)
          private (int): Integer to check if the channel is private (private==1) or public channel
      Returns:
          SlackChannel: object
    """
    self.id = id
    self.name = name
    self.p_level = p_level
    self.dest_channel = dest_channel
    self.dest_channel_id  = dest_channel_id
    self.private  = private

def setup():
    """_summary_
        Fetches the list of channels from Supabase and returns them in a dict()
    Returns:
        dict: Dictionary with SlackChannel objects. 
    """
    channels = dict()
    data = supabase.table("slack_channels").select("channel_id, channel, p_level, dest_channel, dest_channel_id, private").execute().data
    data_dic = data
    for row in data_dic:
        channels[row['channel_id']] = SlackChannel(id = row['channel_id'],
        name = row['channel'],
        p_level = row['p_level'],
        dest_channel = row['dest_channel'],
        dest_channel_id = row['dest_channel_id'],
        private = row['private'])
    return channels

def post( src_channel, link, message):
    """_summary_
        Post a message from a source channel into the destination channel
    Args:
        src_channel (SlackChannel): SlackChannel object
        link (_type_): The link of the message in slack
        message (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        aux_text = ""
        if src_channel.private != 1:
            aux_text = ("Message on <#"+src_channel.id+
                ">. "+src_channel.p_level+" \n"+link)
        else:
            aux_text = ("Message on <#"+src_channel.id+
                ">."+src_channel.p_level+" \n"+message+" \n"+link)
        result = bot_client.chat_postMessage(
                channel= src_channel.dest_channel_id, 
                text=aux_text
                )
        logger.info(result)
    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")

def ts_to_strtime(ts):
    """_summary_
        Converts the UNIX time in timestamp to ISO format.
    Args:
        ts (int): TS datetime

    Returns:
        str: ISO format datetime string for compatibility with Postgres.
    """
    aux_ts = int(ts)
    return str(datetime.utcfromtimestamp(aux_ts).isoformat())

def loop_through_channels(channels):
    """_summary_
        Loop through the channels and post messages on postgres if they aren't cached. 
    Args:
        channels (dict): dict() with SlackChannel objects 
    """
    for channel_id in channels:
        channel = channels[channel_id]
        conversation_history = []
        try:
            result = client.conversations_history(channel=channel.id, limit = 20)
            conversation_history = result["messages"]
            logger.info("{} messages found in {}".format(len(conversation_history), id))
        except SlackApiError as e:
            logger.error("Error creating conversation: {}".format(e))
        for message in conversation_history:
            try:
                msg_dic = dict()
                msg_dic['channel_name'] = channel.name
                msg_dic['channel_id'] = channel.id
                aux_msg = "<@"+message['user']+"> wrote: \n"
                msg_dic['message'] = aux_msg + message['text']
                ts_aux  = message['ts'].split(".")
                msg_dic['ts'] = ts_to_strtime(ts_aux[0])
                msg_dic['ts_ms'] = ts_aux[1]
                supabase.table("slack_watcher").insert(msg_dic).execute()
                auxint = ts_aux[0]+ts_aux[1]
                auxint = auxint.replace(".","")
                link = SLACK_ORG_LINK+channel.id+"/p"+auxint
                post(channel, link, msg_dic['message'])
            except Exception as e:
                pass
        time.sleep(POOLING_DELAY)

def main():
    """_summary_
        Main loop to infinitely keep pooling data from channels and posting on Slack. 
        It also checks for new channels every hour. 
    """
    channels = setup()
    start = time.time()
    while True:
        end = time.time()
        if ((end - start) > SCAN_CHANNELS_DELAY):
            start = time.time()
            channels = setup()
        else:
            loop_through_channels(channels)

if __name__ == '__main__':
    main()