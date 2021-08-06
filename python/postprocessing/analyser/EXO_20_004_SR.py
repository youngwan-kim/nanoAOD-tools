#!/usr/bin/env python
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
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
	for i in range(0,2) :
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
		histlist.append(ROOT.TH1F('photon'+str(i)+'_'+ob,'photon'+str(i)+'_'+ob,binning,minval,maxval))
	
	for i in range(0,2) :
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

	self.addObject(ROOT.TH1F('MET_pt','MET_pt',200,0,1000))
	self.addObject(ROOT.TH1F('MET_phi','MET_phi',60,-3.0,3.0))
	self.addObject(ROOT.TH1F('Njet','Njet',6,0,6))
	self.addObject(ROOT.TH1F('Nfatjet','Nfatjet',6,0,6))
	self.addObject(ROOT.TH1F('Nmu','Nmu',6,0,6))
	self.addObject(ROOT.TH1F('Nel','Nel',6,0,6))
	self.addObject(ROOT.TH1F('Npho','Npho',6,0,6))
	self.addObject(ROOT.TH1F('Cutflow','Cutflow',6,0,6))
 

    def analyze(self, event):

	self.Cutflow.Fill(0)
	
	# rawobjects are pt-unsorted collections of objects
        rawelectrons = Collection(event, "Electron") ; rawmuons = Collection(event, "Muon") ; 
	rawjets = Collection(event, "Jet") ; rawphotons = Collection(event, "Photon") ; rawfatjets = Collection(event, "FatJet") ;
	met = Object(event, "MET") 
	electrons = [] ; muons = []; jets = [] ; photons = [] ; deltaPhiMETJets = [] ; fatjets=[]
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
	 # if IsCustomMuonID("MonojetTight",rawmuon) is True :
	  muons.append(rawmuon)
	  muons.sort(key=lambda x : x.p4().Pt())

	for rawjet in rawjets :
	  HT += rawjet.p4()
	  jets.append(rawjet)
	  deltaPhiMETJets.append(deltaPhi(rawjet.p4().Pt(),met.__getattr__("pt")))
	  jets.sort(key=lambda x : x.p4().Pt())

#	for i in range(0,min(4,len(jets))) :
#	  deltaPhiMETJets.append(deltaPhi(jets[i].p4().Pt(),met.__getattr__("pt")))

	for rawphoton in rawphotons :
	  photons.append(rawphoton)
	  photons.sort(key=lambda x : x.p4().Pt())
	
	for rawfatjet in rawfatjets :   
	  fatjets.append(rawfatjet)
	  fatjets.sort(key=lambda x : x.p4().Pt()) 

	# Signal Region Baseline Event Selection
	# - one or more jets with MET > 250 GeV 
	# - min(deltaPhi(MET,{jets})>0.5 for QCD suppression
	# - Lepton and photon vetoing + b-tagged jets

	if len(jets) is 0 or met.__getattr__("pt") <= 250 : return False
	self.Cutflow.Fill(1)
	if min(deltaPhiMETJets) <= 0.5 : return False
	self.Cutflow.Fill(2)

	# Mono-V Selection For Exclusion
	# - V-Tagged AK-8 Jets with pT>250 GeV + |eta|<2.4
#	if len(fatjets) is not 0 and fatjets[0].__getattr__("deepTag_WvsQCD") > 0.42 and fatjets[0].__getattr__("pt") > 250 and abs(fatjets[0].__getattr__("eta")) < 2.4 : return False 	
#	self.Cutflow.Fill(3)

	# Monojet SR Selection
	# - among events that fail the Mono-V selection
	# - AK4Jets
	if jets[0].__getattr__("pt") < 100 or abs(jets[0].__getattr__("eta")) > 2.4 : return False
	self.Cutflow.Fill(3)

	# this seems so stupid but i don't have any better way to do this yet
	h_mupt = [self.muon0_pt,self.muon1_pt]#self.muon2_pt,self.muon3_pt]
	h_mueta = [self.muon0_eta,self.muon1_eta]#,self.muon2_eta,self.muon3_eta]
	h_muphi = [self.muon0_phi,self.muon1_phi]#,self.muon2_phi,self.muon3_phi]
	
	h_elpt = [self.electron0_pt,self.electron1_pt]#,self.electron2_pt,self.electron3_pt]
	h_eleta = [self.electron0_eta,self.electron1_eta]#,self.electron2_eta,self.electron3_eta]
	h_elphi = [self.electron0_phi,self.electron1_phi]#,self.electron2_phi,self.electron3_phi]

        h_phopt = [self.photon0_pt,self.photon1_pt]#,self.photon2_pt,self.photon3_pt]
        h_phoeta = [self.photon0_eta,self.photon1_eta]#,self.photon2_eta,self.photon3_eta]
        h_phophi = [self.photon0_phi,self.photon1_phi]#,self.photon2_phi,self.photon3_phi]

	h_jetpt = [self.jet0_pt,self.jet1_pt]#,self.jet2_pt,self.jet3_pt,self.jet4_pt,self.jet5_pt]
	h_jetphi = [self.jet0_phi,self.jet1_phi]#,self.jet2_phi,self.jet3_phi,self.jet4_phi,self.jet5_phi]
	h_jeteta = [self.jet0_eta,self.jet1_eta]#,self.jet2_eta,self.jet3_eta,self.jet4_eta,self.jet5_eta]y

	h_fatjetpt = [self.fatjet0_pt,self.fatjet1_pt]#,self.jet2_pt,self.jet3_pt,self.jet4_pt,self.jet5_pt]
	h_fatjetphi = [self.fatjet0_phi,self.fatjet1_phi]#,self.jet2_phi,self.jet3_phi,self.jet4_phi,self.jet5_phi]
	h_fatjeteta = [self.fatjet0_eta,self.fatjet1_eta]#,self.jet2_eta,self.jet3_eta,self.jet4_eta,self.jet5_eta]y

	for i in range(0,min(len(muons),2)) :
	    h_mupt[i].Fill(muons[i].p4().Pt())
	    h_mueta[i].Fill(muons[i].p4().Eta())
	    h_muphi[i].Fill(muons[i].p4().Phi())

	for i in range(0,min(len(electrons),2)) :
	    h_elpt[i].Fill(electrons[i].p4().Pt())
	    h_eleta[i].Fill(electrons[i].p4().Eta())
	    h_elphi[i].Fill(electrons[i].p4().Phi())

        for i in range(0,min(len(photons),2)) :
            h_phopt[i].Fill(photons[i].p4().Pt())
            h_phoeta[i].Fill(photons[i].p4().Eta())
            h_phophi[i].Fill(photons[i].p4().Phi())	

	for i in range(0,min(len(jets),2)) :
	    h_jetpt[i].Fill(jets[i].p4().Pt())
	    h_jeteta[i].Fill(jets[i].p4().Eta())
	    h_jetphi[i].Fill(jets[i].p4().Phi())

	self.MET_pt.Fill(met.__getattr__("pt"))
	self.MET_phi.Fill(met.__getattr__("phi"))

	for i in range(0,min(len(fatjets),2)) :
	    h_fatjetpt[i].Fill(fatjets[i].p4().Pt())
	    h_fatjeteta[i].Fill(fatjets[i].p4().Eta())
	    h_fatjetphi[i].Fill(fatjets[i].p4().Phi())

	self.Nmu.Fill(len(muons)); self.Nel.Fill(len(electrons))
	self.Njet.Fill(len(jets)); self.Npho.Fill(len(photons)) ; self.Nfatjet.Fill(len(fatjets))
	self.LT.Fill(LT.Pt()); self.HT.Fill(HT.Pt())
#	self.LHEpart_pdgid.Fill(LHEparts.GetPdgCode())

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
files = [] 

for filename in os.listdir(directory) :
	if filename.endswith(".root") :
		files.append(os.path.join(directory, filename))
		print(os.path.join(directory,filename))
	else : continue

p = PostProcessor(".", files, cut=preselection, branchsel=None, modules=[
                  ExampleAnalysis()], noOut=True, histFileName=outputname, histDirName="plots")
p.run()

