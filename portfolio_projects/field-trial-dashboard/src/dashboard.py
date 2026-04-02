"""
Streamlit Dashboard for Subtropical Breeding Trial Analytics
=============================================================
Interactive dashboard providing breeder-friendly insights:

Pages:
1. Overview — Dataset summary, QC status, completeness
2. Genotype Performance — Ranking, selection index, trait comparisons
3. Family Analysis — Cross/family performance summaries  
4. GxE & Stability — Genotype-by-environment interaction analysis
5. Selection Tool — Interactive multi-trait selection with customizable weights

Run with: streamlit run src/dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_loader import load_trial_data
from src.trial_analysis import (
    compute_overall_means, compute_selection_index,
    family_performance, stage_advancement_summary, gxe_stability
)

# Page config
st.set_page_config(
    page_title="Breeding Trial Analytics",
    page_icon="🌿",
    layout="wide"
)

TRAIT_COLS = [
    "fruit_weight_g", "brix_content", "skin_color_score", "flesh_firmness_kg",
    "disease_resistance", "tree_vigor", "yield_kg", "fruit_length_mm",
    "fruit_width_mm", "shelf_life_days", "shape_index"
]


@st.cache_data
def get_data():
    """Load and cache trial data."""
    return load_trial_data()


def main():
    st.title("🌿 Subtropical Breeding Trial Analytics")
    st.markdown("*Mango Breeding Program — Multi-Site, Multi-Year Trial Dashboard*")
    
    df = get_data()
    available_traits = [t for t in TRAIT_COLS if t in df.columns]
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_sites = st.sidebar.multiselect(
        "Sites", df["site"].unique().tolist(), default=df["site"].unique().tolist()
    )
    selected_seasons = st.sidebar.multiselect(
        "Seasons", sorted(df["season"].unique()), 
        default=sorted(df["season"].unique())
    )
    selected_stages = st.sidebar.multiselect(
        "Stages", df["stage"].unique().tolist(), 
        default=df["stage"].unique().tolist()
    )
    
    # Apply filters
    mask = (
        df["site"].isin(selected_sites) & 
        df["season"].isin(selected_seasons) &
        df["stage"].isin(selected_stages)
    )
    filtered = df[mask]
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Genotype Performance", "Family Analysis", 
         "GxE Stability", "Selection Tool"]
    )
    
    if page == "Overview":
        render_overview(filtered, available_traits)
    elif page == "Genotype Performance":
        render_genotype_performance(filtered, available_traits)
    elif page == "Family Analysis":
        render_family_analysis(filtered, available_traits)
    elif page == "GxE Stability":
        render_gxe_stability(filtered, available_traits)
    elif page == "Selection Tool":
        render_selection_tool(filtered, available_traits)


def render_overview(df, traits):
    """Overview page with dataset summary and completeness."""
    st.header("Dataset Overview")
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Genotypes", df["genotype_id"].nunique())
    col3.metric("Sites", df["site"].nunique())
    col4.metric("Seasons", df["season"].nunique())
    col5.metric("Families", df["family"].nunique())
    
    st.divider()
    
    # Records by site-season
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Records by Site & Season")
        pivot = df.pivot_table(index="site", columns="season", 
                               values="genotype_id", aggfunc="count", fill_value=0)
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues",
                       labels=dict(color="Records"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Genotypes by Stage")
        stage_counts = df.groupby("stage")["genotype_id"].nunique().reset_index()
        stage_counts.columns = ["Stage", "Genotypes"]
        fig = px.bar(stage_counts, x="Stage", y="Genotypes", color="Stage",
                    color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    
    # Missing data summary
    st.subheader("Missing Data by Trait")
    missing = df[traits].isna().mean().sort_values(ascending=False) * 100
    fig = px.bar(x=missing.index, y=missing.values,
                labels={"x": "Trait", "y": "Missing %"},
                color=missing.values,
                color_continuous_scale=["green", "yellow", "red"])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_genotype_performance(df, traits):
    """Genotype performance ranking and comparison."""
    st.header("Genotype Performance")
    
    # Overall means
    overall = compute_overall_means(df, traits)
    
    # Trait selector
    selected_trait = st.selectbox("Select Trait", traits)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Top 30 Genotypes — {selected_trait}")
        top30 = overall.nlargest(30, selected_trait)
        fig = px.bar(top30, x="genotype_id", y=selected_trait, color="stage",
                    color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(f"Distribution — {selected_trait}")
        fig = px.histogram(df, x=selected_trait, color="site", nbins=50,
                          barmode="overlay", opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)
    
    # Trait correlation heatmap
    st.subheader("Trait Correlations")
    available_numeric = [t for t in traits if t in df.columns]
    corr_matrix = df[available_numeric].corr()
    fig = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r",
                   zmin=-1, zmax=1)
    fig.update_layout(width=800, height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Site comparison scatter
    st.subheader("Site Comparison")
    sites = df["site"].unique().tolist()
    if len(sites) >= 2:
        col1, col2 = st.columns(2)
        site1 = col1.selectbox("Site 1", sites, index=0)
        site2 = col2.selectbox("Site 2", sites, index=min(1, len(sites)-1))
        
        means_site1 = df[df["site"] == site1].groupby("genotype_id")[selected_trait].mean()
        means_site2 = df[df["site"] == site2].groupby("genotype_id")[selected_trait].mean()
        common = means_site1.index.intersection(means_site2.index)
        
        if len(common) > 0:
            scatter_df = pd.DataFrame({
                site1: means_site1[common], site2: means_site2[common]
            })
            corr = scatter_df.corr().iloc[0, 1]
            fig = px.scatter(scatter_df, x=site1, y=site2, 
                           title=f"r = {corr:.3f}", opacity=0.5)
            fig.add_trace(go.Scatter(
                x=[scatter_df[site1].min(), scatter_df[site1].max()],
                y=[scatter_df[site1].min(), scatter_df[site1].max()],
                mode="lines", name="1:1 line", line=dict(dash="dash", color="red")
            ))
            st.plotly_chart(fig, use_container_width=True)


def render_family_analysis(df, traits):
    """Family/cross performance analysis."""
    st.header("Family Analysis")
    
    fam_perf = family_performance(df, traits)
    
    if fam_perf.empty:
        st.warning("No family data available.")
        return
    
    # Family overview
    st.subheader("Family Size & Performance")
    
    selected_trait = st.selectbox("Trait", traits, key="fam_trait")
    mean_col = f"{selected_trait}_mean"
    
    if mean_col in fam_perf.columns:
        fig = px.scatter(fam_perf, x="n_genotypes", y=mean_col,
                        text="family", size="n_genotypes",
                        labels={"n_genotypes": "Number of Genotypes",
                                mean_col: f"Mean {selected_trait}"})
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
    
    # Stage advancement
    st.subheader("Performance by Advancement Stage")
    stage_summary = stage_advancement_summary(df, traits)
    if not stage_summary.empty:
        fig = px.bar(stage_summary, x="stage", y=selected_trait,
                    color="stage", text="n_genotypes",
                    color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(texttemplate="n=%{text}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    
    # Family trait box plots
    st.subheader("Trait Distribution by Family")
    top_families = fam_perf.nlargest(10, "n_genotypes")["family"].tolist()
    fam_df = df[df["family"].isin(top_families)]
    
    fig = px.box(fam_df, x="family", y=selected_trait, color="family",
                color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_gxe_stability(df, traits):
    """GxE interaction and stability analysis."""
    st.header("Genotype × Environment Stability")
    
    selected_trait = st.selectbox("Trait for Stability", traits, key="gxe_trait")
    
    stability = gxe_stability(df, selected_trait)
    
    if stability.empty:
        st.warning("Not enough environments for stability analysis.")
        return
    
    st.markdown("""
    **Finlay-Wilkinson Regression:**
    - Slope ≈ 1.0: Average response to environment
    - Slope < 1.0: Adapted to poor environments (buffered)
    - Slope > 1.0: Adapted to good environments (responsive)
    - Low MSE = High stability
    """)
    
    # Stability scatter
    fig = px.scatter(
        stability, x="mean_performance", y="stability_mse",
        size="n_environments", color="fw_slope",
        hover_data=["genotype_id", "fw_r2"],
        labels={
            "mean_performance": f"Mean {selected_trait}",
            "stability_mse": "Stability (MSE, lower = more stable)",
            "fw_slope": "FW Slope"
        },
        color_continuous_scale="RdYlGn_r",
        title="Mean Performance vs Stability"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top stable + high performing
    st.subheader("Top Stable & High-Performing Genotypes")
    top_stable = stability.nsmallest(20, "stability_mse").nlargest(10, "mean_performance")
    st.dataframe(top_stable, use_container_width=True)


def render_selection_tool(df, traits):
    """Interactive multi-trait selection tool."""
    st.header("Multi-Trait Selection Tool")
    
    st.markdown("Adjust trait weights to customize your selection index. "
                "Positive weights favor higher values, negative weights favor lower values.")
    
    # Weight sliders
    weights = {}
    cols = st.columns(3)
    for i, trait in enumerate(traits):
        with cols[i % 3]:
            default = 1.0
            if "days" in trait or "maturity" in trait:
                default = -0.5
            weights[trait] = st.slider(
                trait.replace("_", " ").title(),
                min_value=-3.0, max_value=3.0, value=default, step=0.1,
                key=f"weight_{trait}"
            )
    
    # Number of selections
    n_select = st.slider("Number of selections", 5, 100, 20)
    
    # Compute selection index
    overall = compute_overall_means(df, traits)
    ranked = compute_selection_index(overall, weights)
    
    # Display selections
    st.subheader(f"Top {n_select} Selections")
    
    display_cols = ["genotype_id", "family", "stage", "selection_index",
                    "n_sites", "n_seasons"] + traits
    available_display = [c for c in display_cols if c in ranked.columns]
    
    top_selections = ranked.head(n_select)[available_display]
    st.dataframe(top_selections, use_container_width=True)
    
    # Selection index distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(ranked, x="selection_index", nbins=50,
                          title="Selection Index Distribution")
        threshold = ranked.iloc[n_select - 1]["selection_index"] if len(ranked) >= n_select else 0
        fig.add_vline(x=threshold, line_dash="dash", line_color="red",
                     annotation_text=f"Selection threshold")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Trait profile of selections vs population
        selected_ids = top_selections["genotype_id"].tolist()
        selected_means = df[df["genotype_id"].isin(selected_ids)][traits].mean()
        pop_means = df[traits].mean()
        
        comparison = pd.DataFrame({
            "Trait": traits,
            "Selected": selected_means.values,
            "Population": pop_means.values,
        })
        comparison["Gain (%)"] = ((comparison["Selected"] - comparison["Population"]) / 
                                    comparison["Population"] * 100).round(1)
        
        fig = px.bar(comparison, x="Trait", y="Gain (%)", 
                    color="Gain (%)",
                    color_continuous_scale=["red", "white", "green"],
                    title="Selection Gain vs Population Mean")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Download button
    csv = top_selections.to_csv(index=False)
    st.download_button(
        label="Download Selection List",
        data=csv,
        file_name="selected_genotypes.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    main()
