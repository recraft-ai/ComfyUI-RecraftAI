# ComfyUI-RecraftAI
<p align="center"><img src="./assets/logo.png" alt="Recraft AI Logo" width="200"></p>

This is a custom node for ComfyUI that allows you to use the Recraft AI API. XXXXXXXXXXXX

## Requirements

Before using this node, you need to have a Recraft AI API key. To generate a key, log in to Recraft, and enter [API page](https://www.recraft.ai/profile/api) and hit 'Generate' (available only if your API units balance is above zero).

## Installation

### Installing manually

1. Navigate to the `ComfyUI/custom_nodes` directory.

2. Clone this repository: `git clone https://github.com/recraft-ai/ComfyUI-RecraftAI.git`
   The files should be located as `ComfyUI/custom_nodes/ComfyUI-RecraftAI/*`, where `*` represents all the files in this repo.
  
3. Install the dependencies:
  - Windows (ComfyUI portable): `.\python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\ComfyUI-RecraftAI\requirements.txt`
  - Linux or MacOS: `cd ComfyUI-RecraftAI && pip install -r requirements.txt`

4. If you don't want to expose your key, you can add it into the `config.ini` file and keep it empty in the node.

5. Start ComfyUI and enjoy using the Recraft AI API node!

## Nodes

### RecraftAI Client

This node is used to create a Recraft AI client.

### RecraftAI Image Generator

This node is used to generate an image given a text prompt.

## API Documentation

For more information about the Recraft AI API, follow [the documentation](https://www.recraft.ai/docs).

## Pricing

For pricing, follow [Recraft AI Pricing](https://www.recraft.ai/docs#pricing).
