# Chatbot for Rothenburg Kriminalmuseum

<!-- Add banner here -->
![Banner](https://www.ometrics.com/blog/wp-content/uploads/2017/12/chat_bot-01.jpg)

<!-- If repo goes public
![GitHub last commit](https://img.shields.io/github/last-commit/bISSKRAFT/marketing_chatbot)
-->

# Table of Contents

- [Chatbot for Rothenburg Kriminalmuseum](#chatbot-for-rothenburg-kriminalmuseum)
- [Installation](#installation)
- [Usage](#usage)

# :warning:Installation
[(Back to top)](#table-of-contents)

> **Note**: the chatbot is based on rasa and has specific version requirements

<br />

**1. First you have to clone the repository with git**
```shell
git clone git@github.com:bISSKRAFT/marketing_chatbot.git
```

<br />

**2. When using pip: Now you have to create a Python virtual environment. [create env](https://docs.python.org/3/library/venv.html)**
> **Note**: the environment python version has to be 3.8.12

<br />

**3. Install the required packages using the ```requirements.txt```**

 &nbsp; A. Install the packages in your created virtual environment using pip
   
```shell
pip install -r requirements.txt
``` 
<br />

&nbsp; B. If you are using conda you can create an environment with the required packages in one go
    
```shell
conda create --name <env_name> --file requirements.txt
```

<br />

**4. Activate your virtual environment**
 
&nbsp; A. using pip:
 
```shell
source /path/to/venv/bin/activate
```

<br />

&nbsp; B. using conda:

```shell
conda activate <env_name>
```


# :rocket:Usage
[(Back to top)](#table-of-contents)

There are two components that have to be in sync. First is the "Server Side" which handels the computation and the "Client Side" which handels the requests.

### :abacus:Server Side

**For using the chatbot there are two steps necessary**

> **Note**: It is recommended to first start the chatbot then the action server

- starting the chatbot itself:
  
```shell
rasa run -m models --enable-api --cors "*" --debug
```

- starting the action server for executing custom actions:

```shell
rasa run actions
```

- to use the chatbot in a website make sure in ```credentials.yml``` is socketio commented out

```yml
socketio:
 user_message_evt: user_uttered
 bot_message_evt: bot_uttered
 session_persistence: false
```

### :computer:Client Side

to use the chatbot on your website include the follwing HTML-file

```html
<div id="rasa-chat-widget" data-websocket-url="http://localhost:5005"></div>
<script src="https://unpkg.com/@rasahq/rasa-chat" type="application/javascript"></script>
```

> **Note**: make sure the IP-Adress and Port are equal to the ones used on the Server Side

