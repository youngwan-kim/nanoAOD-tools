#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.analyser.ID.GenStatus import *
from importlib import import_module
import os
import sys
import ROOT
import argparse
import linecache
ROOT.PyConfig.IgnoreCommandLineOptions = True

f = open("GenParts.txt",'w')

def FromHardProcess() :
  if n & (1 << (k - 1) ) : return True
  else : return False

class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile = True

    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self, histFile, histDirName)

    def analyze(self, event):

	# rawobjects are pt-unsorted collections of objects
        rawGenParts = Collection(event,"GenPart")

	rawGenElectrons = []
	rawGenMuons = []
	rawGenLeptons = []
	
        for rawGenPart in rawGenParts :
          if rawGenPart.status == 1 and fromHardProcess(rawGenPart) :
            if abs(rawGenPart.pdgId) == 13 or abs(rawGenPart.pdgId) ==11 : rawGenLeptons.append(rawGenPart)

#        print("--------")
#        print(" total genparticles : "+str(len(rawGenParts)))
#        print(" status 1 genleptons : "+str(len(rawGenLeptons)))

#	if len(rawGenLeptons) > 9 : 
        f.write("---------- \n") 
        f.write("(#) Mass, Eta, Phi, Pt, MotherIndex, pdgId, Status, statusFlag, isHardProcess \n")
        for index in range(0,len(rawGenParts)) :
	  f.write("("+str(index)+") "+str(rawGenParts[index].mass)+" , "+str(rawGenParts[index].eta)+" , "+str(rawGenParts[index].phi)+" , "+str(rawGenParts[index].pt)+" , "+str(rawGenParts[index].genPartIdxMother)+" , "+str(rawGenParts[index].pdgId)+" , "+str(rawGenParts[index].status)+" , "+str(rawGenParts[index].statusFlags)+" , "+str(isHardProcess(rawGenParts[index]))+"\n")
#	    if rawGenParts[index].status == 1 :
#              if abs(rawGenParts[index].pdgId) == 13 or abs(rawGenParts[index].pdgId) == 11 : f.write("!!!!!!!!!!!!!!!!!\n")

        
	GenMuons = []
        GenElectrons = []
	GenLeptons = []

#	for rawLHELepton in rawLHELeptons :
#	  if abs(rawLHELepton.pdgId) == 13 : rawLHEMuons.append(rawLHELepton)
#	  if abs(rawLHELepton.pdgId) == 11 : rawLHEElectrons.append(rawLHELepton)

        for rawGenLepton in rawGenLeptons :
          if abs(rawGenLepton.pdgId) == 13 : rawGenMuons.append(rawGenLepton)
          if abs(rawGenLepton.pdgId) == 11 : rawGenElectrons.append(rawGenLepton)

#	for rawLHEMuon in rawLHEMuons :
#	  if abs(rawLHEMuon.eta) < 2.7 and rawLHEMuon.pt > 27 :
#	    XT += rawLHEMuon.pt
#	    LHEMuons.append(rawLHEMuon) 
#	    LHELeptons.append(rawLHEMuon)       

#	for rawLHEElectron in rawLHEElectrons :
#	  if abs(rawLHEElectron.eta) < 2.5 and rawLHEElectron.pt > 10 :
#	    XT += rawLHEElectron.pt
#	    LHEElectrons.append(rawLHEElectron)
#	    LHELeptons.append(rawLHEElectron)

	for rawGenMuon in rawGenMuons :
	  if abs(rawGenMuon.eta) < 2.7 and rawGenMuon.pt > 27 :
	    GenMuons.append(rawGenMuon) 
	    GenLeptons.append(rawGenMuon)       

	for rawGenElectron in rawGenElectrons :
	  if abs(rawGenElectron.eta) < 2.5 and rawGenElectron.pt > 10 :
	    GenElectrons.append(rawGenElectron)
	    GenLeptons.append(rawGenElectron)

        print(" status 1 genleptons(with kine. cuts) : "+str(len(GenLeptons)))
        print(" gen muons : "+str(len(GenMuons)))
	print(" gen electrons : "+str(len(GenElectrons)))


	# lepton cleaning for genjets ( dR=0.4 )
#	for rawGenJet in rawGenJets :
#	  n = 0 
#	  for Lepton in LHELeptons :
#	    if deltaR(rawGenJet,Lepton) < 0.3 : n+=1
#	  if n == 0 and abs(rawGenJet.eta) < 4.5 and rawGenJet.pt > 25 :    
#	    XT += rawGenJet.pt
#	    HT += rawGenJet.pt
#	    GenJets.append(rawGenJet)


#	LHELeptons.sort(key=lambda x : x.pt)
#	LHEMuons.sort(key=lambda x : x.pt)
#        LHEElectrons.sort(key=lambda x : x.pt)
#	GenJets.sort(key=lambda x : x.pt)

	# Selection
	# 1. exactly two same sign mu candidates
	# 2. at least 2 jet candidates
	# 3. veto events with >0 el,taus

#	self.Cutflow.Fill(1)
#	if len(LHEMuons) is not 2 : return False
#	self.Cutflow.Fill(2)
#	if LHEMuons[0].pdgId*LHEMuons[1].pdgId < 0 : return False
#	self.Cutflow.Fill(3)
#	if len(GenJets) < 2 :  return False
#	self.Cutflow.Fill(4)
#	if len(LHEElectrons) > 0 : return False
#	self.Cutflow.Fill(5)

	# Histogram Filling
	
#	h_mupt = [self.Muon0_pt,self.Muon1_pt] 
#	h_mueta = [self.Muon0_eta,self.Muon1_eta] 
	
#	h_jetpt = [self.Jet0_pt,self.Jet1_pt] 
#	h_jeteta = [self.Jet0_eta,self.Jet1_eta]

#	for i in range(0,2) :
#	    h_mupt[i].Fill(LHEMuons[i].pt)
#	    h_mueta[i].Fill(LHEMuons[i].eta)

#	for i in range(0,min(len(GenJets),2)) :
#	    h_jetpt[i].Fill(GenJets[i].pt)
#	    h_jeteta[i].Fill(GenJets[i].eta)

#	self.MET.Fill(GenMETv.pt)
#	self.XT.Fill(XT)
#	self.HT.Fill(HT)

#	self.DeltaPhi_ll.Fill(abs(deltaPhi(LHEMuons[0],LHEMuons[1])))			

#	self.M_jj.Fill((GenJets[0].p4()+GenJets[1].p4()).M())	  
#	self.DeltaEta_jj.Fill(GenJets[0].eta-GenJets[1].eta)

#	self.HToverLeadMuPt.Fill(HT/LHEMuons[0].pt)
#	self.XToverLeadMuPt.Fill(XT/LHEMuons[0].pt)
	
        return True



parser = argparse.ArgumentParser(description='SSWW NanoGen')
parser.add_argument('-d', dest='directory',default="")
parser.add_argument('-f', dest='singlefile',default="")
parser.add_argument('-o', dest='output',default="histOut.root")
args = parser.parse_args()

directory = "" ; outputname = "" ; preselection = "" ; singlefile = ""

if args.directory == "" and args.singlefile == "" :
  print("Directory(-d) or file(-f) should be given")
  quit()

outputname = args.output
files=[]

if args.directory != "" and args.singlefile == "" :
  directory = args.directory
  for filename in os.listdir(directory) :
    if filename.endswith(".root") :
      files.append(os.path.join(directory, filename))
      print(os.path.join(directory,filename))
    else : continue

if args.directory == "" and args.singlefile != "" :
  singlefile = args.singlefile	
  files.append(singlefile)

p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  ExampleAnalysis()], noOut=True, histFileName=outputname, histDirName="plots")
p.run()
