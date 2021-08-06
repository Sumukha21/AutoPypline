import os
from AutoPypline.Utils.utils import yaml_reader
from AutoPypline.auto_pipeline import AutoPipeline


if __name__ == "__main__":
    configs_folder = "C:/Users/Sumukha/Desktop/Projects/AutoPypline/test_configs/"
    config_file_name = "Encoder_Decoder.yml"
    config = yaml_reader(os.path.join(configs_folder, config_file_name))
    auto = AutoPipeline(config=config.get("control_flow"),
                        generator_inputs=config.get("generator_inputs"),
                        store_output_as=config.get("store_output_as", "List"))
    auto_output = auto()
    print(auto_output)


if __name__ == "__main2__":
    configs_folder = "C:/Users/Sumukha/Desktop/Projects/AutoPypline/test_configs/"
    config_file_name = "add_simple.yml"
    config = yaml_reader(os.path.join(configs_folder, config_file_name))
    auto = AutoPipeline(config=config.get("control_flow"),
                        generator_inputs=config.get("generator_inputs"),
                        store_output_as=config.get("store_output_as", "List"))
    a_input = [{"a": 10}, {"a": 30}, {"a": 40}]
    auto_output = list(map(auto, a_input))
    print(auto_output)
