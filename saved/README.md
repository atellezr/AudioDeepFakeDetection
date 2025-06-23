# Empirical Results
 
-   Accuracy
-   F1 score
-   Area Under the Receiver Operating Characteristic Curve (ROC AUC)
-   Equal Error Rate (EER)
 
| Experiment | Accuracy | F1 Score | ROC AUC | EER | EER2 | True negatives | False positives | False negatives | True positives |
| :--------- | :------: | :------: | :-----: | :-: | :--: | :--: | :--: | :--: | :--: |
| SimpleLSTM_mfcc_O | 0.320 | 0.484 | 0.3203 | 0.6100 | 0.9961 | 0.004 | 0.996 | 0.363 | 0.637 |
| MLP_lfcc_O | 0.500 | 0.666 | 0.4998 | 0.5001 | 0.9990 | 0.001 | 0.999 | 0.001 | 0.999 |
| MLP_mfcc_O | 0.500 | 0.667 | 0.5004 | 0.4998 | 0.9992 | 0.001 | 0.999 | 0.000 | 1.000 |
| ShallowCNN_mfcc_O | 0.501 | 0.667 | 0.5007 | 0.4996 | 0.9986 | 0.001 | 0.999 | 0.000 | 1.000 |
| TSSD_wave_O | 0.500 | 0.667 | 0.5000 | 0.5000 | 0.0000 | 0.000 | 1.000 | 0.000 | 1.000 |
| SimpleLSTM_lfcc_O | 0.518 | 0.675 | 0.5182 | 0.4907 | 0.9636 | 0.036 | 0.964 | 0.000 | 1.000 |
| ShallowCNN_lfcc_O | 0.528 | 0.679 | 0.5277 | 0.4857 | 0.9445 | 0.055 | 0.945 | 0.000 | 1.000 |
| WaveLSTM_wave_O | 0.531 | 0.680 | 0.5306 | 0.4841 | 0.9353 | 0.065 | 0.935 | 0.003 | 0.997 |
| WaveRNN_wave_O | 0.997 | 0.997 | 0.9969 | 0.0053 | 0.0053 | 0.995 | 0.005 | 0.001 | 0.999 |