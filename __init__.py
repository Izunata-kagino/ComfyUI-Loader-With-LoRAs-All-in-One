from .checkpoint_loader_with_loras import CheckpointLoaderWithOptionalLoRAs

NODE_CLASS_MAPPINGS = {
    "CheckpointLoaderWithOptionalLoRAs": CheckpointLoaderWithOptionalLoRAs
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckpointLoaderWithOptionalLoRAs": "Checkpoint Loader with Optional LoRAs"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]