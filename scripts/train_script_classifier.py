"""
scripts/train_script_classifier.py

Real transfer-learning training loop for the script classifier
(ResNet18 backbone, replaced classification head, fine-tuned on
data/script_classification/{train,validation}). Requires `torch` and
`torchvision` to be installed and a populated dataset directory — see
docs/datasets.md. Produces models/script_classifier/model.pt, consumed by
app.ai.script_classifier.TransferLearningScriptClassifier.

Usage:
    python scripts/train_script_classifier.py --epochs 10 --data-dir data/script_classification
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/script_classification")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--output", default="models/script_classifier/model.pt")
    args = parser.parse_args()

    train_dir = os.path.join(args.data_dir, "train")
    val_dir = os.path.join(args.data_dir, "validation")

    if not os.path.isdir(train_dir):
        print(f"Training data not found at {train_dir}.")
        print("Populate it first — see docs/datasets.md — then re-run this script.")
        return

    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader
        from torchvision import datasets, models, transforms
    except ImportError:
        print("torch/torchvision are not installed. Install them (see requirements.txt) to train.")
        return

    from app.ai.script_classifier import SUPPORTED_SCRIPTS

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )

    train_ds = datasets.ImageFolder(train_dir, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)

    val_loader = None
    if os.path.isdir(val_dir):
        val_ds = datasets.ImageFolder(val_dir, transform=transform)
        val_loader = DataLoader(val_ds, batch_size=args.batch_size)

    model = models.resnet18(weights="IMAGENET1K_V1")
    model.fc = nn.Linear(model.fc.in_features, len(SUPPORTED_SCRIPTS))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        msg = f"Epoch {epoch + 1}/{args.epochs} — train loss: {total_loss / len(train_loader):.4f}"

        if val_loader:
            model.eval()
            correct = total = 0
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    preds = outputs.argmax(dim=1)
                    correct += (preds == labels).sum().item()
                    total += labels.size(0)
            msg += f" — val accuracy: {correct / total:.3f}" if total else ""

        print(msg)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    torch.save(model, args.output)
    print(f"Saved trained model to {args.output}")


if __name__ == "__main__":
    main()
