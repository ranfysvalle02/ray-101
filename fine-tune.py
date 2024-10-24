import pytorch_lightning as pl
import torch
from torch import nn
from torch.utils.data import DataLoader, random_split, TensorDataset
import numpy as np
from sklearn.datasets import make_classification
from ray import tune
from ray.tune.integration.pytorch_lightning import TuneReportCallback
from ray.tune.schedulers import ASHAScheduler


# Step 1: Generate synthetic data
def generate_synthetic_data(n_samples=1000, n_features=20, n_classes=2):
    X, y = make_classification(n_samples=n_samples, n_features=n_features, n_informative=10, 
                               n_classes=n_classes, random_state=42)
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)


# Step 2: Define a Lightning DataModule for the synthetic data
class SyntheticDataModule(pl.LightningDataModule):
    def __init__(self, batch_size=32):
        super(SyntheticDataModule, self).__init__()
        self.batch_size = batch_size

    def setup(self, stage=None):
        X, y = generate_synthetic_data()
        dataset = TensorDataset(X, y)
        self.train, self.val = random_split(dataset, [800, 200])

    def train_dataloader(self):
        return DataLoader(self.train, batch_size=self.batch_size)

    def val_dataloader(self):
        return DataLoader(self.val, batch_size=self.batch_size)


# Step 3: Define a simple model
class SimpleModel(pl.LightningModule):
    def __init__(self, input_dim=20, hidden_size=64, learning_rate=1e-3):
        super(SimpleModel, self).__init__()
        self.save_hyperparameters()

        self.model = nn.Sequential(
            nn.Linear(input_dim, self.hparams.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hparams.hidden_size, 2)  # 2 output classes
        )

        self.criterion = nn.CrossEntropyLoss()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)


# Step 4: Define the training function for Ray Tune
def train_tune(config, num_epochs=10):
    model = SimpleModel(hidden_size=config["hidden_size"], learning_rate=config["learning_rate"])
    data_module = SyntheticDataModule()

    trainer = pl.Trainer(
        max_epochs=num_epochs,
        callbacks=[TuneReportCallback({"loss": "train_loss"}, on="train_end")],  # Use TuneReportCallback
        enable_progress_bar=False,  # Disabling the progress bar for cleaner output
        log_every_n_steps=10  # Log more frequently to avoid the logging interval warning
    )
    trainer.fit(model, datamodule=data_module)


# Step 5: Set up Ray Tune's hyperparameter search space and run the tuning process
search_space = {
    "hidden_size": tune.choice([32, 64, 128]),
    "learning_rate": tune.loguniform(1e-4, 1e-2)
}

scheduler = ASHAScheduler(
    max_t=10,  # Max number of epochs per trial
    grace_period=1,  # Early stopping grace period
    reduction_factor=2  # Halve the number of trials after each step
)

# Run the hyperparameter tuning process with Ray Tune
tuner = tune.run(
    tune.with_parameters(train_tune, num_epochs=10),
    resources_per_trial={"cpu": 1, "gpu": 0},  # Adjust according to available resources
    config=search_space,
    metric="loss",
    mode="min",
    num_samples=10,  # Number of random samples in hyperparameter search
    scheduler=scheduler
)

# Print the best hyperparameters found
print("Best hyperparameters found were: ", tuner.best_config)
"""
Best hyperparameters found were:  {'hidden_size': 128, 'learning_rate': 0.0021063786370817267}
"""
