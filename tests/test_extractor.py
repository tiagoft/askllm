

def test_extractor_init():
    from askllm.extract import Extractor
    extractor = Extractor()
    assert extractor.model is not None
    assert extractor.prompt is not None
    
def test_extractor_any_prompt():
    from askllm.extract import Extractor
    extractor = Extractor()
    prompt = "What is 2 + 2?"
    result = extractor.any_prompt(prompt)
    assert result is not None
    
# def test_extractor_extract():
#     from askllm.extract import Extractor
#     extractor = Extractor()
#     texto = "Eu gosto muito de ética e acho que a ética é super legal!"
#     resultado = extractor.extract(texto)
#     assert resultado is not None