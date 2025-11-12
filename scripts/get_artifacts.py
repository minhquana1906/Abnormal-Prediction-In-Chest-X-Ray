import wandb

run_light = wandb.init()
artifact_light = run_light.use_artifact(
    "minhquana-university-of-transportation-and-communication/chest-xray-abnormality-detection/run_ivmzqro0_model:v0",
    type="model",
)
artifact_dir = artifact_light.download()


run_hard = wandb.init()
artifact_hard = run_hard.use_artifact(
    "minhquana-university-of-transportation-and-communication/chest-xray-abnormality-detection/run_8rmuzba0_model:v0",
    type="model",
)
artifact_dir = artifact_hard.download()

run_baseline = wandb.init()
artifact_baseline = run_baseline.use_artifact(
    "minhquana-university-of-transportation-and-communication/chest-xray-abnormality-detection/run_bzu6cp8g_model:v0",
    type="model",
)
artifact_dir = artifact_baseline.download()
