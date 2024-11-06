from .recraft_nodes import (
    Client,
    ImageGenerator,
    BackgroundRemover,
    ClarityUpscaler,
    GenerativeUpscaler,
)

NODE_CLASS_MAPPINGS = {
    'RecraftClient': Client,
    'RecraftImageGenerator': ImageGenerator,
    'RecraftBackgroundRemover': BackgroundRemover,
    'RecraftClarityUpscaler': ClarityUpscaler,
    'RecraftGenerativeUpscaler': GenerativeUpscaler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'RecraftClient': 'RecraftAI Client',
    'RecraftImageGenerator': 'RecraftAI Image Generator',
    'RecraftBackgroundRemover': 'RecraftAI Background Remover',
    'RecraftClarityUpscaler': 'RecraftAI Clarity Upscaler',
    'RecraftGenerativeUpscaler': 'RecraftAI Generative Upscaler',
}
