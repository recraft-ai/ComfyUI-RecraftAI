from .recraft_nodes import (
    Client,
    ImageGenerator,
    ImageToImageGenerator,
    BackgroundRemover,
    ClarityUpscaler,
    GenerativeUpscaler,
    BackgroundReplacer,
    Inpainter,
)

NODE_CLASS_MAPPINGS = {
    'RecraftClient': Client,
    'RecraftImageGenerator': ImageGenerator,
    'RecraftImageToImage': ImageToImageGenerator,
    'RecraftBackgroundRemover': BackgroundRemover,
    'RecraftClarityUpscaler': ClarityUpscaler,
    'RecraftGenerativeUpscaler': GenerativeUpscaler,
    'RecraftBackgroundReplacer': BackgroundReplacer,
    'RecraftInpainter': Inpainter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'RecraftClient': 'RecraftAI Client',
    'RecraftImageGenerator': 'RecraftAI Image Generator',
    'RecraftImageToImage': 'RecraftAI Image to Image',
    'RecraftBackgroundRemover': 'RecraftAI Background Remover',
    'RecraftClarityUpscaler': 'RecraftAI Clarity Upscaler',
    'RecraftGenerativeUpscaler': 'RecraftAI Generative Upscaler',
    'RecraftBackgroundReplacer': 'RecraftAI Background Replacer',
    'RecraftInpainter': 'RecraftAI Inpainter',
}
