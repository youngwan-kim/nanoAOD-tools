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


class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile = True

    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self, histFile, histDirName)
	# define histograms
	oblist = ['pt','eta'] ; binning=0 ; minval=0 ; maxval=0 ; 
	histlist = [ROOT.TH1F('HT','HT',32,0,1600),ROOT.TH1F('XT','XT',80,0,4000)] #
	for i in range(0,2) :
	    for ob in oblist :
	        if ob == 'pt' : 
			binning = 160
			minval = 0
			maxval = 1600
		if ob == 'eta' :
			binning = 60
			minval = -3.0
			maxval = 3.0
	        histlist.append(ROOT.TH1F('Muon'+str(i)+'_'+ob,'Muon'+str(i)+'_'+ob,binning,minval,maxval))
	
	for i in range(0,2) :
	    for ob in oblist :
	        if ob == 'pt' and i == 0 : 
			binning = 50 
			minval = 0
			maxval = 500
		if ob == 'pt' and i == 1 :
			binning =  40
			minval = 0
			maxval = 200
		if ob == 'eta' :
			binning = 90
			minval = -4.5
			maxval = 4.5
		histlist.append(ROOT.TH1F('Jet'+str(i)+'_'+ob,'Jet'+str(i)+'_'+ob,binning,minval,maxval))

	for hist in histlist :
	    self.addObject(hist)

        self.addObject(ROOT.TH1F('M_jj','M_jj',60,0,6000)) # 
	self.addObject(ROOT.TH1F('DeltaEta_jj','DeltaEta_jj',80,-10,10)) # delta eta between  
	self.addObject(ROOT.TH1F('MET','MET',60,0,60)) # MET
	self.addObject(ROOT.TH1F('DeltaPhi_ll','DeltaPhi_ll',70,0,3.5)) # delta phi between same sign muon pair
	self.addObject(ROOT.TH1F('HToverLeadMuPt','HToverLeadMuPt',15,0,3)) # HT/(leading charged lepton pt)
	self.addObject(ROOT.TH1F('XToverLeadMuPt','XToverLeadMuPt',25,0,5)) # XT/(leading charged lepton pt)
	# debug histograms 
	self.addObject(ROOT.TH1F('Cutflow','Cutflow',6,0,6))

    def analyze(self, event):

	# rawobjects are pt-unsorted collections of objects
        rawGenParts = Collection(event,"GenPart")
	rawGenJets = Collection(event, "GenJet")
	GenMETv = Object(event, "GenMET")
	Generator = Object(event,"Generator")	
	w = Generator.weight

	rawGenElectrons = []
	rawGenMuons = []
	rawGenLeptons = []
	GenJets = [] 
	
	XT = 0
	HT = 0

	# Collection cuts
	# 1. pt(e,mu,tau,jet) > 10,27,20,25
	# 2. abseta(e,mu,tau,jet) < 2.5,2.7,2.5,4.5

	# define genlevel leptons ( status = 1 , |pdgId| = 13 or 11 )
	# used for HT,XT divided by leading charged lepton pt
        for rawGenPart in rawGenParts :
          if rawGenPart.status == 1 and fromHardProcess(rawGenPart) :
            if abs(rawGenPart.pdgId) == 13 or abs(rawGenPart.pdgId) ==11 : rawGenLeptons.append(rawGenPart)

	GenJets = [] 
	GenMuons = []
	GenElectrons = []
	GenLeptons = []

        for rawGenLepton in rawGenLeptons :
          if abs(rawGenLepton.pdgId) == 13 : rawGenMuons.append(rawGenLepton)
          if abs(rawGenLepton.pdgId) == 11 : rawGenElectrons.append(rawGenLepton)

	for rawGenMuon in rawGenMuons :
	  if abs(rawGenMuon.eta) < 2.7 and rawGenMuon.pt > 27 :
	    XT += rawGenMuon.pt
	    GenMuons.append(rawGenMuon) 
	    GenLeptons.append(rawGenMuon)       

	for rawGenElectron in rawGenElectrons :
	  if abs(rawGenElectron.eta) < 2.5 and rawGenElectron.pt > 10 :
	    XT += rawGenElectron.pt
	    GenElectrons.append(rawGenElectron)
	    GenLeptons.append(rawGenElectron)

	# lepton cleaning for genjets ( dR=0.4 )
	for rawGenJet in rawGenJets :
	  n = 0 
	  for Lepton in rawGenLeptons :
	    if deltaR(rawGenJet,Lepton) < 0.3 : n+=1
	  if n == 0 and abs(rawGenJet.eta) < 4.5 and rawGenJet.pt > 25 :    
	    XT += rawGenJet.pt
	    HT += rawGenJet.pt
	    GenJets.append(rawGenJet)


	GenLeptons.sort(key=lambda x : x.pt)
	GenMuons.sort(key=lambda x : x.pt)
        GenElectrons.sort(key=lambda x : x.pt)
	GenJets.sort(key=lambda x : x.pt)

	# Selection
	# 1. exactly two same sign mu candidates
	# 2. at least 2 jet candidates
	# 3. veto events with >0 el,taus

	self.Cutflow.Fill(1)
	if len(GenMuons) is not 2 : return False
	self.Cutflow.Fill(2)
	if GenMuons[0].pdgId*GenMuons[1].pdgId < 0 : return False
	self.Cutflow.Fill(3)
	if len(GenJets) < 2 :  return False
	self.Cutflow.Fill(4)
	if len(GenElectrons) > 0 : return False
	self.Cutflow.Fill(5)

	# Histogram Filling
	
	h_mupt = [self.Muon0_pt,self.Muon1_pt] 
	h_mueta = [self.Muon0_eta,self.Muon1_eta] 
	
	h_jetpt = [self.Jet0_pt,self.Jet1_pt] 
	h_jeteta = [self.Jet0_eta,self.Jet1_eta]

	for i in range(0,2) :
	    h_mupt[i].Fill(GenMuons[i].pt,w)
	    h_mueta[i].Fill(GenMuons[i].eta,w)

	for i in range(0,min(len(GenJets),2)) :
	    h_jetpt[i].Fill(GenJets[i].pt,w)
	    h_jeteta[i].Fill(GenJets[i].eta,w)

	self.MET.Fill(GenMETv.pt,w)
	self.XT.Fill(XT,w)
	self.HT.Fill(HT,w)

	self.DeltaPhi_ll.Fill(abs(deltaPhi(GenMuons[0],GenMuons[1])),w)			

	self.M_jj.Fill((GenJets[0].p4()+GenJets[1].p4()).M(),w)	  
	self.DeltaEta_jj.Fill(GenJets[0].eta-GenJets[1].eta,w)

	self.HToverLeadMuPt.Fill(HT/GenMuons[0].pt,w)
	self.XToverLeadMuPt.Fill(XT/GenMuons[0].pt,w)

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
