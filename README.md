<a href="https://github.com/bISSKRAFT/marketing_chatbot/tree/develop" target="_blank">
    <img src="https://img.shields.io/github/last-commit/navendu-pottekkat/nsfw-filter?style=flat-square" alt="GitHub last commit">
</a>

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


