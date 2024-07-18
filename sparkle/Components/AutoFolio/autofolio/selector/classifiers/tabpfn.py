import numpy as np
import pandas as pd

from ConfigSpace.hyperparameters import CategoricalHyperparameter, \
    UniformFloatHyperparameter, UniformIntegerHyperparameter
from ConfigSpace.conditions import EqualsCondition, InCondition
from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace import Configuration

from autofolio.aslib_scenario import ASlibScenario

from tabpfn import TabPFNClassifier
from ensemble_tabpfn import EnsembleTabPFN

__author__ = "Marius Lindauer"
__license__ = "BSD"


class TabPFN(object):

    @staticmethod
    def add_params(cs: ConfigurationSpace):
        '''
            adds parameters to ConfigurationSpace 
        '''
        try:
            classifier = cs.get_hyperparameter("classifier")
            if "TabPFN" not in classifier.choices:
                return

            ensemble = CategoricalHyperparameter(
                "pfn:use_ensemble", [ False], default_value=False)
            cs.add_hyperparameter(ensemble)

            cond = InCondition(
                child=ensemble, parent=classifier, values=["TabPFN"])
            cs.add_condition(cond)
        except:
            return

    def __init__(self):
        '''
            Constructor
        '''

        self.model = None

    def __str__(self):
        return "TabPFN"

    def fit(self, X, y, config: Configuration, weights=None):
        '''
            fit pca object to ASlib scenario data

            Arguments
            ---------
            X: numpy.array
                feature matrix
            y: numpy.array
                label vector
            weights: numpy.array
                vector with sample weights
            config: ConfigSpace.Configuration
                configuration

        '''
        
        if config['pfn:use_ensemble']:
            self.model = EnsembleTabPFN()
        else:
            self.model = TabPFNClassifier(subsample_features=True, batch_size_inference=1024)

        self.model.fit(X, y, weights)

    def predict(self, X):
        '''
            transform ASLib scenario data

            Arguments
            ---------
            X: numpy.array
                instance feature matrix

            Returns
            -------

        '''
        return self.model.predict(X)
    
    def get_attributes(self):
        '''
            returns a list of tuples of (attribute,value) 
            for all learned attributes
            
            Returns
            -------
            list of tuples of (attribute,value) 
        '''
        attr = []
        return attr
        