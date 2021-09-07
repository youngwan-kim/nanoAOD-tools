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


class MonojetSR(Module):
    def __init__(self):
        self.writeHistFile = True

    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self, histFile, histDirName)
	# define histograms
	oblist = ['pt','eta','phi'] ; binning=0 ; minval=0 ; maxval=0 ; 
	histlist = [ROOT.TH1F('HadronicRecoil_pt','HadronicRecoil_pt',100,0,1000), ROOT.TH1F('HadronicRecoil_phi','HadronicRecoil_phi',60,-3.0,3.0)]
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
	
	self.addObject(ROOT.TH1F('deltaphi','deltaphi',80,-4.0,4.0))
	self.addObject(ROOT.TH1F('MET_pt','MET_pt',200,0,1000))
	self.addObject(ROOT.TH1F('MET_phi','MET_phi',60,-3.0,3.0))
	self.addObject(ROOT.TH1F('Njet','Njet',6,0,6))
	self.addObject(ROOT.TH1F('Nfatjet','Nfatjet',6,0,6))
	self.addObject(ROOT.TH1F('Nvtagfatjet','Nvtagfatjet',6,0,6))
	self.addObject(ROOT.TH1F('Nmu','Nmu',6,0,6))
	self.addObject(ROOT.TH1F('Nel','Nel',6,0,6))
	self.addObject(ROOT.TH1F('Npho','Npho',6,0,6))
	self.addObject(ROOT.TH1F('Cutflow','Cutflow',6,0,6))
 	self.addObject(ROOT.TH1F('TotalEvents','TotalEvents',2,0,2))

    def analyze(self, event):

	self.Cutflow.Fill(0)
	
	# rawobjects are pt-unsorted collections of objects
        rawelectrons = Collection(event, "Electron") 
	rawmuons = Collection(event, "Muon")  
	rawjets = Collection(event, "Jet")  
	rawphotons = Collection(event, "Photon") 
	rawfatjets = Collection(event, "FatJet") 
	rawtaus = Collection(event, "Tau")

	# METs for cuts
	met = Object(event, "MET") 
	calomet = Object(event, "CaloMET") 
	pfmet = Object(event, "ChsMET")
	trackmet = Object(event, "TkMET")

	electrons = []  ; loose_electrons = [] 
	muons = [] ; loose_muons = []
	photons = [] ; loose_photons = [] ; 

	fatjets=[] ; jets = []
	vtagfatjets = []
	taus = []
	
	HadronicRecoil = ROOT.TLorentzVector() ; deltaPhiRecoilJets = []

	# OBJECT DEFINITION
	# - HadronicRecoil = MET + pT_(leptons+photons)

	HadronicRecoil += met.met_p4()

	# Electron

	for rawelectron in rawelectrons :
	  HadronicRecoil += rawelectron.p4()
          electrons.append(rawelectron)
	  if rawelectron.cutBased is 1 and rawelectron.pt > 10 and abs(rawelectron.eta) < 2.5 :
	    loose_electrons.append(rawelectron)

	# Tau

	for rawtau in taus : 
	  if rawtau.pt > 18 and abs(rawtau.eta) < 2.3 and rawtau.idMVAoldDM2017v2 is 2 :
            taus.append(rawtau)

	# Muon

	for rawmuon in rawmuons :
	  HadronicRecoil += rawmuon.p4()
	  muons.append(rawmuon)
	  if rawmuon.looseId and rawmuon.pt > 10 and abs(rawmuon.eta) < 2.4 : 
	    loose_muons.append(rawmuon)

	# Jet
	# - pT > 30 && |eta| < 2.5 (done)
	# - Jet-lepton overlap removal for deltaR < 0.4 (TODO)

	for rawjet in rawjets :
	  if rawjet.pt > 30 and abs(rawjet.eta) < 2.5 :
	    if rawjet.jetId is 6 : 
	      jets.append(rawjet) 
	
	# Photon

	for rawphoton in rawphotons :
	  HadronicRecoil += rawphoton.p4()
	  photons.append(rawphoton)
	  if rawphoton.cutBased is 1 and rawphoton.pt > 15 and abs(rawphoton.eta) < 2.5 :
	    loose_photons.append(rawphoton)	

	# V-Tagged AK8 Jets
	# - nominal tagger (WvsQCD, no MD) > 0.458

	for rawfatjet in rawfatjets :   
	  fatjets.append(rawfatjet)

	for fatjet in fatjets : 
	  if fatjet.deepTag_WvsQCD > 0.458 :
	    vtagfatjets.append(fatjet)
	
	electrons.sort(key=lambda x : x.p4().Pt()) ; muons.sort(key=lambda x : x.p4().Pt()) ; jets.sort(key=lambda x : x.p4().Pt()) 
        fatjets.sort(key=lambda x : x.p4().Pt()) ; vtagfatjets.sort(key=lambda x : x.p4().Pt()) ; taus.sort(key=lambda x : x.p4().Pt())

	if len(jets) is not 0 :
	  for i in range(0,min(4,len(jets))) :
	    deltaPhiRecoilJets.append(abs(deltaPhi(jets[i].phi,HadronicRecoil.Phi())))

	# EVENT SELECTION

	# 1. Signal Region Baseline Event Selection
	# - one or more jets with HadronicRecoil > 250 GeV 
	# - min(deltaPhi(recoil,{jets})>0.5 for QCD suppression
	# - Lepton and photon vetoing + b-tagged jets (TODO)

	if len(jets) is 0 or HadronicRecoil.Pt() <= 250 : return False
	self.Cutflow.Fill(1)
	if min(deltaPhiRecoilJets) <= 0.5 : return False
	self.Cutflow.Fill(2)

	# 2. Mono-V Selection For Exclusion
	# - V-Tagged AK-8 Jets with pT>250 GeV + |eta|<2.4
	# - nominal tagger cut : WvsQCD > 0.458
	# - pruned mass in [65,120]

	if len(vtagfatjets) is not 0 and vtagfatjets[0].pt > 250 and abs(vtagfatjets[0].eta) < 2.4 :
	  if vtagfatjets[0].msoftdrop > 65 and vtagfatjets[0].msoftdrop < 120 :
	    return False
	self.Cutflow.Fill(3)

	# 3. Monojet SR Selection
	# - among events that fail the Mono-V selection
	# - Leading AK4 jet : chHEF > 0.1 && neHEF < 0.8

	if jets[0].pt < 100 or abs(jets[0].eta) > 2.4 : return False
	if jets[0].neHEF >= 0.8 or jets[0].chHEF <= 0.1 : return False
	self.Cutflow.Fill(4) 
        self.TotalEvents.Fill(0)

	# 4. Background suppression 
	# - W+jets : veto events containing one or more loose leptons with pT > 10 GeV or hadronically decaying tau with pT >18 GeV
	# - EW : veto events containing one or more loose isolated photons with pT > 15 GeV and abseta < 2.5
	# - Top : veto events with b-jet && pT > 20 && abseta < 2.4
	# - MET : deltaPt , deltaPhi

#	if len(loose_muons) is not 0 or len(loose_electrons) is not 0 : return False
#	if len(taus) is not 0 and taus[0].pt > 18 : return False 
#	self.Cutflow.Fill(5)	

#	if len(loose_photons) is not 0 : return False
#	self.Cutflow.Fill(6)

#	if (pfmet.pt - calomet.pt)/HadronicRecoil.Pt() >= 0.5 : return False
#	if deltaPhi(trackmet,pfmet) >= 2 : return False
#	self.Cutflow.Fill(7)

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

	h_fatjetpt = [self.fatjet0_pt,self.fatjet1_pt]
	h_fatjetphi = [self.fatjet0_phi,self.fatjet1_phi]
	h_fatjeteta = [self.fatjet0_eta,self.fatjet1_eta]

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

	self.MET_pt.Fill(met.pt)
	self.MET_phi.Fill(met.phi)

	for i in range(0,min(len(fatjets),2)) :
	    h_fatjetpt[i].Fill(fatjets[i].p4().Pt())
	    h_fatjeteta[i].Fill(fatjets[i].p4().Eta())
	    h_fatjetphi[i].Fill(fatjets[i].p4().Phi())

#	self.deltaphi.Fill(min(deltaPhiMETJets)) 
	self.Nmu.Fill(len(muons)); self.Nel.Fill(len(electrons)) 
	self.Nvtagfatjet.Fill(len(vtagfatjets))
	self.Njet.Fill(len(jets))
	self.Npho.Fill(len(photons))
	self.Nfatjet.Fill(len(fatjets))
	self.HadronicRecoil_pt.Fill(HadronicRecoil.Pt())
	self.HadronicRecoil_phi.Fill(HadronicRecoil.Phi())

        return True

parser = argparse.ArgumentParser(description='FastSim EXO-20-004 Monojet Analysis Validation Tool (SR)')
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
                  MonojetSR()], noOut=True, histFileName=outputname, histDirName="plots")
p.run()

