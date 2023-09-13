# matterbridge-custom-notifier

[matterbridge](https://github.com/42wim/matterbridge) is a bridge between mattermost, IRC, gitter, xmpp, slack, discord, telegram, rocketchat, twitch, ssh-chat, zulip, whatsapp, keybase, matrix, microsoft teams, nextcloud, mumble, vk and more with REST API (mattermost not required!) written in GO.

[matterbridge-custom-notifier](https://github.com/t0mer/matterbridge-custom-notifier) is a [Homeassistant ](https://www.home-assistant.io/) custom notification component that enables us to send notification to Whatsapp groups using the Matterbridge gateway and without the need to register to 3rd party integrator or the official Whatsapp cloud API.

## Limitations
* When using your own number to send the notifications it will act like your are sending messages to yourself. that way no alert will popup. Consider using other phone number for that.

## Getting started

### Get WhatsApp group id (JID) from WhatsApp web
You will also need to fid the jid (Group identifier) of the group you want to send the notifications to. You can get the JID from WhatsApp web.

Open WhatsApp web and navigate to the relevant group:
![Whatsapp web](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/smart_home_group.png?raw=true)

Open Developer tools, click the inspect toll and click on one of the messages:
![Developer tools](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/jid.png?raw=true)

In the data-id you will see string that looks like that: **true_1203631xxxxxxxxx @g.us_3EB072082B43E417EA35_xxxxxxxxxxxx@c.us**.
Copy the part that start right after **true_** and ends with **@g.us**. this is the JID you will need.


### Setting up matterbridge
First, create a new firectory named matterbridge under /opt and download the matterbridge pre-compiled binary:

* [Linux ARM](https://matter.techblog.co.il/linux_arm/matterbridge)
* [Linux ARM64](https://matter.techblog.co.il/linux_arm64/matterbridge)
* [Linux x86_x64](https://matter.techblog.co.il/linux_amd_x86_x64/matterbridge).

Alternatively, you can compile matterbridge accordingly to your system OS and CPU architecture. You can find the instructions here [Matterbridge](https://github.com/42wim/matterbridge#installing--upgrading)


Next, create a file named matterbridge.toml and place it in the same directory with the binary file.

Add the following text to the file:

```toml
[general]
LogFile="/var/log/matterbridge.log" #Path to log file
IconURL="https://github.com/identicons/{NICK}.png" #Create avatar from github if user does not have one
PreserveThreading=true
ShowUserTyping=false
ShowJoinPart=false
NoSendJoinPart=false

[api.myapi]
BindAddress="0.0.0.0:4242" #Set API bind address and port
Buffer=1000 
RemoteNickFormat="{NICK} "
Token="Add you own token" #Optional, secure the api endpoint with strong token

[whatsapp.bridge]
# Number you will use as a relay bot. Tip: Get some disposable sim card, don't rely on your own number.
Number="+xxxxxxxxxxxx"
# First time that you login you will need to scan QR code, then credentials willl be saved in a session file
# If you won't set SessionFile then you will need to scan QR code on every restart
# optional (by default the session is stored only in memory, till restarting matterbridge)
SessionFile="session-xxxxxxxxxxxx.gob"
# If your terminal is white we need to invert QR code in order for it to be scanned properly
# optional (default false)
QrOnWhiteTerminal=false
# Messages will be seen by other WhatsApp contacts as coming from the bridge. Original nick will be part of the message.
#RemoteNickFormat="@{NICK}: "
RemoteNickFormat="{NICK}: "
# extra label that can be used in the RemoteNickFormat
# optional (default empty)
Label="Organization"


[[gateway]]
name="gateway1"
enable=true

    [[gateway.out]] #Set as out - send the message to this group
    account="whatsapp.bridge"
    channel="xxxxxxxxxxx@g.us"


    [[gateway.in]] #Set the API as in, receive message from the api 
    account="api.myapi"
    channel="api"

```

Now, run matterbridge (If you get a permission errors, run chmod +x matterbridge to give execute permissions).
If everything goes well, you should see a QR code. Go to the whatsapp app and under Linked devices scan it:

![QR Code](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/qr.png?raw=true)

After a successfull scan, you will see it in the linked devices list under the name **whatsmeow** which is the library that matterbridge is based on.

![Linked devices](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/linked_devices.png?raw=true)

### Set matterbridge to start on system startup
As for now, this version of matterbridge that supports multi devices can be installed as System service and I'm working in a docker container version.

To add matterbridge as system service, run the following command:
```bash
nano /etc/systemd/system/matterbridge.service
```
and paste the following text:

```
[Unit]
Description=Matterbridge daemon
After=network-online.target

[Service]
WorkingDirectory=/opt/matterbridge
Type=simple
User=root
ExecStart=/opt/matterbridge/matterbridge -conf /opt/matterbridge/matterbridge.toml
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target

```
 Save the file and enable it by running the following commands:

```bash
 systemctl enable matterbridge
 systemctl status matterbridge
```

And to verify that the servie is running, run the following command:
```bash
systemctl status matterbridge
```
The output should look like this

```
● matter.service - Matterbridge daemon
   Loaded: loaded (/etc/systemd/system/matter.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2023-09-05 10:24:12 UTC; 6 days ago
 Main PID: 9486 (matterbridge)
    Tasks: 6 (limit: 4915)
   CGroup: /system.slice/matter.service
           └─9486 /opt/matterbridge/matterbridge -conf /opt/matterbridge/matterbridge.toml

Sep 11 16:51:02 pub-api matterbridge[9486]: 16:51:02.534 [Client WARN] Error decrypting message from 972546683213@s.whatsapp.net in xxxxxxxxxx-1628582008@g.us: failed to decrypt group message: no send
```

You can also view the log by running
```bash
tail -f /var/log/matterbridge.log
```

## Add the custom notifier to homeassistant
To add matterbridge reposiroty to HACS, Open you Homeassistant application and navigate to HACS:

![HACS](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/hacs.png?raw=true)

Then click on Integrations:

![Integrations](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/integrations.png?raw=true)

On the upper right corner, click the three dots and select Custom repositories:

![Custom repositories](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/custom_repos.png?raw=true)

Under repository, paste the following address: **https://github.com/t0mer/matterbridge-custom-notifier**

And Under category, select Integration:

![Repo details](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/repo_details.png?raw=true)

And click **ADD**.

You can now see that the *Matterbridge" was added to the custom repositories list:
![Custom Repo Added](https://github.com/t0mer/matterbridge-custom-notifier/blob/main/screenshots/repo_added.png?raw=true)

Tou can now add matterbridge custom component from HACS.

## Configure homeassistant to use matterbridge.
First, afetr the custom component installation, make sure you restarted home assistant.

### configuration.yaml
To work with matterbridge, add the following code to your configuration.yaml file:
```yaml

notify:
  - platform: matterbridge
    name: #Firendly name for the application
    nickname: #The name for the sender that appears in the message
    url: #URL for the matterbridge API. the url should end with "/api/message"
    token: #The token you entered in the matterbridge configuration file.
```

Save the file and restart Home-assistant.

### Sending test notification
In Home assistant, under Developer tools go to services and find matterbridge notification service. 

Insert the following lines:

```yaml
service: notify.matter_whatsapp_notifire
data:
  title: #Title for the message (Required!)
  message: #Message to send
    target: #Gateway name from the matterbridge configuration file
```
And click *Call Service*


# Notes
* Matterbridge is not officially supported by Whatsapp. It's an open source written in GO.
* In the matterbridge configuration you can add many gateways to send notifications to different groups by using multiple gateways. This is the reason that you can specify gateway name as target in the payload.
