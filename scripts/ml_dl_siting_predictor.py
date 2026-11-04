#!/usr/bin/env python3
"""
scripts/ml_dl_siting_predictor.py

Unified ML/DL Data Center Siting Predictor.
Implements, trains, evaluates, and compares:
1. Classical Baseline: Regularized Ridge Regression
2. Machine Learning: Random Forest Regressor
3. Machine Learning: XGBoost Gradient Boosted Trees
4. Machine Learning: LightGBM Gradient Boosted Trees
5. Deep Learning: Deep Multi-Layer Perceptron (MLP) Neural Network
6. Hybrid Super-Learner: Blended Stacking Ensemble (ML + DL)

Outputs:
- Cross-validation performance benchmark (R2, RMSE, MAE, Pearson r, Spearman rho)
- Feature Importance / Driver Analysis
- 36-State Siting Suitability Predictions & Tier Classifications -> clean/ml_dl_siting_predictions.csv
- Model Benchmark Summary -> clean/ml_dl_model_benchmarks.csv
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from sklearn.model_selection import KFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, VotingRegressor
from sklearn.neural_network import MLPRegressor
import xgboost as xgb
import lightgbm as lgb

MASTER_PATH = "clean/master_state_siting_panel.csv"
STAGE2_PATH = "clean/stage2_multiobjective_ranking.csv"
STAGE1_PATH = "clean/stage1_feasibility_results.csv"

OUT_PREDICTIONS = "clean/ml_dl_siting_predictions.csv"
OUT_BENCHMARKS = "clean/ml_dl_model_benchmarks.csv"
OUT_IMPORTANCES = "clean/ml_feature_importances.csv"

def build_feature_matrix():
    print("=" * 80)
    print("STAGE 3: UNIFIED ML & DL SITE SUITABILITY PREDICTOR")
    print("=" * 80)
    
    # Load data
    master_df = pd.read_csv(MASTER_PATH)
    stage2_df = pd.read_csv(STAGE2_PATH)
    stage1_df = pd.read_csv(STAGE1_PATH)
    
    print(f"Loaded Master Panel: {master_df.shape[0]} states/UTs, {master_df.shape[1]} features.")
    print(f"Loaded Stage 2 Multi-Objective Benchmark: {stage2_df.shape[0]} candidate states.")
    print(f"Loaded Stage 1 Hard Feasibility Mask: {stage1_df.shape[0]} states.")
    
    # Merge datasets
    merged = master_df.merge(
        stage2_df[['state_id', 'topsis_balanced', 'rank_balanced', 'is_pareto_optimal']],
        on='state_id',
        how='left'
    )
    merged = merged.merge(
        stage1_df[['state_id', 'is_enterprise_feasible', 'is_hyperscale_feasible', 'feasibility_status']],
        on='state_id',
        how='left'
    )
    
    # Feature selection across 5 strategic pillars
    feature_cols = [
        # 1. Grid & Transmission Capacity
        'substation_count_total',
        'substation_count_765kv_plus',
        'substation_count_400kv',
        'substation_count_220kv',
        'transformation_capacity_total_mva',
        'transformation_capacity_400kv_plus_mva',
        'max_voltage_kv',
        'capacity_added_last_5yr_mva',
        'mva_per_sq_km',
        # 2. Renewable Energy Headroom & Trajectory
        'total_re_mw',
        'total_re_potential_mw',
        'renewable_headroom_mw',
        'renewable_utilization_pct',
        're_capacity_growth_mw',
        'solar_power_mw',
        'wind_power_mw',
        # 3. Water Security & Hydrological Resilience
        'waterbody_count_total',
        'waterbody_density_per_1000_km2',
        'large_waterbodies_count',
        'gw_depth_mean_mbgl',
        'gw_depletion_trend_mbgl_per_yr',
        # 4. Land Economics & Space
        'land_cost_avg_rs_acre',
        'land_cost_log_avg',
        'area_km2',
        # 5. Ecosystem & Demand Presence
        'dc_count_state',
        'has_datacenter_presence'
    ]
    
    print(f"Selected {len(feature_cols)} core features spanning Power, RE, Water, Land, and Market.")
    return merged, feature_cols

def build_models():
    """
    Constructs all ML, DL, and Hybrid Ensemble pipelines.
    Implements strict featurization ordering (imputation and scaling inside pipeline).
    """
    # 1. Baseline: Ridge Regression
    pipe_ridge = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('ridge', Ridge(alpha=10.0, random_state=42))
    ])
    
    # 2. ML: Random Forest Regressor
    pipe_rf = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('rf', RandomForestRegressor(
            n_estimators=150,
            max_depth=5,
            min_samples_split=2,
            random_state=42
        ))
    ])
    
    # 3. ML: XGBoost Regressor
    pipe_xgb = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('xgb', xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.5,
            reg_lambda=1.0,
            random_state=42
        ))
    ])
    
    # 4. ML: LightGBM Regressor
    pipe_lgb = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('lgb', lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=3,
            min_child_samples=3,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.5,
            reg_lambda=1.0,
            random_state=42,
            verbose=-1
        ))
    ])
    
    # 5. Deep Learning: Deep Multi-Layer Perceptron (MLP) Neural Network
    # Wrapped with TransformedTargetRegressor for standardized gradient descent
    mlp_core = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('mlp', MLPRegressor(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu',
            solver='lbfgs',
            alpha=1.0,
            max_iter=1000,
            random_state=42
        ))
    ])
    model_dl = TransformedTargetRegressor(regressor=mlp_core, transformer=StandardScaler())
    
    # 6. Hybrid Super-Learner Ensemble (combines ML + DL)
    # Blends Random Forest (30%), XGBoost (30%), LightGBM (20%), and Deep MLP (20%)
    estimators = [
        ('rf', pipe_rf),
        ('xgb', pipe_xgb),
        ('lgb', pipe_lgb),
        ('dl_mlp', model_dl)
    ]
    model_hybrid = VotingRegressor(
        estimators=estimators,
        weights=[0.30, 0.30, 0.20, 0.20]
    )
    
    models = {
        "Ridge Baseline": pipe_ridge,
        "Random Forest (ML)": pipe_rf,
        "XGBoost (ML)": pipe_xgb,
        "LightGBM (ML)": pipe_lgb,
        "Deep Neural Net MLP (DL)": model_dl,
        "Hybrid Super-Learner (ML + DL)": model_hybrid
    }
    
    return models

def evaluate_models(models, X_train, y_train):
    print("\n" + "-" * 80)
    print("5-FOLD CROSS-VALIDATION MODEL BENCHMARKING (Strict Out-of-Fold Evaluation)")
    print("-" * 80)
    
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    benchmark_records = []
    oof_predictions = {}
    
    for name, model in models.items():
        preds = cross_val_predict(model, X_train, y_train, cv=cv)
        oof_predictions[name] = preds
        
        r2 = r2_score(y_train, preds)
        rmse = np.sqrt(mean_squared_error(y_train, preds))
        mae = mean_absolute_error(y_train, preds)
        p_corr, _ = pearsonr(y_train, preds)
        s_corr, _ = spearmanr(y_train, preds)
        
        benchmark_records.append({
            "model_name": name,
            "r2_score": round(r2, 4),
            "rmse": round(rmse, 3),
            "mae": round(mae, 3),
            "pearson_r": round(p_corr, 4),
            "spearman_rho": round(s_corr, 4)
        })
        
        print(f"[{name:30s}] R²: {r2:6.3f} | RMSE: {rmse:5.2f} | MAE: {mae:5.2f} | Pearson r: {p_corr:5.3f} | Spearman ρ: {s_corr:5.3f}")
        
    benchmarks_df = pd.DataFrame(benchmark_records)
    benchmarks_df.to_csv(OUT_BENCHMARKS, index=False)
    print(f"\nSaved benchmark metrics -> {OUT_BENCHMARKS}")
    return benchmarks_df, oof_predictions

def train_and_predict_all(models, X_train, y_train, X_all, full_df):
    print("\n" + "-" * 80)
    print("FULL DATASET INFERENCE & PREDICTION GENERATION")
    print("-" * 80)
    
    results_df = full_df[['state_id', 'state_name', 'region', 'is_enterprise_feasible', 'is_hyperscale_feasible', 'feasibility_status']].copy()
    
    # Ground benchmark TOPSIS score (scaled 0-100)
    results_df['ground_topsis_score'] = (full_df['topsis_balanced'] * 100.0).round(2)
    results_df['ground_topsis_rank'] = full_df['rank_balanced']
    results_df['is_pareto_optimal'] = full_df['is_pareto_optimal'].fillna(False)
    
    fitted_models = {}
    for name, model in models.items():
        # Fit on training data
        model.fit(X_train, y_train)
        fitted_models[name] = model
        
        # Predict on all 36 states
        preds = model.predict(X_all)
        # Clip to sensible 0-100 domain
        preds = np.clip(preds, 0.0, 100.0)
        
        col_prefix = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus").replace("-", "_")
        results_df[f'pred_{col_prefix}'] = np.round(preds, 2)
        results_df[f'rank_{col_prefix}'] = results_df[f'pred_{col_prefix}'].rank(ascending=False, method='min').astype(int)
    
    # Set the Hybrid Super-Learner as the definitive unified predicted score
    hybrid_col = 'pred_hybrid_super_learner_ml_plus_dl'
    results_df['final_predicted_suitability_score'] = results_df[hybrid_col]
    results_df['final_predicted_rank'] = results_df['final_predicted_suitability_score'].rank(ascending=False, method='min').astype(int)
    
    # Classify Siting Suitability Tiers
    def classify_tier(row):
        score = row['final_predicted_suitability_score']
        feasibility = str(row['feasibility_status'])
        
        if "Failed" in feasibility:
            return "Tier-4: Hard-Constrained / Infeasible"
        elif score >= 65.0:
            return "Tier-1: National Hyperscale Core"
        elif score >= 50.0:
            return "Tier-2: Regional Growth Core"
        elif score >= 35.0:
            return "Tier-3: Edge & Distributed Siting"
        else:
            return "Tier-4: Sub-Scale Siting"
            
    results_df['suitability_tier'] = results_df.apply(classify_tier, axis=1)
    
    # Sort by final predicted rank
    results_df = results_df.sort_values(by='final_predicted_rank', ascending=True).reset_index(drop=True)
    results_df.to_csv(OUT_PREDICTIONS, index=False)
    print(f"Saved complete 36-state predictions -> {OUT_PREDICTIONS}")
    
    return results_df, fitted_models

def compute_feature_importances(fitted_models, feature_cols):
    print("\n" + "-" * 80)
    print("FEATURE IMPORTANCE & DRIVER ANALYSIS")
    print("-" * 80)
    
    rf_model = fitted_models['Random Forest (ML)'].named_steps['rf']
    xgb_model = fitted_models['XGBoost (ML)'].named_steps['xgb']
    
    rf_imp = rf_model.feature_importances_
    xgb_imp = xgb_model.feature_importances_
    
    imp_df = pd.DataFrame({
        'feature': feature_cols,
        'rf_importance_pct': np.round(rf_imp * 100, 2),
        'xgb_importance_pct': np.round(xgb_imp * 100, 2)
    })
    imp_df['mean_importance_pct'] = np.round((imp_df['rf_importance_pct'] + imp_df['xgb_importance_pct']) / 2.0, 2)
    imp_df = imp_df.sort_values(by='mean_importance_pct', ascending=False).reset_index(drop=True)
    
    imp_df.to_csv(OUT_IMPORTANCES, index=False)
    print(f"Saved feature drivers -> {OUT_IMPORTANCES}\n")
    print(f"{'Rank':4s} | {'Feature Name':40s} | {'RF Imp %':10s} | {'XGB Imp %':10s} | {'Mean Imp %':10s}")
    print("-" * 80)
    for idx, row in imp_df.head(10).iterrows():
        print(f"{idx+1:4d} | {row['feature']:40s} | {row['rf_importance_pct']:10.2f} | {row['xgb_importance_pct']:10.2f} | {row['mean_importance_pct']:10.2f}")
        
    return imp_df

def print_summary_table(results_df):
    print("\n" + "=" * 100)
    print("TOP 15 PREDICTED DATA CENTER SITES IN INDIA (HYBRID ML/DL PREDICTION)")
    print("=" * 100)
    print(f"{'Rank':4s} | {'State':22s} | {'Region':8s} | {'Hybrid (ML+DL)':16s} | {'DL (MLP)':10s} | {'XGBoost':10s} | {'RF':8s} | {'TOPSIS':8s} | {'Suitability Tier':32s}")
    print("-" * 125)
    for idx, row in results_df.head(15).iterrows():
        h_score = row['final_predicted_suitability_score']
        dl_score = row['pred_deep_neural_net_mlp_dl']
        xgb_score = row['pred_xgboost_ml']
        rf_score = row['pred_random_forest_ml']
        t_score = f"{row['ground_topsis_score']:.1f}" if pd.notnull(row['ground_topsis_score']) else "N/A"
        
        print(f"{row['final_predicted_rank']:4d} | {row['state_name']:22s} | {row['region']:8s} | {h_score:16.2f} | {dl_score:10.2f} | {xgb_score:10.2f} | {rf_score:8.2f} | {t_score:8s} | {row['suitability_tier']:32s}")

def main():
    full_df, feature_cols = build_feature_matrix()
    
    # Filter training set: candidate states with evaluated Stage 2 multi-objective target
    train_mask = full_df['topsis_balanced'].notnull()
    X_train = full_df.loc[train_mask, feature_cols].copy()
    y_train = (full_df.loc[train_mask, 'topsis_balanced'] * 100.0).values
    
    X_all = full_df[feature_cols].copy()
    
    print(f"Training set: {len(X_train)} candidate states with ground-truth multi-objective evaluation.")
    print(f"Inference set: {len(X_all)} total states/UTs.")
    
    models = build_models()
    benchmarks_df, oof_predictions = evaluate_models(models, X_train, y_train)
    results_df, fitted_models = train_and_predict_all(models, X_train, y_train, X_all, full_df)
    compute_feature_importances(fitted_models, feature_cols)
    print_summary_table(results_df)
    
    print("\n" + "=" * 80)
    print("Unified ML/DL Prediction Pipeline Completed Successfully!")
    print("=" * 80)

if __name__ == '__main__':
    main()
