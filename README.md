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
