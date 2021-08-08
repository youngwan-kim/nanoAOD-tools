#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.analyser.ID.IDChecker import *
from importlib import import_module
import os
import sys
import ROOT
import argparse
import linecache
ROOT.PyConfig.IgnoreCommandLineOptions = True


class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile = True

    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self, histFile, histDirName)
	# define histograms
	oblist = ['pt','eta','phi'] ; binning=0 ; minval=0 ; maxval=0 ; 
	histlist = [ROOT.TH1F('HT','HT',100,0,1000),ROOT.TH1F('LT','LT',100,0,1000)]
	for i in range(0,4) :
	    for ob in oblist :
	        if ob == 'pt' : 
			binning = 200
			minval = 0
			maxval = 1000
		if ob == 'phi' or ob == 'eta' :
			binning = 60
			minval = -3.0
		maxval = 3.0
		histlist.append(ROOT.TH1F('electron'+str(i)+'_'+ob,'electron'+str(i)+'_'+ob,binning,minval,maxval))
	        histlist.append(ROOT.TH1F('muon'+str(i)+'_'+ob,'muon'+str(i)+'_'+ob,binning,minval,maxval))
	
	for i in range(0,6) :
	    for ob in oblist :
	        if ob == 'pt' : 
			binning = 200 
			minval = 0
			maxval = 1000
		if ob == 'phi' or ob == 'eta' :
			binning = 60
			minval = -3.0
			maxval = 3.0
		histlist.append(ROOT.TH1F('jet'+str(i)+'_'+ob,'jet'+str(i)+'_'+ob,binning,minval,maxval))
		histlist.append(ROOT.TH1F('fatjet'+str(i)+'_'+ob,'fatjet'+str(i)+'_'+ob,binning,minval,maxval))

	for hist in histlist :
	    self.addObject(hist)

	self.addObject(ROOT.TH1F('Njet','Njet',20,0,20))
	self.addObject(ROOT.TH1F('Nmu','Nmu',6,0,6))
	self.addObject(ROOT.TH1F('Nel','Nel',6,0,6))
#	self.addObject(ROOT.TH1F('LHEpart_pdgid','LHEpart_pdgid',50,-25,25))
#	self.addObject(ROOT.TH1F('LHEpart_pt','LHEpart_pt',200,0,1000))
 

    def analyze(self, event):

	# rawobjects are pt-unsorted collections of objects
        rawelectrons = Collection(event, "Electron") ; rawmuons = Collection(event, "Muon") ; rawjets = Collection(event, "Jet")
	electrons = [] ; muons = []; jets = [] 
	LT = ROOT.TLorentzVector(); HT = ROOT.TLorentzVector()

	# pt sorting lorentz vectors from collections
	for rawelectron in rawelectrons :
	  LT += rawelectron.p4()
#	  if IsCustomElectronID("HNElectronTight",rawelectron) is True :
          electrons.append(rawelectron)
          electrons.sort(key=lambda x : x.p4().Pt())

	for rawmuon in rawmuons :
	  LT += rawmuon.p4()
	  # Custom IDs can be used so
#	  if IsCustomMuonID("HNMuonTight",rawmuon) is True :
	  muons.append(rawmuon)
	  muons.sort(key=lambda x : x.p4().Pt())

	for rawjet in rawjets :
	  HT += rawjet.p4()
	  jets.append(rawjet)
	  jets.sort(key=lambda x : x.p4().Pt())

	h_mupt = []
	for i in range(0,min(len(muons),4)) :
	  h_mupt.append(self.__getattr__("muon"+i+"_pt"))

	# this seems so stupid but i don't have any better way to do this yet
#	h_mupt = [self.muon0_pt,self.muon1_pt,self.muon2_pt,self.muon3_pt]
	h_mueta = [self.muon0_eta,self.muon1_eta,self.muon2_eta,self.muon3_eta]
	h_muphi = [self.muon0_phi,self.muon1_phi,self.muon2_phi,self.muon3_phi]
	
	h_elpt = [self.electron0_pt,self.electron1_pt,self.electron2_pt,self.electron3_pt]
	h_eleta = [self.electron0_eta,self.electron1_eta,self.electron2_eta,self.electron3_eta]
	h_elphi = [self.electron0_phi,self.electron1_phi,self.electron2_phi,self.electron3_phi]

	h_jetpt = [self.jet0_pt,self.jet1_pt,self.jet2_pt,self.jet3_pt,self.jet4_pt,self.jet5_pt]
	h_jetphi = [self.jet0_phi,self.jet1_phi,self.jet2_phi,self.jet3_phi,self.jet4_phi,self.jet5_phi]
	h_jeteta = [self.jet0_eta,self.jet1_eta,self.jet2_eta,self.jet3_eta,self.jet4_eta,self.jet5_eta]


	for i in range(0,min(len(muons),4)) :
	    h_mupt[i].Fill(muons[i].p4().Pt())
	    h_mueta[i].Fill(muons[i].p4().Eta())
	    h_muphi[i].Fill(muons[i].p4().Phi())

	for i in range(0,min(len(electrons),4)) :
	    h_elpt[i].Fill(electrons[i].p4().Pt())
	    h_eleta[i].Fill(electrons[i].p4().Eta())
	    h_elphi[i].Fill(electrons[i].p4().Phi())

	for i in range(0,min(len(jets),6)) :
	    h_jetpt[i].Fill(jets[i].p4().Pt())
	    h_jeteta[i].Fill(jets[i].p4().Eta())
	    h_jetphi[i].Fill(jets[i].p4().Phi())

#	for i in range(0,min(len(fatjets),6)) :
#	    h_fatjetpt[i].Fill(fatjets[i].Pt())
#	    h_fatjeteta[i].Fill(fatjets[i].Eta())
#	    h_fatjetphi[i].Fill(fatjets[i].Phi())

	self.Nmu.Fill(len(muons)); self.Nel.Fill(len(electrons))
	self.Njet.Fill(len(jets)); #self.Nfatjet.Fill(len(fatjets))
	self.LT.Fill(LT.Pt()); self.HT.Fill(HT.Pt())
#	self.LHEpart_pdgid.Fill(LHEparts.GetPdgCode())

	###### USER DEFINED CUTS
	# ex) m(ll) : Z cand mass cuts
	# 	self.addObject(ROOT.TH1F('m_ll','m_ll',~)) in beginjob
	# 	if len(muons) == 2 :
	#	  for i in range(0,2) :
	#	    candmass = 0 ; candmass+=muons[i].M()
	#	    self.m_ll.Fill(candmass)
	######

        return True

parser = argparse.ArgumentParser(description='FastSim NanoAOD validation tool (wip)')
parser.add_argument('-d', dest='directory',default="")
parser.add_argument('-o', dest='output',default="histOut.root")
args = parser.parse_args()

directory = "" ; outputname = "" ; preselection = ""

if args.directory == "" :
	print("Directory should be given")
	quit()

if args.directory != "" :
	directory = args.directory

outputname = args.output 
 
#directory = "/T2_KR_KISTI/store/mc/RunIISummer20UL16NanoAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v15-v1/280000/"
#directory = "/T2_KR_KISTI/store/data/Run2018D/DoubleMuonLowMass/NANOAOD/UL2018_MiniAODv1_NanoAODv2-v2/00000/"
#directory="/T2_KR_KISTI/store/data/Run2016G/DoubleMuon/NANOAOD/UL2016_MiniAODv1_NanoAODv2-v1/270000/"
#directory="/T2_KR_KISTI/store/user/youngwan/gluinoGMSB_M2200_ctau30000p0_TuneCP5_pythia8/RunIISummer20UL18_NanoAODv2/210309_054146/0000/"

files = [] 

for filename in os.listdir(directory) :
	if filename.endswith(".root") :
		files.append(os.path.join(directory, filename))
		print(os.path.join(directory,filename))
	else : continue

p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  ExampleAnalysis()], noOut=True, histFileName=outputname, histDirName="plots")
p.run()

