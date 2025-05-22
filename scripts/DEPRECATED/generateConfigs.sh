#!/bin/bash

# 生成 betaThal 測試樣本
python configGenerator.py \
 -d ../functions/test/THAL_files/betaThal \
 -p '.ab1' \
 -t thalassemia_test_data \
 -s betaThal \
 -o ../configs/beta_thal_testing_sample.json

# 生成 HBB Mutant 測試樣本
python configGenerator.py \
 -d ../functions/test/THAL_files/HBB_Mutant \
 -p '.ab1' \
 -t thalassemia_test_data \
 -s HBB_Mutant \
 -o ../configs/hbb_mutant_testing_sample.json

# 生成 HBB Wild type 測試樣本
python configGenerator.py \
 -d ../functions/test/THAL_files/HBB_Wild_type \
 -p '.ab1' \
 -t thalassemia_test_data \
 -s HBB_Wild_type \
 -o ../configs/hbb_wild_type_testing_sample.json

# 生成 Low signal 測試樣本
python configGenerator.py \
 -d ../functions/test/THAL_files/Low_signal \
 -p '.ab1' \
 -t thalassemia_test_data \
 -s Low_signal \
 -o ../configs/sanger_low_signal_testing_sample.json

# 生成 Non_HBB_Sanger 測試樣本
python configGenerator.py \
 -d ../functions/test/THAL_files/Non_HBB_Sanger \
 -p '.ab1' \
 -t thalassemia_test_data \
 -s Non_HBB_Sanger \
 -o ../configs/non_hbb_sanger_testing_sample.json

# 生成 Non_HBB_high_bg 測試樣本
python configGenerator.py \
 -d ../functions/test/THAL_files/Non_HBB_HighBG \
 -p '.ab1' \
 -t thalassemia_test_data \
 -s Non_HBB_HighBG \
 -o ../configs/non_hbb_highbg_testing_sample.json