import json
import os
from pathlib import Path
from typing import Tuple, Union
import logging

import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as skm
from scipy.interpolate import interp1d
from scipy.optimize import brentq

LOGGER = logging.getLogger(__name__)

def compute_roc_auc_eer(y_true, y_pred, exp_name) -> Tuple[float, float]:
    # Compute the ROC curve and the AUC
    fpr, tpr, thresholds = skm.roc_curve(y_true, y_pred, pos_label=1)
    roc_auc = skm.auc(fpr, tpr)
    # Compute the Equal Error Rate (EER)
    fnr = 1 - tpr
    # Ref: https://stackoverflow.com/a/46026962
    eer = fpr[np.nanargmin(np.absolute((fnr - fpr)))]
    printROC(fpr, tpr, roc_auc, exp_name)
    return roc_auc, eer


def alt_compute_eer(y_true, y_pred) -> float:
    # Ref: https://github.com/scikit-learn/scikit-learn/issues/15247#issuecomment-542138349
    fpr, tpr, thresholds = skm.roc_curve(y_true, y_pred, pos_label=1)
    LOGGER.info(f"fpr: {fpr}")
    fpr = np.nan_to_num(fpr, nan=0)
    LOGGER.info(f"fpr: {fpr}")
    LOGGER.info(f"tpr: {tpr}")
    LOGGER.info(f"thresholds: {thresholds}")
    eer = brentq(lambda x: 1.0 - x - interp1d(fpr, tpr)(x), 0.0, 1.0)
    return eer


def printROC(fpr, tpr, roc_auc, exp_name):
    LOGGER.info(f"Printing ROC for {exp_name}")
    plt.figure()
    plt.plot(fpr, tpr, label="ROC curve (area = %0.2f)" % roc_auc)
    plt.plot([1, 0], [0, 1], "k--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver operating characteristic")
    plt.legend(loc="lower right")
    # plt.show()
    plt.savefig(exp_name + '.png')


def main():
    np.random.seed(0)

    # Load the data
    y_true = np.random.randint(2, size=500)
    y_pred = np.random.randint(2, size=500)

    # Compute the ROC curve and the AUC
    fpr, tpr, thresholds = skm.roc_curve(y_true, y_pred, pos_label=1)
    roc_auc = skm.auc(fpr, tpr)
    # Compute the Equal Error Rate (EER)
    fnr = 1 - tpr
    eer = fpr[np.nanargmin(np.absolute((fnr - fpr)))]
    print(f"EER: {eer:.3f}")

    # Plot the ROC curve
    plt.figure()
    plt.plot(fpr, tpr, label="ROC curve (area = %0.2f)" % roc_auc)
    plt.plot([1, 0], [0, 1], "k--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver operating characteristic")
    plt.legend(loc="lower right")
    plt.show()


def compute_metrics_for_file(
    filename: Union[str, Path],
    exp_name
) -> Tuple[float, float, float, float, float]:
    filepath: Path = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"File {filepath} does not exist.")
    with filepath.open("r") as f:
        data = json.load(f)

    total_analyzed_elements: int = len(data["y_true"])
    total_analyzed_positive: int = data["y_true"].count(1)
    total_analyzed_negative: int = total_analyzed_elements - total_analyzed_positive
    cm = skm.confusion_matrix(data["y_true"], data["y_pred"])
    tn, fp, fn, tp = cm.ravel().tolist()
    tn = tn / total_analyzed_negative
    fp = fp / total_analyzed_negative
    fn = fn / total_analyzed_positive
    tp = tp / total_analyzed_positive
    acc: float = skm.accuracy_score(data["y_true"], data["y_pred"])
    f1: float = skm.f1_score(data["y_true"], data["y_pred"])
    eer: float = alt_compute_eer(data["y_true"], data["y_pred"])
    roc_auc, eer2 = compute_roc_auc_eer(data["y_true"], data["y_pred"], exp_name)

    return acc, f1, roc_auc, eer, eer2, tn, fp, fn, tp


def compute_all():
    save_dir = Path(__file__).parent / "saved"
    export_md = save_dir / "README.md"
    export_html = save_dir / "table.html"
    result = {}

    for exp_name in os.listdir(save_dir):
        pred_filepath = save_dir / exp_name / "best_pred.json"
        if not pred_filepath.is_file():
            continue

        acc, f1, roc_auc, eer, eer2, tn, fp, fn, tp = compute_metrics_for_file(pred_filepath, exp_name)

        result[exp_name] = dict(
            acc=f"{acc:.3f}",
            f1=f"{f1:.3f}",
            roc_auc=f"{roc_auc:.4f}",
            eer=f"{eer:.4f}",
            eer2=f"{eer2:.4f}",
            tn=f"{tn:.3f}",
            fp=f"{fp:.3f}",
            fn=f"{fn:.3f}",
            tp=f"{tp:.3f}",
        )

    md_to_write = [
        "# Empirical Results",
        " ",
        "-   Accuracy",
        "-   F1 score",
        "-   Area Under the Receiver Operating Characteristic Curve (ROC AUC)",
        "-   Equal Error Rate (EER)",
        " ",
        "| Experiment | Accuracy | F1 Score | ROC AUC | EER | EER2 | True negatives | False positives | False negatives | True positives |",
        "| :--------- | :------: | :------: | :-----: | :-: | :--: | :--: | :--: | :--: | :--: |",
    ]

    for exp_name in sorted(result.keys(), key=lambda x: result[x]["f1"]):
        d = result[exp_name]
        md_to_write.append(
            f"| {exp_name} | {d['acc']} | {d['f1']} | {d['roc_auc']} | {d['eer']} | {d['eer2']} | {d['tn']} | {d['fp']} | {d['fn']} | {d['tp']} |"
        )

    with export_md.open("w") as f:
        f.write("\n".join(md_to_write))
        print(f"Exported: {export_md}")

    html_to_write = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<style>table, th, td { border: 1px solid black; border-collapse: collapse; } th, td { padding: 10px; }</style>",
        "</head>",
        "<body>",
        "<h1>Empirical Results</h1>",
        '<table  class="table has-text-centered mx-auto">',
        '<thead><tr><td>Experiment</td><td>Accuracy</td><td><abbr title="F1 score">F1</abbr></td><td><abbr title="Area Under the Receiver Operating Characteristic Curve">ROC AUC</abbr></td><td><abbr title="Equal Error Rate">EER</abbr></td><td><abbr title="True negatives">TN</abbr></td><td><abbr title="False positives">FP</abbr></td><td><abbr title="False negatives">FN</abbr></td><td><abbr title="True positives">TP</abbr></td></tr></thead>',
        "</table>",
        "</body>",
        "</html>",
    ]

    for exp_name in sorted(result.keys(), key=lambda x: result[x]["f1"], reverse=True):
        d = result[exp_name]
        html_to_write.insert(
            9,
            f"<tr><td>{exp_name}</td><td>{d['acc']}</td><td>{d['f1']}</td><td>{d['roc_auc']}</td><td>{d['eer']}</td><td>{d['tn']}</td><td>{d['fp']}</td><td>{d['fn']}</td><td>{d['tp']}</td></tr>",
        )

    with export_html.open("w") as f:
        f.write("\n".join(html_to_write))
        print(f"Exported: {export_html}")


if __name__ == "__main__":
    compute_all()
