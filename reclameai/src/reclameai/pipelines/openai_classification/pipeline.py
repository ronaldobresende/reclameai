"""
This is a boilerplate pipeline 'openai_classification'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import (
    load_data,
    clean_data,
    group_reports,
    classify_complaints,
    save_results,
    plot_histogram,
    consolidate_reports,
)

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=load_data,
                inputs="nps_mock_data",
                outputs="nps_data",
                name="load_data_node",
            ),
            node(
                func=clean_data,
                inputs="nps_data",
                outputs="cleaned_data",
                name="clean_data_node",
            ),
            node(
                func=group_reports,
                inputs="cleaned_data",
                outputs="grouped_reports",
                name="group_reports_node",
            ),
            node(
                func=classify_complaints,
                inputs=["grouped_reports", "params:categorias"],
                outputs="classificated_data",
                name="classify_complaints_node",
            ),
            node(
                func=save_results,
                inputs="classificated_data",
                outputs="classified_nps_data",
                name="save_results_node",
            ),
            node(
                func=plot_histogram,
                inputs="classified_nps_data",
                outputs="histogram_output",  
                name="plot_histogram_node",
            ),   
            node(
                func=consolidate_reports,
                inputs=dict(
                    output_dir="params:openai.output_dir",
                    consolidated_filename="params:openai.consolidated_filename",
                    classificated_data="classificated_data",  # Adiciona classificated_data como entrada, para criar dependência do nó e ser executado por último
                ),
                outputs=None,
                name="consolidate_reports_node",
            ),                        
        ]
    )
