import subprocess
import json
import os
from pathlib import Path


class SynapsePromptGenerator:
    """
    A ComfyUI custom node that generates prompts using the Synapse Engine.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                "output_format": (["text", "json"], {"default": "text"}),
                "seed": ("INT", {"default": -1}),
            },
            "optional": {
                "custom_root": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_prompt"
    CATEGORY = "text/synapse"
    
    def __init__(self):
        # Get the path to this node's directory
        self.node_dir = Path(__file__).parent
        
    def generate_prompt(self, count, output_format, seed, custom_root=""):
        """
        Generate prompts using the Synapse Engine JavaScript generator.
        """
        try:
            # Build the command
            cmd = ["node", str(self.node_dir / "dist" / "index.js")]
            cmd.extend(["--count", str(count)])
            
            if output_format == "json":
                cmd.append("--json")
            
            if custom_root:
                cmd.extend(["--root", custom_root])
            else:
                cmd.extend(["--root", str(self.node_dir)])
            
            # Set environment for reproducible results if seed is provided
            env = os.environ.copy()
            if seed >= 0:
                env['SEED'] = str(seed)
            
            # Run the Synapse Engine
            result = subprocess.run(
                cmd,
                cwd=self.node_dir,
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode != 0:
                error_msg = f"Synapse Engine failed: {result.stderr}"
                print(f"[Synapse Engine] Error: {error_msg}")
                return (error_msg,)
            
            output = result.stdout.strip()
            
            if output_format == "json":
                try:
                    # Parse JSON and extract prompts
                    data = json.loads(output)
                    if isinstance(data, list) and len(data) > 0:
                        # Return the first prompt if multiple generated
                        return (data[0].get('prompt', output),)
                    else:
                        return (output,)
                except json.JSONDecodeError:
                    return (output,)
            else:
                # For text format, extract just the prompt part (skip metadata)
                lines = output.split('\n')
                prompts = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('---') and not line.startswith('Warnings:'):
                        # Remove metadata tags from the beginning
                        if '/' in line:
                            # Find where the actual prompt starts after metadata tags
                            # Metadata tags are in format /key:value/
                            parts = line.split(' ')
                            prompt_parts = []
                            
                            for part in parts:
                                if part.startswith('/') and part.endswith('/'):
                                    # This is a metadata tag, skip it
                                    continue
                                else:
                                    # This is part of the prompt
                                    prompt_parts.append(part)
                            
                            if prompt_parts:
                                clean_prompt = ' '.join(prompt_parts)
                                prompts.append(clean_prompt)
                            else:
                                # Fallback if no clean parts found
                                prompts.append(line)
                        else:
                            prompts.append(line)
                
                if prompts:
                    return (prompts[0],)  # Return first prompt
                else:
                    return (output,)  # Fallback to raw output
                    
        except Exception as e:
            error_msg = f"Error running Synapse Engine: {str(e)}"
            print(f"[Synapse Engine] Error: {error_msg}")
            return (error_msg,)


# ComfyUI Node Registration
NODE_CLASS_MAPPINGS = {
    "SynapsePromptGenerator": SynapsePromptGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SynapsePromptGenerator": "Synapse Prompt Generator"
}