import os
import folder_paths
from comfy.sd import load_lora_for_models
from comfy.utils import load_torch_file
import comfy.sd

class CheckpointLoaderWithOptionalLoRAs:
    def __init__(self):
        self.loaded_loras = [None, None, None]

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "model_name")
    OUTPUT_TOOLTIPS = ("U-Net model (denoising latents)", "CLIP (Contrastive Language-Image Pre-Training) model (encoding text prompts)", "VAE (Variational autoencoder) model (latent<->pixel encoding/decoding)", "checkpoint name")
    FUNCTION = "load_checkpoint_with_loras"

    CATEGORY = "loaders"
    DESCRIPTION = "Loads checkpoint model and optionally applies up to three LoRAs"

    @classmethod
    def INPUT_TYPES(cls):
        lora_list = folder_paths.get_filename_list("loras")
        lora_list = ["None"] + lora_list  
        
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "Checkpoint to load"}),
            },
            "optional": {
                # LoRA 1
                "enable_lora1": ("BOOLEAN", {"default": False, "tooltip": "Enable or disable the first LoRA"}),
                "lora_name1": (lora_list, {"default": "None", "tooltip": "First LoRA to apply"}),
                "lora_strength1": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01, "tooltip": "Strength for first LoRA"}),
                
                # LoRA 2
                "enable_lora2": ("BOOLEAN", {"default": False, "tooltip": "Enable or disable the second LoRA"}),
                "lora_name2": (lora_list, {"default": "None", "tooltip": "Second LoRA to apply"}),
                "lora_strength2": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01, "tooltip": "Strength for second LoRA"}),
                
                # LoRA 3
                "enable_lora3": ("BOOLEAN", {"default": False, "tooltip": "Enable or disable the third LoRA"}),
                "lora_name3": (lora_list, {"default": "None", "tooltip": "Third LoRA to apply"}),
                "lora_strength3": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01, "tooltip": "Strength for third LoRA"}),
            }
        }

    def load_and_apply_lora(self, model, clip, lora_name, strength, lora_index):
        if lora_name == "None":
            return model, clip
            
        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = None
        
        # Check if we already have this LoRA loaded
        if self.loaded_loras[lora_index] is not None:
            if self.loaded_loras[lora_index][0] == lora_path:
                lora = self.loaded_loras[lora_index][1]
            else:
                # Free memory from previous LoRA
                temp = self.loaded_loras[lora_index]
                self.loaded_loras[lora_index] = None
                del temp

        # Load the LoRA if needed
        if lora is None:
            lora = load_torch_file(lora_path, safe_load=True)
            self.loaded_loras[lora_index] = (lora_path, lora)
            
        # Apply the LoRA
        model_lora, clip_lora = load_lora_for_models(model, clip, lora, strength, strength)
        print(f"\033[34m[CheckpointLoaderWithLoRAs] Loaded LoRA: {lora_name} with strength: {strength}\033[0m")
        return model_lora, clip_lora

    def load_checkpoint_with_loras(self, ckpt_name, 
                                  enable_lora1=False, lora_name1="None", lora_strength1=1.0,
                                  enable_lora2=False, lora_name2="None", lora_strength2=1.0,
                                  enable_lora3=False, lora_name3="None", lora_strength3=1.0):
        # Load the checkpoint
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, 
                                                  embedding_directory=folder_paths.get_folder_paths("embeddings"))
        
        model, clip, vae = out[:3]
        
        # Apply LoRAs if enabled
        if enable_lora1 and lora_name1 != "None":
            model, clip = self.load_and_apply_lora(model, clip, lora_name1, lora_strength1, 0)
            
        if enable_lora2 and lora_name2 != "None":
            model, clip = self.load_and_apply_lora(model, clip, lora_name2, lora_strength2, 1)
            
        if enable_lora3 and lora_name3 != "None":
            model, clip = self.load_and_apply_lora(model, clip, lora_name3, lora_strength3, 2)
        
        # Return with the checkpoint name
        return (model, clip, vae, ckpt_name)