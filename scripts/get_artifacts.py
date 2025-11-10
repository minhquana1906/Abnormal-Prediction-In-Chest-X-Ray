import wandb

run = wandb.init()
artifact = run.use_artifact(
    "minhquana-university-of-transportation-and-communication/chest-xray-abnormality-detection/run_wxzus486_model:v0",
    type="model",
)
artifact_dir = artifact.download()
