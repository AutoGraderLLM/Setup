# Command to check if ollama IP or API is working 
curl http://127.0.0.1:11434

# Command to list all the ollama models installed


ollama list

# Command to make a model from a model file example. Same command to update existing model


ollama create name-of-model -f the-location-of-modelfile

example: ollama create cody -f phase2.modelfile

# Command to run a model best case to test model by asking questions with have a script


ollama run model-name

example: ollama run llama3.1
