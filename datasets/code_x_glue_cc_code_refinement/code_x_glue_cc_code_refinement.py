from typing import List

import datasets

from .common import TrainValidTestChild
from .generated_definitions import DEFINITIONS


_DESCRIPTION = """We use the dataset released by this paper(https://arxiv.org/pdf/1812.08693.pdf). The source side is a Java function with bugs and the target side is the refined one. All the function and variable names are normalized. Their dataset contains two subsets ( i.e.small and medium) based on the function length."""
_CITATION = """@article{10.1145/3340544,
author = {Tufano, Michele and Watson, Cody and Bavota, Gabriele and Penta, Massimiliano Di and White, Martin and Poshyvanyk, Denys},
title = {An Empirical Study on Learning Bug-Fixing Patches in the Wild via Neural Machine Translation},
year = {2019},
issue_date = {October 2019},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
volume = {28},
number = {4},
issn = {1049-331X},
url = {https://doi-org.proxy.wm.edu/10.1145/3340544},
doi = {10.1145/3340544},
abstract = {Millions of open source projects with numerous bug fixes are available in code repositories. This proliferation of software development histories can be leveraged to learn how to fix common programming bugs. To explore such a potential, we perform an empirical study to assess the feasibility of using Neural Machine Translation techniques for learning bug-fixing patches for real defects. First, we mine millions of bug-fixes from the change histories of projects hosted on GitHub in order to extract meaningful examples of such bug-fixes. Next, we abstract the buggy and corresponding fixed code, and use them to train an Encoder-Decoder model able to translate buggy code into its fixed version. In our empirical investigation, we found that such a model is able to fix thousands of unique buggy methods in the wild. Overall, this model is capable of predicting fixed patches generated by developers in 9--50% of the cases, depending on the number of candidate patches we allow it to generate. Also, the model is able to emulate a variety of different Abstract Syntax Tree operations and generate candidate patches in a split second.},
journal = {ACM Trans. Softw. Eng. Methodol.},
month = sep,
articleno = {19},
numpages = {29},
keywords = {bug-fixes, Neural machine translation}
}"""


class CodeXGlueCcCodeRefinementImpl(TrainValidTestChild):
    _DESCRIPTION = _DESCRIPTION
    _CITATION = _CITATION

    _FEATURES = {
        "id": datasets.Value("int32"),  # Index of the sample
        "buggy": datasets.Value("string"),  # The buggy version of the code
        "fixed": datasets.Value("string"),  # The correct version of the code
    }

    _SUPERVISED_KEYS = ["fixed"]

    def generate_urls(self, split_name):
        size = self.info["parameters"]["size"]
        for key in "buggy", "fixed":
            yield key, f"{size}/{split_name}.buggy-fixed.{key}"

    def _generate_examples(self, split_name, file_paths):
        """This function returns the examples in the raw (text) form."""
        # Open each file (one for java, and one for c#)
        files = {k: open(file_paths[k], encoding="utf-8") for k in file_paths}

        id_ = 0
        while True:
            # Read a single line from each file
            entries = {k: files[k].readline() for k in file_paths}

            empty = self.check_empty(entries)
            if empty:
                # We are done: end of files
                return

            entries["id"] = id_
            yield id_, entries
            id_ += 1


CLASS_MAPPING = {
    "CodeXGlueCcCodeRefinement": CodeXGlueCcCodeRefinementImpl,
}


class CodeXGlueCcCodeRefinement(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIG_CLASS = datasets.BuilderConfig
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(name=name, description=info["description"]) for name, info in DEFINITIONS.items()
    ]

    def _info(self):
        name = self.config.name
        info = DEFINITIONS[name]
        if info["class_name"] in CLASS_MAPPING:
            self.child = CLASS_MAPPING[info["class_name"]](info)
        else:
            raise RuntimeError(f"Unknown python class for dataset configuration {name}")
        ret = self.child._info()
        return ret

    def _split_generators(self, dl_manager: datasets.DownloadManager) -> List[datasets.SplitGenerator]:
        return self.child._split_generators(dl_manager=dl_manager)

    def _generate_examples(self, split_name, file_paths):
        return self.child._generate_examples(split_name, file_paths)
