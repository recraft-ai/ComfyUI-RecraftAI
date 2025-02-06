from .recraft_nodes import (
    Client,
    ImageGenerator,
    ImageToImageTransformer,
    BackgroundRemover,
    CrispUpscaler,
    CreativeUpscaler,
    BackgroundReplacer,
    Inpainter,
)

NODE_CLASS_MAPPINGS = {
    'RecraftClient': Client,
    'RecraftImageGenerator': ImageGenerator,
    'RecraftImageToImageTransformer': ImageToImageTransformer,
    'RecraftBackgroundRemover': BackgroundRemover,
    'RecraftClarityUpscaler': CrispUpscaler,
    'RecraftGenerativeUpscaler': CreativeUpscaler,
    'RecraftBackgroundReplacer': BackgroundReplacer,
    'RecraftInpainter': Inpainter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'RecraftClient': 'RecraftAI Client',
    'RecraftImageGenerator': 'RecraftAI Image Generator',
    'RecraftImageToImageTransformer': 'RecraftAI Image To Image Transformer',
    'RecraftBackgroundRemover': 'RecraftAI Background Remover',
    'RecraftClarityUpscaler': 'RecraftAI Crisp Upscaler',
    'RecraftGenerativeUpscaler': 'RecraftAI Creative Upscaler',
    'RecraftBackgroundReplacer': 'RecraftAI Background Replacer',
    'RecraftInpainter': 'RecraftAI Inpainter',
}
