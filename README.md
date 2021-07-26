# AutoPypline
This library designs and executes data flow pipelines. It constructs an acyclic graph from the available code blocks 
based on the users configuration and automatically executes it.

## Where would this be useful?
Consider Data Science as an example, where experimenting with different models, data or even hyper parameters settings
is routine work. Some examples where the AutoPypline library can help you save time and manual effort:
   1) You can save the configuration file when you run the experiments so that you have an account of the experiment
      setting which was used. This will help you keep track of all the different experiments you have done which 
      could help you understand what works and what does not work!
   2) Since changing the models, data processing pipeline, training parameters such as callbacks, loss functions,
      metrics, optimizer, number of epochs is also a regular workflow in the life cycle of a data science project,
      the changes can be directly made in the configuration file without making changes to the code each time.
   3) This could also be used while designing inference and evaluation pipelines.
 
## How to use it?
You can design your configuration using yaml, json or any other file format which supports storing values 
as dictionaries. Each code block (python function or class) is defined in a particular format within 
the configuration. Each block definition can be divided into three components:
   1) Path to the python function or class ("function" or  "factory").
   2) Parameter values which are independent of other code blocks ("params").
   3) Parameter values which are dependent on the outputs of other code blocks ("inputs"). <br />
So each block is configured as a node in the acyclic graph. Once the graph is defined, the possible data flows 
(possibility of parallel flows is also checked) are identified automatically and executed.
Please check the folder "**test_configs**" containing few example configuration file which addresses all the features
supported by AutoPypline. The corresponding code used is also available in the folder "**test_scripts**".
Please note that for simplicity and to make sure anyone can understand the configurations contain data flows 
for trivial use cases, but the design rules followed within the examples are applicable to any pipeline.

## Designing your configuration file:
   Designing of the configuration file will be covered using very basic examples which showcase the different features
   supported by AutoPypline. For demonstration, yaml files will be used for defining configuration files.
   1) **Defining a single node/block**: <br>
      Reference configuration file: **test_configs/add_simple.yml <br>**
      For designing a single node, lets consider an example where we want to compute the sum of two integers.
      We already have a python function which takes in two integers as parameters ("a" and "b") and return the 
      sum. As mentioned previously, the definition of each block consists of three components:
      1) The path to the python function is defined under "function": <br />
         **function: test_scripts.arithmetic.adder** <br />
         The function adder is defined in the file arithmetic.py in the folder test_scripts
         As you can see, I have provided the path relative to my project directory here. 
         You can also provide the full path as an alternative.
      2) The parameters of the node which are independent of other nodes is defined under "params": <br />
         **params: <br />
              a: 20 <br />
              b: 10** <br />
        <br>
         The function parameters a and b are defined in "key: value" fashion and assigned integer values of 20 and 10
      There are no parameters which are dependent on other nodes, consequently "inputs" are not defined. <br>
      These components are defined under an identifier for the node. In this case an identifier "adder" is used. <br>
      In addition to the definition of nodes, an extra node "outputs" can be defined to indicate the name of the nodes
      whose output is required. In this example, I have specified that te output of the node having the identifier 
      "adder" is required. The outputs can be specified as a dictionary (key: value as in current example), a list of
       node names or a single node name or any combination of these.
       Additionally all the node definitions and the output specification should be defined under the key "control_flow".
       
       The AutoPypline object is instantiated as follows:
           &nbsp;&nbsp;&nbsp;&nbsp;AutoPipeline(config=config.get("control_flow"), <br>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;generator_inputs=config.get("generator_inputs"), <br>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;store_output_as=config.get("store_output_as", "List")) <br>
              
   2) **Designing a simple workflow having three nodes**: <br>
        Reference configuration file: **test_configs/three_nodes_simple.yml** <br>
        Consider a simple workflow with the objective to evaluate: ((c - (a + b)) + d + (a + b)), where a, b and c are
        integers. <br>
        Lets assume we have three functions to compute sum of two integers, difference between two integers
        and sum of three integers respectively (adder, subtract, adder_3). <br>
        The sum between "a" and "b" is first computed using the function "adder". Next the difference between "c" and 
        the result of the function "adder" is computed using the function "subtract". Finally we compute the sum between
        the integer "d" and the outputs of the functions "adder" and "subtract" using the function "adder_3". <br>
        In the configuration file the functions are defined with the identifiers "adder", "subtract" and "adder3". 
        Remember that any string can be used as an identifier. As discussed with the previous example, we define the 
        path and the parameters independent of other nodes. The parameters which are dependent on the outputs of 
        the other nodes are defined under "inputs" key within each node definition. <br>
        **Note**: Refer to the config **test_configs/multi_node_multi_output.yml** for a more complex objective.
        
        
           
             
             
        
          
        
          
