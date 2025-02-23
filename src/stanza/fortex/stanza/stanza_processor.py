# Copyright 2019 The Forte Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import List, Any, Dict, Set

import stanza
from ft.onto.base_ontology import Token, Sentence, Dependency

from forte.common import ProcessorConfigError
from forte.common.configuration import Config
from forte.common.resources import Resources
from forte.data.data_pack import DataPack
from forte.processors.base import PackProcessor

__all__ = [
    "StandfordNLPProcessor",
]


class StandfordNLPProcessor(PackProcessor):
    def __init__(self):
        super().__init__()
        self.nlp = None
        self.processors = set()

    def set_up(self):
        stanza.download(self.configs.lang, self.configs.dir)
        self.processors = set(self.configs.processors.split(","))

    # pylint: disable=unused-argument
    def initialize(self, resources: Resources, configs: Config):
        super().initialize(resources, configs)
        if (
            "pos" in configs.processors
            or "lemma" in configs.processors
            or "depparse" in configs.processors
        ):
            if "tokenize" not in configs.processors:
                raise ProcessorConfigError(
                    "tokenize is necessary in "
                    "configs.processors for "
                    "pos or lemma or depparse"
                )
        self.set_up()
        self.nlp = stanza.Pipeline(  # type: ignore
            lang=self.configs.lang,
            dir=self.configs.dir,
            use_gpu=self.configs.use_gpu,
            processors=self.configs.processors,
        )

    @classmethod
    def default_configs(cls) -> Dict[str, Any]:
        """
        This defines a basic config structure for StanfordNLP.
        """
        return {
            "processors": "tokenize,pos,lemma,depparse",
            "lang": "en",
            # Language code for the language to build the Pipeline
            "use_gpu": False,
            "dir": ".",
        }

    def _process(self, input_pack: DataPack):
        doc = input_pack.text

        if len(doc) == 0:
            logging.warning("Find empty text in doc.")

        # sentence parsing
        sentences = self.nlp(doc).sentences

        # Iterating through stanfordnlp sentence objects
        for sentence in sentences:
            Sentence(
                input_pack,
                sentence.tokens[0].start_char,
                sentence.tokens[-1].end_char,
            )

            tokens: List[Token] = []
            if "tokenize" in self.processors:
                # Iterating through stanfordnlp word objects
                for word in sentence.words:
                    misc = word.misc.split("|")

                    t_start = -1
                    t_end = -1
                    for m in misc:
                        k, v = m.split("=")
                        if k == "start_char":
                            t_start = int(v)
                        elif k == "end_char":
                            t_end = int(v)

                    if t_start < 0 or t_end < 0:
                        raise ValueError(
                            "Cannot determine word start or end for "
                            "stanfordnlp."
                        )

                    token = Token(input_pack, t_start, t_end)

                    if "pos" in self.processors:
                        token.pos = word.pos
                        token.ud_xpos = word.xpos

                    if "lemma" in self.processors:
                        token.lemma = word.lemma

                    tokens.append(token)

            # For each sentence, get the dependency relations among tokens
            if "depparse" in self.processors:
                # Iterating through token entries in current sentence
                for token, word in zip(tokens, sentence.words):
                    child = token  # current token
                    parent = tokens[word.head - 1]  # Head token
                    relation_entry = Dependency(input_pack, parent, child)
                    relation_entry.rel_type = word.deprel

    def record(self, record_meta: Dict[str, Set[str]]):
        r"""Method to add output type record of current processor
        to :attr:`forte.data.data_pack.Meta.record`.

        Args:
            record_meta: the field in the datapack for type record that need to
                fill in for consistency checking.
        """
        record_meta["ft.onto.base_ontology.Sentence"] = set()
        if "tokenize" in self.configs.processors:
            record_meta["ft.onto.base_ontology.Token"] = set()
            if "pos" in self.configs.processors:
                record_meta["ft.onto.base_ontology.Token"].add("pos")
            if "lemma" in self.processors:
                record_meta["ft.onto.base_ontology.Token"].add("lemma")
            if "depparse" in self.configs.processors:
                record_meta["ft.onto.base_ontology.Dependency"] = {"rel_type"}
