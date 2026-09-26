# unsloth MUST be imported before transformers / trl / peft
from unsloth import FastLanguageModel

import sys
import importlib.metadata as md

import torch


def ver(pkg: str) -> str:
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return "NOT INSTALLED"


print(f"python        {sys.version.split()[0]}")
for p in ["torch", "transformers", "peft", "trl", "bitsandbytes", "triton", "unsloth"]:
    print(f"{p:<13} {ver(p)}")

assert torch.cuda.is_available(), "CUDA not visible to PyTorch. Fix this before continuing."
props = torch.cuda.get_device_properties(0)
print(f"gpu           {props.name}  {props.total_memory / 2**30:.1f} GiB")

# Smoke-test model only. The final base model is chosen at the baseline milestone.
model, tok = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    max_seq_length=2048,
    load_in_4bit=True,
    dtype=None,  # auto-pick (bf16 on your RTX 4050)
)
print(f"4-bit model loaded. VRAM allocated: {torch.cuda.memory_allocated() / 2**30:.2f} GiB")

# LoRA with the project's starting numbers (r=16, attention + MLP projections)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)
model.print_trainable_parameters()

# One forward + backward pass at 1024 tokens: the real training memory path
torch.cuda.reset_peak_memory_stats()
model.train()
x = torch.randint(0, 150000, (1, 1024), device="cuda")
out = model(input_ids=x, labels=x)
out.loss.backward()
print(f"fwd+bwd OK at 1024 tokens. loss={out.loss.item():.2f}  peak VRAM={torch.cuda.max_memory_allocated() / 2**30:.2f} GiB")

# Inference sanity check
FastLanguageModel.for_inference(model)
msgs = [{"role": "user", "content": "Say hello in one short sentence."}]
inputs = tok.apply_chat_template(
    msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True
).to("cuda")
gen = model.generate(**inputs, max_new_tokens=30, do_sample=False, use_cache=True)
print("reply:", tok.decode(gen[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))