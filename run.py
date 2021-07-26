import os
from AutoPypline.Utils.utils import yaml_reader
from AutoPypline.auto_pipeline import AutoPipeline


if __name__ == "__main__":
    configs_folder = "C:/Users/Sumukha/Desktop/Projects/AutoPypline/test_configs/"
    config_file_name = "multi_node_multi_output.yml"
    config = yaml_reader(os.path.join(configs_folder, config_file_name))
    auto = AutoPipeline(config=config.get("control_flow"),
                        generator_inputs=config.get("generator_inputs"),
                        store_output_as=config.get("store_output_as", "List"))
    auto_output = auto()
    print(auto_output)
