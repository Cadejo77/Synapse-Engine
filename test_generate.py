import argparse
import os
from procedural_prompt_graph import Preset, Context, expand_key
import random

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset_dir", required=True, help="Path to presets/default folder")
    ap.add_argument("--entry", default="0_master_generator.yaml")
    ap.add_argument("--key", default="template")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--sep", default="\n\n")
    ap.add_argument("--strip_meta", action="store_true")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    preset = Preset(args.preset_dir)
    entry_stem = os.path.splitext(args.entry)[0]

    ctx = Context(
        rng=random.Random(args.seed),
        strip_meta=args.strip_meta,
        sep_text=args.sep,
        active_tags=set(),
        debug_lines=[] if args.debug else [],
    )

    prompt = expand_key(preset, ctx, entry_stem, args.key)
    print("PROMPT:\n")
    print(prompt)
    if args.debug:
        print("\n\nDEBUG:\n")
        print("\n".join(ctx.debug_lines))
        print("\nActive tags:\n", ", ".join(sorted(ctx.active_tags)))

if __name__ == "__main__":
    main()
