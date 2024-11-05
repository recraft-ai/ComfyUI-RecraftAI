from .recraft_nodes import (
    Client,
    ImageGenerator,
    BackgroundRemover,
)

NODE_CLASS_MAPPINGS = {
    'RecraftClient': Client,
    'RecraftImageGenerator': ImageGenerator,
    'RecraftBackgroundRemover': BackgroundRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'RecraftClient': 'RecraftAI Client',
    'RecraftImageGenerator': 'RecraftAI Image Generator',
    'RecraftBackgroundRemover': 'RecraftAI Background Remover',
}
