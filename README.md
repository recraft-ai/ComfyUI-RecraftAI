# ComfyUI-RecraftAI
<p align="center"><img src="./assets/logo.png" alt="Recraft AI Logo" width="200"></p>

This is a custom node for ComfyUI that allows you to use the Recraft AI API. Recraft V3 (code-named red_panda) is a text-to-image model with the ability to generate long texts, images in a wide list of styles, including custom brand styles. It's also possible to set up brand colors. As of today, it is SOTA in image generation, proven by Hugging Face’s industry-leading Text-to-Image Benchmark by Artificial Analysis.

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

### RecraftAI Image To Image Transformer

This node is used to transform an input image into an output image given a text prompt.

### RecraftAI Background Remover

This node is used to remove background of an image.

### RecraftAI Crisp Upscaler

This node is used to enhance an image using ‘crisp upscale’ tool, increasing image resolution, making the image sharper and cleaner.

### RecraftAI Creative Upscaler

This node is used to enhance an image using ‘creative upscale’ tool, boosting resolution with a focus on refining small details and faces.

### RecraftAI Background Replacer

This node is used to detect and replace background of an image according to a given text prompt.

### RecraftAI Inpainter

This node is used to modify specific parts of an image according to mask and text prompt. You should use ComfyUI mask for an input mask. Note, that pixels with mask values >= 0.5 will be filled based on the prompt, while others will keep intact.

## API Documentation

For more information about the Recraft AI API, follow [the documentation](https://www.recraft.ai/docs).

## Pricing

For pricing, follow [Recraft AI Pricing](https://www.recraft.ai/docs#pricing).
