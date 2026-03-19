import torch
from app.core.config import DEVICE

def get_hardware_report():
    report = {"device": DEVICE}
    if DEVICE == "cuda":
        report["gpu_name"] = torch.cuda.get_device_name(0)
        report["vram_available"] = torch.cuda.get_device_properties(0).total_memory
    return report

def print_startup_banner():
    report = get_hardware_report()
    print(f"🚀 Neural Engine Active on: {DEVICE.upper()}")
    if "gpu_name" in report:
        print(f"📟 GPU: {report['gpu_name']}")