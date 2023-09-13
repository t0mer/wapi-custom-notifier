# wapi-custom-notifier

[whatsapp-api](https://github.com/chrishubert/whatsapp-api/) is a REST API wrapper for the [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) library, providing an easy-to-use interface to interact with the WhatsApp Web platform. It is designed to be used as a docker container, scalable, secure, and easy to integrate with other non-NodeJs projects.

[wapi-custom-notifier](https://github.com/t0mer/wapi-custom-notifier) is a [Homeassistant ](https://www.home-assistant.io/) custom notification component that enables us to send notification to Whatsapp groups using the whatsapp-api gateway and without the need to register to 3rd party integrator or the official Whatsapp cloud API.

## Limitations
* When using your own number to send the notifications it will act like your are sending messages to yourself. that way no alert will popup. Consider using other phone number for that.

## Getting started
### Setting up *whatsapp-api* 
1.  create *docker-compose.yaml* file and paste the following content:
```yaml
version: '3.8'

services:
  app:
    container_name: whatsapp_web_api
    image: chrishubert/whatsapp-web-api:latest # Pull the image from Docker Hub
    # restart: always
    ports:
      - "3000:3000"
    environment:
      #- API_KEY= #Optional - Recomended to enable when goint to prod
      - BASE_WEBHOOK_URL=http://localhost:3000/localCallbackExample
      - ENABLE_LOCAL_CALLBACK_EXAMPLE=FALSE # OPTIONAL, NOT RECOMMENDED TO ENABLE FOR PRODUCTION
      - MAX_ATTACHMENT_SIZE=5000000 # IN BYTES
      - SET_MESSAGES_AS_SEEN=FALSE # WILL NOT MARK THE MESSAGES AS READ AUTOMATICALLY
      # ALL CALLBACKS: auth_failure|authenticated|call|change_state|disconnected|group_join|group_leave|group_update|loading_screen|media_uploaded|message|message_ack|message_create|message_reaction|message_revoke_everyone|qr|ready|contact_changed
      - DISABLED_CALLBACKS=message_ack  # PREVENT SENDING CERTAIN TYPES OF CALLBACKS BACK TO THE WEBHOOK
      - ENABLE_SWAGGER_ENDPOINT=TRUE #When enabled, adding "/api-docs" to the url will open Swagger. Not recomended to production.
    volumes:
      - ./sessions:/usr/src/app/sessions # Mount the local ./sessions/ folder to the container's /usr/src/app/sessions folder
```

2. Run the Docker Compose:
```
docker-compose pull && docker-compose up
```

3. Visit http://localhost:3000/session/start/ABCD (Replace ABCD with your desired session name)

4. Scan the QR on your console using WhatsApp mobile app -> Linked Device -> Link a Device (it may take time to setup the session)

5. Visit http://localhost:3000/client/getContacts/ABCD (Replace ABCD with your desired session name)
This will list all the contacts and groups chats in json format:
```json
{
    "success": true,
    "contacts": [
        {
            "id": {
                "server": "g.us",
                "user": "xxxxxxxxxxxxxxxxxx",
                "_serialized": "xxxxxxxxxxxxxx@g.us"
            },
            "number": null,
            "isBusiness": false,
            "isEnterprise": false,
            "name": "AI XXXXX",
            "type": "in",
            "isMe": false,
            "isUser": false,
            "isGroup": true,
            "isWAContact": false,
            "isMyContact": false,
            "isBlocked": false
        }
    ]
}
```

6. EXTRA: Look at all the callbacks data in ./session/message_log.txt


## Add the custom notifier to homeassistant
To add wapi reposiroty to HACS, Open you Homeassistant application and navigate to HACS.

1. Then click on Integrations.

2. On the upper right corner, click the three dots and select Custom repositories.

3. Under repository, paste the following address: **https://github.com/t0mer/wapi-custom-notifier**

4. Under category, select Integration and click ADD.

5. You can now see that the *wapi" was added to the custom repositories list.

6. can now add wapi custom component from HACS.

## Configure homeassistant to use wapi.
First, afetr the custom component installation, make sure you restarted home assistant.

### configuration.yaml
To work with wapi, add the following code to your configuration.yaml file:
```yaml

notify:
  - platform: wapi
    name: wapi whatsapp notifire
    session: ABCD #Set your own session
    url: http://192.168.0.238:3000/client/sendMessage #Set the url configured in the whatsapp-api docker
    token: #Optional - This token shoukd be equel to the token you set in the whatsapp-api configuration.
```

Save the file and restart Home-assistant.

### Sending test notification
In Home assistant, under Developer tools go to services and find wapi notification service. 

Insert the following lines:

```yaml
service: notify.wapi_whatsapp_notifire
data:
  message: The garage door has been open for 10 minutes.
  title: Your Garage Door Friend
  target: xxxxxxxxxx@c.us #Can be contact or group chat id


```
And click *Call Service*


# Notes
* wapi is not officially supported by Whatsapp. It's an open source written in GO.
* In the wapi configuration you can add many gateways to send notifications to different groups by using multiple gateways. This is the reason that you can specify gateway name as target in the payload.
