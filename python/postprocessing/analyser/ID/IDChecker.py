#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


# TODO move these ID related codes to another file
# (low priority) try to use IDCriteriaDict = {} rather than ~List
# (high priority) in order to minimize useless loops, differ the logic from v1
# by splitting ID file (not to make useless in-line loops in CustomID.txt)
# Also, distinguish IDs via objects.

mu_dir = "/ID/muon/"
el_dir = "/ID/electron/"
jet_dir = "/ID/jet/"
pho_dir = "/ID/photon/"

def str2bool(string) :
  if string is "True" : return True
  if string is "False" : return False


def CustomIDCheck(linenum,ID,obj) :
  # main part checking if 'obj' satsifies "all" criteria of 'ID'
  # here linenum is from "IsCustomId"
  # read lines starting from desired custom ID
  IDCriteriaList = dict()
  for i in range(linenum+1,linenum+10):
    data = linecache.getline('CustomID.txt',i).strip() 
    if "name" not in data : IDCriteriaList.append(data.split())
    if "name" in data : pass

  # now check for object if it satisfies given criteria of CustomID
  # here the input is Collection objects 
  # TODO trkiso, check standard cone size for pfRelIso (.3 or .4)
  for criteria in IDCriteriaList :
    if "eta" in criteria[0] and abs(obj.p4().Eta()) > float(criteria[1]) :  return False
    if "pt" in criteria[0] and obj.p4().Pt() < float(criteria[1]) : return False  
    if "pog_tight" in criteria[0] and obj.__getattr__("tightId") is not str2bool(criteria[1]) : return False
    if "pog_medium" in criteria[0] and obj.__getattr__("mediumId") is not str2bool(criteria[1]) : return False 
    if "dxy" in criteria[0] and obj.__getattr__("dxy") < float(criteria[1]) :  return False
    if "dz" in criteria[0] and obj.__getattr__("dz") < float(criteria[1]) :  return False
    if "reliso" in criteria[0] and obj.__getattr__("pfRelIso03_all") > float(criteria[1]) : return False
    if "tightcharge" in criteria[0] and obj.__getattr__("tightCharge") is not int(criteria[1]) : return False
 #   print(ID+" OK")
    return True

def IsCustomMuonID(ID,obj) :
  filename = os.getcwd()+mu_dir+ID+".txt" ;  IDdict = dict()
  if os.path.exists(filename) :
    with open(filename) as MuonIDFile :
      for line in MuonIDFile:
	(key,val) = line.split()
	IDdict[key] = val

    if 'pt' in IDdict and obj.p4().Pt() <= float(IDdict['pt']) : return False  
    if 'eta' in IDdict and abs(obj.p4().Eta()) >= float(IDdict['eta']) :  return False 
    if 'pog_tight' in IDdict and obj.__getattr__("tightId") is not str2bool(IDdict['pog_tight']) : return False
    if 'pog_medium' in IDdict and obj.__getattr__("mediumId") is not str2bool(IDdict['pog_medium']) : return False 
    if 'dxy' in IDdict and obj.__getattr__("dxy") >= float(IDdict['dxy']) :  return False
    if 'dz' in IDdict and obj.__getattr__("dz") >= float(IDdict['dz']) :  return False
    if 'reliso03' in IDdict and obj.__getattr__("pfRelIso03_all") >= float(IDdict['reliso03']) : return False
    if 'reliso04' in IDdict and obj.__getattr__("pfRelIso04_all") >= float(IDdict['reliso04']) : return False
    if 'sip3d' in IDdict and obj.__getattr__("sip3d") <= float(IDdict['sip3d']) : return False
    return True

  else : 
   print(ID+".txt doesn't exist in "+mu_dir) ; exit()


def IsCustomElectronID(ID,obj) :
  filename = os.getcwd()+el_dir+ID+".txt"; IDdict = dict()
  if os.path.exists(filename) :
    with open(filename) as ElectronIDFile :
      for line in ElectronIDFile:
	(key,val) = line.split()
	IDdict[key] = val

    if abs(obj.p4().Eta()) <= float(IDdict['eta']) :  return False
    if 'pt' in IDdict and obj.p4().Pt() >= float(IDdict['pt']) : return False  
    if 'dxy' in IDdict and obj.__getattr__("dxy") >= float(IDdict['dxy']) :  return False
    if 'dz' in IDdict and obj.__getattr__("dz") >= float(IDdict['dz']) :  return False
    if 'reliso' in IDdict and  obj.__getattr__("pfRelIso03_all") > float(IDdict['reliso']) : return False
    if 'cutBased' in IDdict and obj.__getattr__("cutBased") is not int(IDdict['cutBased']) : return False
    if 'convVeto' in IDdict and obj.__getattr__("convVeto") is not str2bool(IDdict['convVeto']) : return False
    return True
  else :
   print(ID+".txt doesn't exist in "+mu_dir) 
   exit()


def IsCustomJetID(ID,obj) :
  filename = os.getcwd()+jet_dir+ID+".txt"; IDdict = dict()
  if os.path.exists(filename) :
    with open(filename) as CustomIDFile :
      for line in MuonIDFile:
	(key,val) = line.split()
	IDdict[key] = val

    if abs(obj.p4().Eta()) > float(IDdict['eta']) :  return False
    if obj.p4().Pt() < float(IDdict['pt']) : return False  
#    if obj.__getattr__("tightId") is not str2bool(IDdict['pog_tight']) : return False
#    if obj.__getattr__("mediumId") is not str2bool(IDdict['pog_medium']) : return False 
    if obj.__getattr__("dxy") < float(IDdict['dxy']) :  return False
    if obj.__getattr__("dz") < float(IDdict['dz']) :  return False
#    if obj.__getattr__("pfRelIso03_all") > float(IDdict['reliso']) : return False
    return True
  else :
    print(ID+".txt doesn't exist in "+mu_dir)    
    exit()

def IsCustomPhotonID(ID,obj) :
  filename = os.getcwd()+pho_dir+ID+".txt"; IDdict = dict()
  if os.path.exists(filename) :
    with open(filename) as ElectronIDFile :
      for line in ElectronIDFile:
	(key,val) = line.split()
	IDdict[key] = val

    if abs(obj.p4().Eta()) <= float(IDdict['eta']) :  return False
    if 'pt' in IDdict and obj.p4().Pt() >= float(IDdict['pt']) : return False  
    if 'dxy' in IDdict and obj.__getattr__("dxy") >= float(IDdict['dxy']) :  return False
    if 'dz' in IDdict and obj.__getattr__("dz") >= float(IDdict['dz']) :  return False
    if 'reliso' in IDdict and  obj.__getattr__("pfRelIso03_all") > float(IDdict['reliso']) : return False
#    if obj.__getattr__("tightCharge") is not int(IDdict['tightcharge']) : return False
    if 'convVeto' in IDdict and obj.__getattr__("convVeto") is not str2bool(IDdict['convVeto']) : return False
    return True
  else :
   print(ID+".txt doesn't exist in "+mu_dir) 
   exit()


