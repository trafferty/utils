import importlib
module_name = "BasicResults_PostProcessor"

imp = importlib.import_module(module_name)
mod = getattr(imp, "BasicResults_PostProcessor")

config = {}
last_loop_vars={}
last_loop_vars["ExpFolder"] = "/home/dif/results"

post_processor = mod(config, last_loop_vars)

postProcessStep_dict = {
        "type": "result_proc",
        "vel_desired_range": [4.0, 5.0],
        "vol_desired_range": [0.8, 1.0]
      }

post_processor.process(postProcessStep_dict)




   "PostProcess": [
      {
        "name": "ImageStats_PostProcessor",

        "bar": 42
      },
      
      {
        "name": "BasicResults_PostProcessor",

        "vel_desired_range": [4.0, 5.0],
        "vol_desired_range": [0.8, 1.0]
      }
   ]



pp = p()
imp = importlib.import_module('basic_results_post_processor')
p = getattr(imp, "BasicResults_PostProcessor")
config = {}
pp = p()
pp = p(config, last_loop_vars)
pp = p(config)
history
