# SlackConsolidate
SlackBot to consolidate messages from several channels. You can read more about how to build and get this up and running in the page below:

[Slack Consolidate blog post](https://supabase.com/blog/slack-consolidate-slackbot-to-consolidate-messages?utm_source=github&utm_medium=social&utm_campaign=blog-content)

There is also a colab notebook that you can use to run and test the bot directly in the Colab notebook:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mansueli/SlackConsolidate/blob/main/SlackConsolidate_bot.ipynb)

## Bonus:
Setting up the SlackConsolidate bot as a service:
Edit the [slack_consolidate.service](https://github.com/mansueli/SlackConsolidate/blob/main/slack_consolidate.service) file to match the path where you have the python script.

>**Note** 
>: Default path is `/usr/bin/slack_consolidate.py`

### Creating the service:
Now you have to add this service file to the path `/etc/systemd/system/`.

Make sure the `slack_consolidate.py` is executable:

`sudo chmod +x /usr/bin/slack_consolidate.py`

### Running the service:
We run this code below to make the system aware of the changes:
`sudo systemctl daemon-reload`

Then we start the service (it will auto-start if the system reboots):
`sudo systemctl start slack_consolidate`

# License:
[Apache 2.0](https://github.com/mansueli/SlackConsolidate/blob/main/LICENSE) 
