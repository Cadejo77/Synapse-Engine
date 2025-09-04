# Frequently Asked Questions

## What is the difference between YAMLPromptMaster and regular chat?

This is one of the most common questions we receive. The key differences are:

### **Regular Chat Approach**
When you ask an AI assistant to generate prompts through conversation:
- **Inconsistent**: Each conversation produces different quality and style
- **Manual**: Requires you to specify details every time  
- **Limited**: Depends on AI's immediate creativity and your ability to describe what you want
- **No structure**: Results vary wildly in format and completeness
- **Time-consuming**: Each prompt requires a separate conversation

**Example regular chat:**
```
You: "Give me a fantasy character prompt"
AI: "A brave elven wizard with a staff"
```

### **YAMLPromptMaster Approach**  
This system uses structured data and algorithms to generate prompts:
- **Consistent**: Every prompt follows quality standards and comprehensive coverage
- **Automated**: Generate hundreds of professional prompts in seconds
- **Intelligent**: Uses weighted relationships, conflict resolution, and complexity budgets
- **Systematic**: Covers all dimensions (character, setting, style, composition) methodically  
- **Customizable**: Fine-tune every aspect through YAML configuration files

**Example YAMLPromptMaster output:**
```
/genre:dark_fantasy/ /rarity:epic/ /vibe:mystical/ /mode:compositional/ 
/type:figure/ /species:tiefling_ember/ /archetypes:stormcaller/ 
/physiques:sturdy/ /emotions:introspective/ /conditions:weathered/ 
/power_sources:arcane/ /gear_primary:longsword/ 
/gear_secondary:grapnel_spool/ /modifiers:living_ink_tattoos/ 

A epic sturdy tiefling_ember stormcaller empowered by arcane 
adorned with living_ink_tattoos longsword + grapnel_spool, 
introspective (weathered). 

Style: volcanic_ember_char, rim_high_contrast, digital_paint, 
subtle_depth_of_field, centered_subject
```

### **When to Use Each Approach**

**Use Regular Chat When:**
- You want a quick, simple prompt for casual use
- You have very specific requirements that need human-like interpretation
- You're brainstorming ideas and want conversational feedback

**Use YAMLPromptMaster When:**
- You need professional-quality, consistent prompts at scale
- You want comprehensive coverage of all creative dimensions
- You're doing serious creative work (art generation, game development, etc.)
- You want to customize and fine-tune prompt generation to your needs
- You need batch generation of many varied prompts

### **Bottom Line**
YAMLPromptMaster is like having a professional prompt engineer working 24/7, while regular chat is like asking a friend for suggestions. Both have their place, but for serious creative work, the structured approach provides far superior results.

---

## Other Common Questions

### How do I customize the prompts?
Edit the YAML files in the `config/` directory. Each file contains weighted entries that you can modify, add to, or remove.

### Can I add new categories?
Yes! Add new YAML files to the appropriate directory and update the `poolFiles` configuration in `src/configLoader.ts`.

### How does the complexity system work?
Each token has a complexity cost. The system uses a budget based on rarity level to ensure prompts don't become overwhelming while maintaining quality.

### What are the relationships?
The system understands that certain combinations work better together (e.g., certain species with specific archetypes) and weights them accordingly.

### How do I report issues or contribute?
Please open issues on the GitHub repository or submit pull requests with improvements.