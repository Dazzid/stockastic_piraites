# Welcome to KSPR Stochastic Pirate Radio! 🏴‍☠️🏴‍☠️🏴‍☠️ 🦜
This is the main repository for the Stochastic Piraites Radio. 

To download the Mistral model 
- https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF	
  
Choose:
- mistral-7b-v0.1.Q4_K_M.gguf	Q4_K_M	4	4.37 GB	6.87 GB	medium, balanced quality - recommended
- mistral-7b-v0.1.Q5_K_M.gguf	Q5_K_M	5	5.13 GB	7.63 GB	large, very low quality loss - recommended (it doesn't work well)

Libraires:
Torch, torchvision and torchaudio

- pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
- pip3 install transformers==4.31.0
- pip install ctransformers
- pip install pydub
