# Ollama Model Directory

This directory contains the configuration for ASL AI models using Ollama.

## Modelfile

The `Modelfile` contains the configuration for the ASL model, based on Llama2:
- Uses a lower temperature (0.2) for more focused and predictable responses
- Configured with a system prompt specific to ASL interpretation

## Usage

To build and run the model locally with Ollama:

```bash
cd asl_model_training_hub/ollama
ollama create asl-model -f Modelfile
ollama run asl-model
```

This creates a custom Ollama model that's optimized for ASL interpretation.