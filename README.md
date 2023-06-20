<!-- Add banner here -->

# Chatbot for Rothenburg Kriminalmuseum

<!-- If repo goes public
![GitHub last commit](https://img.shields.io/github/last-commit/bISSKRAFT/marketing_chatbot)
-->

# Table of Contents

- [Chatbot for Rothenburg Kriminalmuseum](#chatbot-for-rothenburg-kriminalmuseum)
- [Installation](#installation)

# Installation
[(Back to top)](#table-of-contents)

> **Note**: the chatbot is based on rasa and has specific version requirements

<br />

**1. First you have to clone the repository with git**
```shell
git clone git@github.com:bISSKRAFT/marketing_chatbot.git
```

<br />
<br />

**2. When using pip: Now you have to create a Python virtual environment. [create env](https://docs.python.org/3/library/venv.html)**
> **Note**: the environment python version has to be 3.8.12

<br />
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


# RUN

- to start the server with connection to the front end

```
rasa run -m models --enable-api --cors "*" --debug
```

- in the widet you have to use the correct url
- you have to change the ip adress to the right one
- if you don't want specify a port leave it default

```
http://localhost:5005
```

# TRAINING
**to train on a specific GPU please use**

```
export CUDA_VISIBLE_DEVICES=X
```
- x is the GPU you want to invoke

# Important Commands

```
rasa shell
```
- opens up a shell in which you can interact with the chatbot
- the chatbot respons with the contents of the "utter_*" action

```
rasa shell nlu
```

- opens up a shell in which you can interact with the chatbot
- the response is the possibility of the intent and the corresponding action

```
rasa interactive
```

- opens up a shell for interaction
- asks if the output is the desired or not
- and if the action was the right one
- can be used for interactive learning


