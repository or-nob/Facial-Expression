python data.py ./Data/data.zip
python tune.py ./Data/Train/Under_90_min_tuning/data.zip ./Data/Validation/Validation_10_percent/data.zip
python train.py ./Data/Train/Best_hyperparameter_80_percent/data.zip ./hyperparameter.txt
python test.py ./Data/Test/Test_10_percent/data.zip ./model.h5