#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


def FlagIsOn(status,flag_n) :
  if status & (1 << (flag_n -1)) : return True
  else : return False

def isPrompt(gen) : return FlagIsOn(gen.statusFlags,1)
def isDecayedLeptonHadron(gen) : return FlagIsOn(gen.statusFlags,2)
def isTauDecayProduct(gen) : return FlagIsOn(gen.statusFlags,3)
def isPropmtTauDecayProduct(gen) : return FlagIsOn(gen.statusFlags,4)
def isHardProcess(gen) : return FlagIsOn(gen.statusFlags,8)
def fromHardProcess(gen) : return FlagIsOn(gen.statusFlags,9)
